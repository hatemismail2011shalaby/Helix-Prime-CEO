from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from orchestrator import Orchestrator, RegistryLoadError  # noqa: E402


def test_load_registry_accepts_utf8_bom(tmp_path: Path) -> None:
    project_root = tmp_path
    config_dir = project_root / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    registry_payload = '{"demo": {"script": "agents/demo.py", "capabilities": ["conversation"], "status": "active", "max_concurrent": 1}}'
    (config_dir / "agents.json").write_bytes("\ufeff".encode("utf-8") + registry_payload.encode("utf-8"))

    orchestrator = Orchestrator(project_root=project_root)

    assert orchestrator.registry["demo"]["status"] == "active"


def test_dispatch_executes_agent_script_and_returns_stdout(tmp_path: Path) -> None:
    project_root = tmp_path
    command_center_dir = project_root / "command_center"
    agent_dir = command_center_dir / "agents"
    agent_dir.mkdir(parents=True, exist_ok=True)

    config_dir = project_root / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "agents.json").write_text(
        json.dumps(
            {
                "demo": {
                    "script": "agents/demo.py",
                    "capabilities": ["conversation"],
                    "status": "active",
                    "max_concurrent": 1,
                }
            }
        ),
        encoding="utf-8",
    )

    agent_script = agent_dir / "demo.py"
    agent_script.write_text(
        "import sys\n"
        "import json\n"
        "data = json.loads(sys.stdin.read())\n"
        "print(f'agent:{data.get(\"prompt\", \"\")}')\n",
        encoding="utf-8",
    )

    orchestrator = Orchestrator(project_root=project_root)
    orchestrator.command_center_dir = command_center_dir
    orchestrator.registry = orchestrator.load_registry()

    result = orchestrator.dispatch("demo", "hello")

    assert result == "agent:hello"


def test_agent_payload_routes_wili_teach_prompts(tmp_path: Path) -> None:
    project_root = tmp_path
    config_dir = project_root / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "agents.json").write_text(
        json.dumps({"dummy": {"script": "agents/dummy.py", "status": "active"}}),
        encoding="utf-8",
    )

    orchestrator = Orchestrator(project_root=project_root)

    payload = orchestrator._agent_payload("wili", "Teach me about Python functions")

    assert payload["command"] == "teach"
    assert payload["args"]["topic"] == "Teach me about Python functions"
