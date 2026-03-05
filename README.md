# Personal AI Orchestrator

This repository contains a production-oriented personal AI assistant
core, designed around strict orchestration, routing, and local LLM
inference.

## Scope and Intent

This repository focuses strictly on the **core orchestration layer** of a
personal AI assistant.

It is not intended to be a full end-user application at this stage.
Instead, it serves as a controlled environment for validating architectural
decisions around orchestration, routing, and local LLM execution.

The emphasis is on:
- Correctness over features
- Explicit control flow
- Predictable runtime behavior

---

## Architecture Overview

The system follows an **orchestrator-first design**.

- The Orchestrator owns all control flow and decision-making
- LLMs are treated as **stateless execution workers**
- Prompts are inputs, not sources of logic
- Business rules never live inside the model

This ensures that:
- System behavior remains deterministic
- Failures are observable and debuggable
- LLMs can be swapped without rewriting core logic

---

## Local LLM Inference

Local inference is performed using `llama.cpp`, invoked through a
Python subprocess boundary.

Key characteristics of the current approach:
- Batch size is fixed at 1
- Each inference call is a one-shot execution
- Process lifecycle is explicitly controlled
- Hard timeouts are enforced as guardrails

The LLM runtime is deliberately **not exposed as an HTTP service**
at this stage to avoid unnecessary complexity.

Architectural rationale and trade-offs are documented in `ADR-0001`.

---

## Repository Structure

```text
personal-ai-orchestrator/
├── core/                         # Orchestration and routing logic
├── llm_runtime/                  # Local LLM runtime boundary
├── prompt/                       # Prompt construction utilities
├── scripts/
│   └── dev/                      # Development-only validation scripts
├── adr/                          # Architectural Decision Records
└── README.md
```

### Notes:
* **`core/`** must remain free of LLM-specific assumptions.
* **`llm_runtime/`** isolates all model execution concerns.
* **`scripts/dev/`** contains non-production tooling only.
* **`adr/`** captures decisions, not implementation details.

---

## Development Workflow

Development is performed on a separate `dev` branch. The `main` branch is reserved for:
* **Stable code**
* **Reviewed architectural changes**
* **Behavior** that aligns with documented ADRs

Development-only scripts and experiments are intentionally kept out of the production path.

---

## Current Status

The system is currently in a **stabilization phase**. Primary focus areas:
1.  **Local LLM runtime correctness**
2.  **Deterministic orchestration behavior**
3.  **Clear architectural boundaries**

Feature expansion is intentionally deferred until these foundations are proven stable.