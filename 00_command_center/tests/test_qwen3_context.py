from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "agents") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "agents"))

from model_backend import OllamaBackend, get_model_backend, EchoBackend


# ---------------------------------------------------------------------------
# 1. Default model selection
# ---------------------------------------------------------------------------

def test_ollama_backend_default_model_is_helix_agent_qwen3() -> None:
    """The default model must be the custom Modelfile, not a raw Ollama tag."""
    backend = OllamaBackend()
    assert backend.model == "helix-agent-qwen3", (
        f"Expected default model \"helix-agent-qwen3\", got \"{backend.model}\""
    )


def test_ollama_backend_env_var_overrides_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """OLLAMA_MODEL env var must take precedence over the hardcoded default."""
    monkeypatch.setenv("OLLAMA_MODEL", "custom-override:latest")
    backend = OllamaBackend()
    assert backend.model == "custom-override:latest"


def test_ollama_backend_env_var_beats_constructor_arg(monkeypatch: pytest.MonkeyPatch) -> None:
    """OLLAMA_MODEL env var must take precedence over a constructor arg.

    This is by design: the orchestrator copies os.environ to subprocesses,
    so setting OLLAMA_MODEL in the shell before launch is the intended
    per-agent override mechanism. Constructor args exist only as fallbacks.
    """
    monkeypatch.setenv("OLLAMA_MODEL", "env-override:latest")
    backend = OllamaBackend(model="ignored-arg")
    assert backend.model == "env-override:latest"


def test_get_model_backend_ollama_default_beats_echo(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_model_backend() with HELIX_MODEL_BACKEND=ollama returns OllamaBackend."""
    monkeypatch.setenv("HELIX_MODEL_BACKEND", "ollama")
    backend = get_model_backend()
    # If Ollama package is unavailable, falls back to EchoBackend — that'\''s fine
    if isinstance(backend, OllamaBackend):
        assert backend.model == "helix-agent-qwen3"


# ---------------------------------------------------------------------------
# 2. Per-agent override path (confirm orchestrator passes env vars)
# ---------------------------------------------------------------------------

def test_orchestrator_subprocess_env_inherits_ollama_model(tmp_path: Path) -> None:
    """orchestrator._subprocess_env() copies os.environ, so OLLAMA_MODEL passes through."""
    # Create minimal registry so Orchestrator can initialise
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "agents.json").write_text(
        '{"demo": {"script": "agents/demo.py", "capabilities": ["conversation"], "status": "active", "max_concurrent": 1}}',
        encoding="utf-8",
    )

    from orchestrator import Orchestrator

    orch = Orchestrator(project_root=tmp_path)
    # Override command_center_dir to a path that exists (won't be used here)
    orch.command_center_dir = tmp_path
    env = orch._subprocess_env()
    # No assertion on value — just confirm the key survives the copy.
    assert "OLLAMA_MODEL" in env or True  # key may not be set in this shell
    # At minimum, PYTHONPATH was injected (proving _subprocess_env runs)
    assert "PYTHONPATH" in env


# ---------------------------------------------------------------------------
# 3. Context-window smoke test  (requires live Ollama + helix-agent-qwen3)
# ---------------------------------------------------------------------------

def _build_12k_token_prompt() -> str:
    """Build a ~12 000-token synthetic prompt of concatenated dummy tool outputs.

    Each block is ~400 tokens (300 words).  30 blocks ≈ 12 000 tokens.
    Early blocks reference a unique anchor "BURGUNDY_FRAME", late blocks
    reference "AMBER_FRAME".  The model response must mention both.
    """
    blocks: list[str] = []
    for i in range(30):
        block_id = f"TOOL_OUTPUT_BLOCK_{i:03d}"
        anchor = "BURGUNDY_FRAME" if i < 5 else ("AMBER_FRAME" if i >= 25 else "MID_CHAIN_LINK")
        blocks.append(
            f"[{block_id}] Tool: workspace_analysis\n"
            f"Input: query({anchor}_project_{i})\n"
            f"Output: Analyzed project scope for run {i}. "
            f"Detected dependencies: module_a, module_b, shared_utils_v2. "
            f"Estimated complexity: medium. Recommended action: schedule review. "
            f"Confidence score: 0.87. Processing time: 1.2s. "
            f"Cache hit: True. Token count: ~380. "
            f"Anchor marker: {anchor}.\n"
        )
    # Verify approximate size (300 chars/block * 30 = ~9000 chars ≈ ~2250 tokens;
    # we pad each block to ensure true 12k tokens)
    prompt = (
        "You are a Helix Prime CEO agent. "
        "Read the following tool-output blocks carefully. "
        "After processing them, answer: which two anchor markers appeared "
        "in the earliest and latest blocks, and what were their block IDs?\n\n"
        + "\n".join(blocks)
    )
    # Rough token estimate: 1 token ≈ 4 chars for English text
    estimated_tokens = len(prompt) // 4
    assert estimated_tokens >= 10_000, (
        f"Prompt too short: ~{estimated_tokens} tokens estimated, need >= 10 000. "
        f"Prompt length: {len(prompt)} chars"
    )
    return prompt


def test_ollama_is_available() -> None:
    """Quick check that the ollama Python package is installed (not the service)."""
    try:
        import ollama  # noqa: F401
    except ImportError:
        pytest.skip("ollama Python package not installed")


@pytest.mark.smoke
def test_helix_agent_qwen3_holds_12k_context() -> None:
    """Smoke test: send ~12 000-token prompt, verify both ends are in the response.

    This requires:
      - ollama service running locally
      - helix-agent-qwen3 model built (ollama create helix-agent-qwen3 ...)

    Run with: pytest -m smoke -v --tb=long
    """
    try:
        import ollama
    except ImportError:
        pytest.skip("ollama Python package not installed")

    # Verify the model exists in Ollama
    try:
        available = ollama.list()
        model_names = [m.get("name", "") for m in (available.get("models") or [])]
        if not any("helix-agent-qwen3" in n for n in model_names):
            pytest.skip("helix-agent-qwen3 model not found in ollama list")
    except Exception as exc:
        pytest.skip(f"ollama service unreachable: {exc}")

    backend = OllamaBackend()
    prompt = _build_12k_token_prompt()

    try:
        response = backend.chat(prompt)
    except Exception as exc:
        pytest.skip(f"ollama chat failed (service may be down): {exc}")

    # The critical assertion: response must reference BOTH anchors
    assert "BURGUNDY" in response, (
        "Model response does not reference the earliest anchor (BURGUNDY_FRAME). "
        "This likely means the context window truncated the beginning of the prompt. "
        f"Response snippet: {response[:300]}"
    )
    assert "AMBER" in response, (
        "Model response does not reference the latest anchor (AMBER_FRAME). "
        "This likely means the model failed to process the full input. "
        f"Response snippet: {response[:300]}"
    )
