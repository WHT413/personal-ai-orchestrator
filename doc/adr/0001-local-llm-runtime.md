# ADR-0001: Local LLM Runtime Strategy

## Context
The system requires low-latency LLM inference on a single GPU (8GB VRAM)
for a Telegram-based personal assistant. Concurrency is low, and
batch size is 1.

## Decision
Use llama.cpp as the local LLM runtime, wrapped via a Python subprocess
interface. The LLM runtime is not exposed as an HTTP API at this stage.

## Rationale
- Lowest latency for batch=1
- Native support for GGUF quantized models
- Full control over timeout and process lifecycle
- Avoids premature Docker/API overhead

## Consequences
- No horizontal scaling at this stage
- Future migration to API-based serving remains possible