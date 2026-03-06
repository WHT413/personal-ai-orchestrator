# System Boundary

This document defines the scope of the Personal AI Orchestrator system.

The system is designed as a local-first AI orchestration core that
coordinates language understanding, reasoning, and deterministic
system actions.

## In Scope

The system is responsible for:

Local LLM inference orchestration  
Agent selection and reasoning coordination  
Deterministic execution of system tools  
Personal finance tracking  
Scheduling and calendar management  
Task management  
User interaction through Telegram

The system coordinates agents and tools but does not directly
implement external services.

## Out of Scope

The following components are considered external systems:

Cloud LLM providers  
Messaging platforms (Telegram infrastructure)  
Calendar service providers (Google Calendar)  
External knowledge sources

The orchestrator interacts with these services through controlled
integration layers.

## System Role

The Personal AI Orchestrator acts as:

- a coordination engine for AI reasoning
- a gateway for deterministic tool execution
- a central control layer for system capabilities

It does not act as a standalone chatbot or LLM interface.

Instead, it serves as an orchestration layer that manages
agents, tools, and external integrations.