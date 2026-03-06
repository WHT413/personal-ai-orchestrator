# Development Scope

This document defines the scope of early development phases.

The goal is to incrementally build the system architecture while
maintaining stability and low operational complexity.

## Phase 1 Goals

Phase 1 focuses on establishing the core infrastructure required
for the system to operate.

Objectives:

- Stable llama.cpp runtime wrapper
- Basic orchestrator skeleton
- Deterministic execution of finance and calendar actions
- Telegram interface integration
- Basic guardrails and request routing

The system in Phase 1 will primarily operate as a deterministic
pipeline rather than a full multi-agent system.

Agent reasoning capabilities will be introduced in later phases.

## Phase 1 Capabilities

Supported capabilities:

- Record expenses
- Query expenses
- Create calendar events
- List calendar events

These actions will be executed through deterministic business modules.

## Explicitly Excluded From Phase 1

The following capabilities are intentionally excluded to reduce
system complexity during early development:

- Multi-agent reasoning
- ReAct-style agent execution loops
- Advanced memory management
- Long-term knowledge storage
- Retrieval-augmented generation (RAG)
- Autonomous task planning
- Multi-agent collaboration

These features will be considered in later phases.

## Phase 2 Direction

Future development phases may introduce:

- agent-based reasoning
- skill-based capability discovery
- more complex planning workflows
- expanded tool ecosystems

The architecture is designed to support these capabilities without
requiring fundamental structural changes.