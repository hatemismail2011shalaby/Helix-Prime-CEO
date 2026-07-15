## The Helix Ecosystem

Helix is an accumulated operations solution — 28 years of contact-centre, WFM, and BPO operations fused with 14 years of AI automation engineering — that has evolved from AI-as-a-tool into a full automated agentic organization. It exists to deliver real, preventive solutions for business's most critical operations workflows: talent acquisition, workforce forecasting, real-time adherence, customer churn, and client onboarding.

The full canonical narrative — origin, mission, the two repositories, engineering philosophy (Constitution 000), and verified local test results — is the **single source of truth** in `MASTER STORY.docx` and is reproduced in full at the end of this document under "## Helix Ecosystem — Master Story".

---

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

---

## Helix Ecosystem — Master Story

> Source of truth: `MASTER STORY.docx`. The canonical Helix narrative is reproduced below for every project document so the ecosystem story stays consistent.

# THE HELIX ECOSYSTEM - MASTER STORY
Single Source of Truth

## Origin: An Accumulated Operations Solution
Helix is not a tutorial project and not a chatbot wrapper. It is the accumulated operational solution of 28 years in contact-centre, Workforce Management (WFM), and BPO operations, fused with 14 years of AI automation engineering. Every engine encodes hard-won operational truth: how staffing actually fails, why adherence slips, what makes a client churn, where onboarding breaks.

## AI as a Tool, Then an Agentic Organization
We began by using AI as a tool - local models and scripts that solved one painful workflow at a time (Erlang C staffing, real-time adherence, churn risk, client SOP generation). Those tools compounded. They became a system of specialized agents and domain engines that observe, reason, remember, and act. Helix is now a full automated agentic organization: humans supervise, the system executes.

## Mission
To deliver the ultimate, powerful, real solutions for business's most critical operations workflows - the reactive-not-predictive pain points that quietly drain enterprises: talent acquisition, workforce forecasting, real-time adherence, customer churn, and client onboarding. Not dashboards that report the past, but systems that prevent the failure before it happens.

## The Two Repositories
The Helix Ecosystem ships as two focused repositories:

1. AI Automation Engineering - the operational engine platform. Five domain engines (WFM Forecasting, RTA Command Center, CX Churn Sentinel, B2B Onboarding, Helix Personnel) unified in one Streamlit command center, plus a metacognitive memory layer (TMK loop) that learns across engines.
2. Helix Prime CEO - the agentic orchestration system. A Go runtime daemon routes tasks through a Python orchestrator to a capability-tagged agent registry (SAMI, WILI, PHILI, SUBY) with crash-isolated subprocess execution, shared memory, and local RAG. Zero mandatory cloud dependency.

## Engineering Philosophy - Constitution 000
Architecture is the expression of truth. Identity precedes implementation. No hardcoded configuration. Crash isolation by design. Local-first, secure, human-supervised. Every decision must reveal the assumptions it introduces.

## Verified Working - Local Test Results
- Unified dashboard boots clean on localhost:8501 (Streamlit, headless).
- All sections render: Home, WFM, RTA, CX, B2B, Personnel Board, Metacognition.
- WFM Erlang C pipeline returns required agents, SLA-met flag, occupancy, service level.
- RTA adherence and variance charts render from sample schedule CSV.
- CX 4-KPI risk scorer classifies Critical / High / Medium / Low.
- B2B SOP generator produces staffing plan + Notion payload.
- Personnel Board: hiring funnel, open requisitions, staffing recommendations, pending actions (Generate), HR Director Report - all render; empty-states safe with no seeded data.
- Metacognition: memory store, cross-engine pattern detection, TMK reflect, decision log all functional.
- python -m compileall passes; CEO daemon crash-isolation verified (agent crash leaves daemon and memory intact).

## Trajectory
Single operations practitioner -> accumulated operational solution -> AI-augmented toolset -> full automated agentic organization, purpose-built to solve the operations workflows that matter most.
