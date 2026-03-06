# Architecture Overview

The Personal AI system is designed as an orchestrated multi-agent platform.

The architecture separates language reasoning, system coordination,
and deterministic execution into distinct layers.

## High-Level Architecture

User Interface Layer  
Handles user interaction through external platforms.

Orchestration Layer  
Coordinates agents, model routing, and tool execution.

Agent Layer  
Contains domain-specific reasoning agents.

Tool Layer  
Contains deterministic functions that perform system actions.

Infrastructure Layer  
Handles LLM runtime, configuration, and external integrations.

## Layer Description

Interface Layer

Receives user requests and returns responses.

Example:

Telegram Bot

This layer contains no business logic.

Orchestration Layer

The orchestrator acts as the system brain.

Responsibilities include:

- request coordination
- agent selection
- model routing
- tool execution control

Agent Layer

Agents perform reasoning and planning.

Each agent is responsible for a specific domain.

Agents use ReAct-style reasoning loops to determine
which tools to execute.

Initial agents include:

FinanceAgent  
CalendarAgent  
TaskAgent  
ConversationAgent  

Skill Layer

Skills describe agent capabilities.

Skills provide structured descriptions of:

- supported actions
- expected inputs
- relevant tools

Skills do not execute actions directly.

Tool Layer

Tools perform deterministic operations.

Examples:

finance.add_expense  
finance.query_expense  
calendar.create_event  
task.create_task  

Tools act as wrappers around system modules.

Infrastructure Layer

Provides supporting infrastructure:

- llama.cpp runtime
- model management
- configuration
- logging
- external API integrations