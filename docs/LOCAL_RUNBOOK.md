# Helix Prime CEO — Local Runbook

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
cd "H:\10072026\Helix Prime CEO\00_command_center"
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
cd "H:\10072026\Helix Prime CEO"
$payload = '{"agent_name":"sami","prompt":"hello"}'
$payload | python .\00_command_center\orchestrator.py
```

## Automated verification
```powershell
cd "H:\10072026\Helix Prime CEO\00_command_center"
python -m pytest tests/test_orchestrator.py -q
```

## Notes for demos and recruiting
The system is designed to demonstrate a credible end-to-end product story: a persistent command center, isolated agents, shared memory, and a connected learning system that can be presented as a real operating layer rather than a toy prototype.


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
