# Helix CEO AI Assistant — Local Runbook

## Purpose
This project is a local-first AI orchestration system that runs a persistent Go daemon, routes requests through a Python orchestrator, and executes four isolated agents: SAMI, WILI, PHILI, and SUBY.

## Runtime architecture
- Go daemon: 00_command_center/engine.go
- Python orchestrator: 00_command_center/orchestrator.py
- Agent registry: config/agents.json
- Shared memory: 06_memory/
- Learning integration: AI Automation Engineering/02_learning_system/browser_engine

## Clean-code requirements applied
- Type hints are present on the orchestrator and supporting runtime entry points.
- Broad exception handlers were replaced with specific exception handling.
- Paths are derived from Path(__file__) and project-root injection rather than hardcoded drive letters.
- Agent execution is isolated behind subprocess boundaries.

## Local startup
From the project root:

```powershell
cd "H:\Helix CEO AI Assistant\00_command_center"
go build -o engine.exe engine.go
.\engine.exe
```

Then enter commands such as:

```text
sami hello
wili teach me a lesson
phili reflect on my day
suby generate a dashboard app
```

## Direct orchestrator test
```powershell
cd "H:\Helix CEO AI Assistant"
$payload = '{"agent_name":"sami","prompt":"hello"}'
$payload | python .\00_command_center\orchestrator.py
```

## Automated verification
```powershell
cd "H:\Helix CEO AI Assistant\00_command_center"
python -m pytest tests/test_orchestrator.py -q
```

## Notes for demos and recruiting
The system is designed to demonstrate a credible end-to-end product story: a persistent command center, isolated agents, shared memory, and a connected learning system that can be presented as a real operating layer rather than a toy prototype.
