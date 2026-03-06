# Request Lifecycle

This document describes how a user request flows through the system.

## Step 1 — User Interaction

A user sends a message through the interface layer.

Example:

Telegram message.

The interface forwards the request to the orchestrator.

## Step 2 — Guardrails

Before processing, guardrails validate the request.

Checks may include:

- safety policies
- request validity
- permission checks

Invalid requests are rejected early.

## Step 3 — Agent Selection

The orchestrator selects an agent capable of handling the request.

Agent selection is performed using a small local language model.

The model analyzes the request and chooses the most appropriate agent.

Example outcome:

FinanceAgent  
CalendarAgent  
TaskAgent  
ConversationAgent

## Step 4 — Agent Reasoning

The selected agent receives the request.

The agent performs reasoning using a medium-sized language model.

Agents follow a ReAct-style reasoning pattern:

1. interpret the request
2. decide which tool to use
3. execute the tool
4. observe the result
5. determine whether additional actions are needed

## Step 5 — Tool Execution

When the agent selects a tool, the orchestrator executes the
corresponding deterministic function.

Example:

finance.add_expense

Tools interact with system modules or external services.

The result is returned to the agent.

## Step 6 — Task Completion

Once the agent determines the task is complete, it produces a final
response.

The orchestrator formats the response and sends it back through
the interface layer.

## Step 7 — Response Delivery

The final response is delivered to the user through the interface.

Example:

Telegram message reply.