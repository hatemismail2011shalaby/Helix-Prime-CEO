from pathlib import Path
import sys, json, subprocess, datetime
from dispatcher import select_agent

def get_registry():
    base_dir = Path(__file__).resolve().parent.parent
    registry_path = base_dir / "config" / "agents.json"
    with open(registry_path, 'r') as f:
        return json.load(f)

def log_interaction(agent_name, prompt, response):
    memory_path = Path(__file__).resolve().parent.parent / "06_memory" / "memory.json"
    try:
        with open(memory_path, 'r') as f:
            memory = json.load(f)
        memory["sessions"].append({
            "timestamp": datetime.datetime.now().isoformat(),
            "agent": agent_name,
            "prompt": prompt,
            "response": response
        })
        memory["total_interactions"] += 1
        memory["last_active"] = datetime.datetime.now().isoformat()
        with open(memory_path, 'w') as f:
            json.dump(memory, f, indent=2)
    except Exception as e:
        import traceback
        print(f"MEMORY ERROR: {e}")
        traceback.print_exc()

def run():
    constitution = Path(__file__).resolve().parent.parent / "docs" / "00_CONSTITUTION.md"
    if not constitution.exists():
        print("ERROR: Constitution missing")
        sys.exit(1)
    input_data = json.loads(sys.stdin.read())
    agent_name = input_data.get("agent_name")
    registry = get_registry()
    prompt = input_data.get("prompt", "")
    
    if agent_name and agent_name in registry:
        agent = registry[agent_name]
        if agent["status"] == "active":
            pass  # Use this agent directly
        elif agent["status"] != "active":
            print(f"ERROR: Agent {agent_name} is not active (status: {agent['status']})")
            return
    else:
        agent_name = select_agent(prompt, registry)
        if agent_name is None:
            print("ERROR: No active agents available in registry")
            return
    
    script_path = registry[agent_name]["script"]
    if not Path(script_path).is_absolute():
        script_path = Path(__file__).resolve().parent / script_path
    
    try:
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=json.dumps(input_data))
        
        if process.returncode != 0:
            print(f"ERROR: Failed to execute {script_path}: {stderr}")
        else:
            print(stdout)
            log_interaction(agent_name, prompt, stdout)
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    run()