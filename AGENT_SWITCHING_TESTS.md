# Agent Switching & Memory System - Test Guide

## Overview
The Helix Prime CEO now has a sophisticated agent switching system with shared memory management. Agents can now:
- Access shared memory (all agents read/write)
- Track accomplishments
- Maintain SAMI's strategic memory
- Preserve conversation context across switches
- Reference each other's work

## Memory Architecture

### 1. **Shared Memory** (`memory.json`)
- **Access**: All agents
- **Contents**: Session logs, interactions, total counts
- **Purpose**: Central hub of all agent activity

### 2. **Agent Accomplishments** (`agent_accomplishments.json`)
- **Access**: All agents (read), individual agents (write)
- **Structure**:
  ```json
  {
    "AGENT_NAME": {
      "total": 5,
      "items": [
        {
          "timestamp": "2026-07-04T10:30:00",
          "accomplishment": "Created lesson on Machine Learning",
          "details": {...}
        }
      ]
    }
  }
  ```

### 3. **SAMI Strategic Memory** (`sami_strategic_memory.json`)
- **Access**: SAMI only (read/write)
- **Contents**:
  - Directives for other agents
  - Agent assignments and roles
  - Priorities
  - Decisions
  - Next steps

### 4. **Agent Context** (`agent_context.json`)
- **Access**: All agents
- **Contents**:
  - Current active agent
  - Conversation history (last 100 entries)
  - Active tasks
  - Last agent switch timestamp

## Testing Procedure

### Test 1: Basic Agent Switching
```bash
# Terminal 1: Start orchestrator with SAMI
echo '{"agent_name": "SAMI", "prompt": "hello"}' | python orchestrator.py

# Terminal 2: Switch to WILI
echo '{"agent_name": "WILI", "command": "teach", "args": {"topic": "Python"}}' | python orchestrator.py
```

### Test 2: Check Context About SAMI from WILI
```bash
# While logged in as WILI, ask about SAMI's work
echo '{
  "agent_name": "WILI",
  "command": "context",
  "args": {"agent": "SAMI"}
}' | python orchestrator.py
```

**Expected Output**:
```
📊 Context About SAMI:
━━━━━━━━━━━━━━━━━━━━━━━━
📊 SAMI's Accomplishments (N total):
1. Processed: hello (2026-07-04)
2. Processed: ...

SAMI is the CEO Orchestrator coordinating all agents.
```

### Test 3: List All Agent Accomplishments
```bash
# Get a summary of all agents
echo '{
  "agent_name": "WILI",
  "command": "context",
  "args": {"agent": "all"}
}' | python orchestrator.py
```

### Test 4: Verify Shared Memory Access
```python
# Direct Python test
from memory_manager import get_memory_manager

mgr = get_memory_manager()

# Test shared memory
shared = mgr.get_shared_memory()
print(f"Total interactions: {shared['total_interactions']}")

# Test accomplishments
accomplishments = mgr.get_agent_accomplishments()
for agent in accomplishments:
    print(f"{agent}: {accomplishments[agent]['total']} accomplishments")

# Test SAMI's strategy
strategy = mgr.get_sami_strategy()
print(f"SAMI Priorities: {strategy['priorities']}")
```

### Test 5: Verify Context Preservation
```bash
# Sequence of interactions maintaining context
echo '{"agent_name": "SAMI", "prompt": "Start project X"}' | python orchestrator.py
echo '{"agent_name": "WILI", "command": "teach", "args": {"topic": "X"}}' | python orchestrator.py
echo '{"agent_name": "PHILI", "command": "check_mode", "args": {"mood": "focused"}}' | python orchestrator.py
echo '{"agent_name": "SUBY", "command": "create", "args": {"type": "dashboard", "name": "Project X"}}' | python orchestrator.py

# Then check context from any agent
echo '{"agent_name": "WILI", "command": "context", "args": {"agent": "SAMI"}}' | python orchestrator.py
```

## Key Features

### 1. Memory Manager API

```python
from memory_manager import get_memory_manager

mgr = get_memory_manager()

# Shared memory operations
mgr.log_session("WILI", "teach", "Lesson created")
shared = mgr.get_shared_memory()

# Accomplishments
mgr.add_accomplishment("WILI", "Created Python lesson")
summary = mgr.get_accomplishments_summary("WILI")

# SAMI strategic memory
mgr.add_directive("Build dashboard", ["SUBY", "WILI"])
strategy = mgr.get_sami_strategy()

# Context operations
mgr.set_current_agent("WILI")
mgr.add_conversation_entry("WILI", "Message content")
```

### 2. Agent Switching in UI

When switching agents in the web interface:
1. Conversation context is preserved
2. Previous agent's work is logged
3. New agent can query previous work
4. SAMI maintains strategic overview

### 3. Cross-Agent Communication

**Example**: WILI asking about SAMI's accomplishments
```
User: "While talking to WILI, ask what SAMI accomplished"
→ WILI queries: get_accomplishments_summary("SAMI")
→ Returns: "SAMI processed 3 tasks today..."
```

## Testing Checklist

- [ ] Shared memory updates correctly after each agent interaction
- [ ] Accomplishments are logged for each agent
- [ ] WILI can query SAMI's accomplishments
- [ ] PHILI can see SUBY's recent work
- [ ] SUBY can reference WILI's lessons
- [ ] Current agent context is tracked
- [ ] Conversation history maintains last 100 entries
- [ ] SAMI's strategic memory persists correctly
- [ ] Agent context switches properly update timestamp
- [ ] All agents can read shared memory

## Files Involved

### Core Memory System
- `00_command_center/memory_manager.py` - Central memory management
- `00_command_center/orchestrator.py` - Updated to use memory manager
- `06_memory/memory.json` - Shared memory
- `06_memory/agent_accomplishments.json` - Accomplishment tracking
- `06_memory/sami_strategic_memory.json` - SAMI's strategic info
- `06_memory/agent_context.json` - Conversation context

### Updated Agents
- `00_command_center/agents/sami.py` - Logs accomplishments
- `00_command_center/agents/wili.py` - Can query agent context
- `00_command_center/agents/phili.py` - Logs accomplishments
- `00_command_center/agents/suby.py` - Logs accomplishments

## Troubleshooting

### Issue: Memory files not being updated
**Solution**: Check file permissions on `06_memory/` directory

### Issue: Context queries returning empty
**Solution**: Ensure agents have executed commands first to populate accomplishments

### Issue: Agent switching not preserving context
**Solution**: Verify `agent_context.json` is being updated by orchestrator

## Next Steps

1. **Test in Web UI** - Update bridge.py to support agent switching with memory awareness
2. **Add Agent Dashboard** - Show all agents' accomplishments in real-time
3. **Implement Auto-Directives** - SAMI automatically assigns tasks to agents
4. **Add Memory Search** - Query past interactions across agents
5. **Create Memory UI** - Visual representation of agent work and context

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
