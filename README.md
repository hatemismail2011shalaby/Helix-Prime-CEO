# Helix Prime CEO

> This project is built under [Constitution 000 — Day Zero](./CONSTITUTION_000_DAY_ZERO.md), the foundational engineering philosophy that governs every decision in this codebase. Read it first.

A production-grade local AI orchestration middleware. Go-based persistent runtime daemon routes tasks through a Python orchestration layer to a capability-tagged agent registry — zero cloud dependency, fully local inference via Ollama.

## Prerequisites

- **Go** — for building the engine daemon
- **Python 3.13+** — for the orchestration and agent layers
- **Ollama** — installed and running as the local inference backend
- **Required Ollama models** — pull these:

```powershell
ollama pull qwen3:14b
ollama pull nomic-embed-text
```

## ⚠️ Critical Setup Warning

If the `OLLAMA_HOST` environment variable is set to `0.0.0.0:11434` anywhere in your system environment, the Python `ollama` client will fail to connect even though the Ollama CLI works fine. It must be set to `127.0.0.1:11434` for local development.

Diagnose with:
```powershell
Get-ChildItem Env: | Where-Object { $_.Name -eq "OLLAMA_HOST" }
```

Fix with:
```powershell
[System.Environment]::SetEnvironmentVariable("OLLAMA_HOST", "127.0.0.1:11434", "User")
```
Then **restart your terminal**.

## Installation

```powershell
# Clone the repository
git clone <repo-url>
cd "Helix Prime CEO"

# Install Python dependencies
pip install -r requirements.txt --break-system-packages

# Pull required Ollama models
ollama pull qwen3:14b
ollama pull nomic-embed-text

# Build the Go engine daemon
cd 00_command_center
go build -o engine.exe engine.go
cd ..
```

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

You can interact with Helix Prime CEO in three ways:

### 1. Via the Go engine daemon (recommended for persistent use)

```powershell
cd 00_command_center
go build -o engine.exe engine.go
.\engine.exe
```

Then type: `<agent_name> <task>` — e.g. `sami hello`
Type `exit` or `quit` to shut down.

### 2. Via the orchestrator directly (one-shot commands)

```powershell
echo '{"agent_name":"sami","prompt":"hello"}' | python 00_command_center/orchestrator.py
```

### 3. Via the web UI (bridge.py)

```powershell
cd 00_command_center
uvicorn bridge:app --reload
```

Open http://localhost:8000 in your browser.

## Testing

Run the test suite:
```powershell
pytest 00_command_center/tests/ -v
```

Smoke-test individual agents via stdin:
```powershell
echo '{"command": "...", "args": {...}}' | python agents/<agent>.py
```

## RAG System

The project includes a retrieval-augmented generation (RAG) module located in `00_command_center/rag/`:

- **embedder.py** — generates vector embeddings using `nomic-embed-text` via Ollama
- **chunker.py** — splits documents into manageable chunks for indexing
- **vector_store.py** — manages ChromaDB collections for persistent vector storage
- **retriever.py** — queries the vector store and returns relevant context for agent prompts

Embeddings are generated locally by the `nomic-embed-text` model. ChromaDB data persists to `06_memory/vector_store/`, which is gitignored — it is per-user state, not shipped in the repository.

## Status
Phase 1 complete — verified end-to-end including crash isolation testing. Sprint 2 complete — capability-tagged registry, dispatcher layer, persistent session daemon all operational. RAG integration complete 2026-07-14 across all four agents (SAMI, WILI, PHILI, SUBY).

## License
MIT
