# Helix CEO AI Assistant

A production-grade local AI orchestration middleware. Go-based persistent runtime daemon routes tasks through a Python orchestration layer to a capability-tagged agent registry — zero cloud dependency, fully local inference via Ollama.

## Architecture
engine.exe (Go daemon, persistent listening mode) → orchestrator.py (constitution check, registry read, agent dispatch, memory logging) → dispatcher.py (capability-based routing) → agent scripts → Ollama local inference. The repository layout centers on 00_command_center/ for the daemon, orchestrator, and dispatcher, config/ for the registry, 06_memory/ for stored interaction history, and docs/ for the operating constitution.

## Key Design Principles
- Zero hardcoded configuration (capability-tagged registry, not flat name-to-path mapping)
- Clean separation of concerns: routing (Go) / orchestration (Python) / dispatch logic (pure functions) / agent execution (isolated subprocess)
- Crash isolation: agent failures do not crash the daemon or corrupt memory state
- Persistent session daemon: one process, many tasks, until explicit shutdown

## Tech Stack
Go (runtime engine), Python (orchestration, dispatch), JSON (registry, memory, IPC), Ollama (local LLM inference)

## Quickstart
cd 00_command_center

go build -o engine.exe engine.go

.\engine.exe

```
Then type: `<agent_name> <task>` — e.g. `sami hello`
Type `exit` or `quit` to shut down.

## Status
Phase 1 complete — verified end-to-end including crash isolation testing. Sprint 2 complete — capability-tagged registry, dispatcher layer, persistent session daemon all operational.

## License
MIT
