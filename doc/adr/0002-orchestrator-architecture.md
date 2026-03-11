# ADR-0002: Orchestrator Architecture

Status: Accepted

## Context

The system is designed as a Personal AI Orchestrator responsible for
coordinating language understanding, agent reasoning, and deterministic
business logic execution.

The system interacts with users through natural language and must
support capabilities such as:

- personal finance tracking
- scheduling and reminders
- task management
- general conversational interaction

The architecture must satisfy several constraints:

- Local-first LLM inference using llama.cpp
- Low latency for common operations
- Deterministic execution for business logic
- Clear separation between reasoning and execution layers
- Future extensibility for additional capabilities

The system will eventually operate as an orchestrated multi-agent system,
where specialized agents handle different domains of responsibility.

Without a centralized orchestration component, the system would become
a tightly coupled chatbot implementation with logic scattered across
multiple layers.

## Decision

The system adopts a centralized **Orchestrator Architecture**.

The orchestrator acts as the primary control component responsible for:

- receiving processed user requests from the interface layer
- selecting the appropriate agent
- coordinating agent reasoning
- triggering tool execution
- assembling final responses

The orchestrator itself does not perform reasoning. Instead, reasoning
is delegated to specialized agents.

Agent selection is performed using an LLM-driven routing mechanism.

Model routing strategy:

- Small local model → agent selection
- Medium local model → agent reasoning and planning

Agents follow a **ReAct-style execution pattern**, where reasoning and
tool interaction occur in iterative steps.

## Agent Architecture

Each agent contains the following conceptual components:

Role  
Defines the domain responsibility of the agent.

Skills  
High-level capabilities that describe what the agent can do.

Tools  
Deterministic functions that perform real system actions.

Reasoning Strategy  
Agents use ReAct-style reasoning to decide which tools to invoke.

Agents do not directly access system infrastructure such as databases
or external APIs. All actions must occur through tools.

## Initial Agent Set

The system begins with four domain-specific agents:

FinanceAgent  
Handles personal finance operations.

CalendarAgent  
Handles scheduling and calendar management.

TaskAgent  
Handles task management and reminders.

ConversationAgent  
Handles open-ended dialogue and general assistance.

Each agent exposes a set of skills describing its capabilities.

## Tool Execution Model

All real-world system actions are executed through deterministic tools.

Examples:

finance.add_expense  
finance.query_expense  
calendar.create_event  
calendar.list_events  

Tools wrap the underlying business modules.

LLMs are not allowed to directly access databases or external systems.

## Architectural Responsibilities

Orchestrator responsibilities:

- agent selection
- request coordination
- tool execution control
- response assembly

Agent responsibilities:

- interpret request context
- perform reasoning
- select tools
- determine when the task is complete

Tool responsibilities:

- execute deterministic operations
- return structured outputs

## Consequences

Advantages:

- clear separation between reasoning and execution
- extensible architecture for future agents
- deterministic control of system side-effects
- compatibility with local LLM inference

Trade-offs:

- additional architectural complexity
- multi-step reasoning increases latency
- requires careful prompt and tool design

This architecture provides a foundation for expanding the system into
a full multi-agent personal AI platform.