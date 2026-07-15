# Contributing to Helix Prime CEO

## Getting Oriented

Before contributing, please read these documents in order:

1. **CONSTITUTION_000_DAY_ZERO.md** (read this first — it explains why this project exists, not just how it works)
2. [README.md](./README.md)
3. [docs/00_CONSTITUTION.md](./docs/00_CONSTITUTION.md)
4. [docs/LOCAL_RUNBOOK.md](./docs/LOCAL_RUNBOOK.md)

## Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Code Standards

- Follow the Helix Clean Code Constitution (docs/00_CONSTITUTION.md)
- All agents must pass constitution check before execution
- Memory logging is mandatory for all agent interactions
- Crash isolation must be preserved

## Testing

- Test agent changes with `python agents/<agent>.py` via stdin JSON
- Verify engine builds with `go build -o engine.exe engine.go`
- Run crash isolation tests before submitting

## Commit Messages

Use conventional commits:
- `feat:` new capability
- `fix:` bug fix
- `refactor:` code restructuring
- `docs:` documentation updates
- `test:` test additions

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
