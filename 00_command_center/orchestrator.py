"""Route Go daemon requests through the Python command center to isolated agents.

The Go engine sends a JSON payload to this module over stdin. The orchestrator
validates the requested agent against the project registry, records the active
conversation context through the shared memory manager, then executes the
agent's script in a subprocess so agent crashes do not terminate the command
center process.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from dispatcher import get_active_agents, select_agent
from memory_manager import get_memory_manager


LOGGER = logging.getLogger(__name__)
SUBPROCESS_TIMEOUT_SECONDS = int(os.environ.get("HELIX_AGENT_TIMEOUT", "180"))


class RegistryLoadError(Exception):
    """Raised when the agent registry cannot be loaded."""


class Orchestrator:
    """Coordinates registry validation, memory updates, and agent execution."""

    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.project_root = (project_root or Path(__file__).resolve().parents[1]).resolve()
        self.command_center_dir = Path(__file__).resolve().parent
        self.memory_manager = get_memory_manager(memory_dir=self.project_root / "06_memory")
        self.registry = self.load_registry()
        self._check_constitution()

    def load_registry(self) -> Dict[str, Any]:
        """Load the configured agent registry from config/agents.json."""
        registry_path = self.project_root / "config" / "agents.json"

        try:
            with registry_path.open("r", encoding="utf-8-sig") as registry_file:
                registry = json.load(registry_file)
        except FileNotFoundError as exc:
            raise RegistryLoadError(f"Agent registry not found: {registry_path}") from exc
        except json.JSONDecodeError as exc:
            raise RegistryLoadError(
                f"Agent registry contains invalid JSON: {registry_path}: {exc}"
            ) from exc

        if not isinstance(registry, dict):
            raise RegistryLoadError(
                f"Agent registry must contain a JSON object: {registry_path}"
            )

        return registry

    def dispatch(self, agent_name: str, prompt: str) -> str:
        """Validate and execute the requested agent, returning terminal-safe text."""
        suggested_agent = select_agent(prompt, self.registry)
        active_agents = get_active_agents(self.registry)

        if agent_name not in self.registry:
            suggestion = f" Suggested active agent: {suggested_agent}." if suggested_agent else ""
            active = ", ".join(active_agents) if active_agents else "none"
            return (
                f"Error: unknown agent '{agent_name}'. Active agents: {active}."
                f"{suggestion}"
            )

        agent_config = self.registry[agent_name]
        status = agent_config.get("status")
        if status != "active":
            return (
                f"Error: agent '{agent_name}' is not active "
                f"(status: {status or 'unknown'})."
            )

        script_value = agent_config.get("script")
        if not isinstance(script_value, str) or not script_value:
            return f"Error: agent '{agent_name}' has no valid script configured."

        agent_script = self.command_center_dir / script_value
        if not agent_script.is_file():
            return f"Error: agent script for '{agent_name}' was not found: {agent_script}"

        self.memory_manager.set_current_agent(agent_name)
        self.memory_manager.add_conversation_entry(agent_name, prompt)

        payload = json.dumps(self._agent_payload(agent_name, prompt), ensure_ascii=False)
        subprocess_env = self._subprocess_env()

        try:
            completed = subprocess.run(
                [sys.executable, str(agent_script)],
                input=payload,
                text=True,
                capture_output=True,
                timeout=SUBPROCESS_TIMEOUT_SECONDS,
                check=False,
                cwd=str(self.command_center_dir),
                encoding="utf-8",
                env=subprocess_env,
            )
        except subprocess.TimeoutExpired:
            return (
                f"Error: agent '{agent_name}' timed out after "
                f"{SUBPROCESS_TIMEOUT_SECONDS} seconds."
            )
        except OSError as exc:
            return f"Error: could not execute agent '{agent_name}': {exc}"

        # If the agent exited with a non-zero code, prefer stderr for diagnostics.
        response = (completed.stdout or "").strip()
        if completed.returncode != 0:
            stderr = (completed.stderr or "").strip()
            if stderr:
                response = f"Error: agent '{agent_name}' failed: {stderr}"
            else:
                response = f"Error: agent '{agent_name}' exited with code {completed.returncode}."
        self.memory_manager.log_session(agent_name, prompt, response)
        return response

    def _agent_payload(self, agent_name: str, prompt: str) -> Dict[str, Any]:
        """Adapt the Go prompt contract to each agent script's command contract."""
        if agent_name == "wili":
            prompt_lower = prompt.lower().strip()
            if any(keyword in prompt_lower for keyword in ["teach", "learn", "lesson", "study", "quiz"]):
                return {"command": "teach", "args": {"topic": prompt}}
            return {"command": "query", "args": {"question": prompt}}
        if agent_name == "phili":
            return {"command": "reflect", "args": {"question": prompt}}
        if agent_name == "suby":
            return {"command": "generate", "args": {"spec": prompt}}
        return {"prompt": prompt}

    def _subprocess_env(self) -> Dict[str, str]:
        """Build subprocess environment with command center import path available."""
        subprocess_env = os.environ.copy()
        existing_pythonpath = subprocess_env.get("PYTHONPATH", "")
        subprocess_env["PYTHONPATH"] = (
            str(self.command_center_dir) + os.pathsep + existing_pythonpath
            if existing_pythonpath
            else str(self.command_center_dir)
        )
        return subprocess_env

    def _check_constitution(self) -> None:
        constitution_path = self.project_root / "docs" / "00_CONSTITUTION.md"
        if constitution_path.is_file():
            LOGGER.info("Constitution file present: %s", constitution_path)
        else:
            LOGGER.warning("Constitution file missing: %s", constitution_path)


def main() -> None:
    """Read the Go daemon payload from stdin, dispatch it, and print the result."""
    raw_payload = sys.stdin.read()

    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON payload: {exc}")
        sys.exit(1)

    if not isinstance(payload, dict):
        print("Error: JSON payload must be an object.")
        sys.exit(1)

    agent_name = payload.get("agent_name")
    prompt = payload.get("prompt")

    if not isinstance(agent_name, str) or not isinstance(prompt, str):
        print("Error: payload must contain string fields 'agent_name' and 'prompt'.")
        sys.exit(1)

    try:
        orchestrator = Orchestrator()
    except RegistryLoadError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    result = orchestrator.dispatch(agent_name, prompt)
    print(result)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Ensure stdout uses UTF-8 to avoid UnicodeEncodeError when printing
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        # Older Python builds or unusual environments may not support reconfigure;
        # in that case fall back to the default behavior.
        pass
    main()
