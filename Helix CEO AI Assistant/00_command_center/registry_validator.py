from typing import Dict, List, Any
from pathlib import Path
import json

def validate_registry(registry: Dict[str, Dict[str, Any]]) -> List[str]:
    required_fields = {"script", "capabilities", "status", "max_concurrent"}
    allowed_statuses = {"active", "disabled", "maintenance"}
    allowed_capabilities = {"general_reasoning", "conversation"}
    errors = []
    for agent_id, agent_data in registry.items():
        if not isinstance(agent_data, dict):
            errors.append(
                f"Agent '{agent_id}' has invalid data type: '{type(agent_id)}'. Expected dictionary."
            )
            continue
        if not isinstance(agent_id, str):
            errors.append(
                f"Agent '{agent_id}' has invalid key type: '{type(agent_id)}'. Expected string."
            )
            continue
        capabilities = agent_data.get("capabilities", [])
        if not isinstance(capabilities, list):
            errors.append(
                f"Agent '{agent_id}' has invalid capabilities type: '{type(capabilities)}'. Expected list."
            )
            continue
        if not capabilities:
            errors.append(
                f"Agent '{agent_id}' has empty capabilities list. Expected at least one capability."
            )
        for cap in capabilities:
            if cap not in allowed_capabilities:
                errors.append(
                    f"Agent '{agent_id}' has invalid capability: '{cap}'. Expected one of {allowed_capabilities}."
                )
        if "script" not in agent_data:
            errors.append(
                f"Agent '{agent_id}' is missing required field: 'script'."
            )
            continue
        if "status" not in agent_data:
            errors.append(
                f"Agent '{agent_id}' is missing required field: 'status'."
            )
            continue
        if "max_concurrent" not in agent_data:
            errors.append(
                f"Agent '{agent_id}' is missing required field: 'max_concurrent'."
            )
            continue
        max_concurrent = agent_data.get("max_concurrent")
        if max_concurrent is not None and not isinstance(max_concurrent, int):
            errors.append(
                f"Agent '{agent_id}' has invalid max_concurrent type: '{type(max_concurrent)}'. Expected integer."
            )
            continue
        elif max_concurrent is not None and max_concurrent < 1:
            errors.append(
                f"Agent '{agent_id}' has invalid max_concurrent value: '{max_concurrent}'. Must be >= 1."
            )
        if agent_data["status"] not in allowed_statuses:
            errors.append(
                f"Agent '{agent_id}' has invalid status: '{agent_data['status']}'. Expected one of {allowed_statuses}."
            )
    return errors

def main():
    registry_path = Path(__file__).resolve().parent.parent / "config" / "agents.json"
    if not registry_path.exists():
        print("Configuration file not found.")
        return
    try:
        with open(registry_path, "r") as f:
            registry = json.load(f)
        errors = validate_registry(registry)
        if errors:
            print(f"VALIDATION FAILED — {len(errors)} error(s):")
            for e in errors:
                print(f"  - {e}")
        else:
            print(f"VALIDATION PASSED — {len(registry)} agent(s) verified clean.")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")

if __name__ == "__main__":
    main()