"""
DEV-ONLY SCRIPT

Purpose:
- Validate local llama.cpp runtime via subprocess
- Smoke-test LlamaRunner implementation (ADR-0001)

Notes:
- Not a production entrypoint
- May assume local paths and dev-only configs
"""

import sys
from pathlib import Path

from llm_runtime.llama_runner import LlamaRunner
from core.prompt_builder import PromptBuilder
from core.orchestrator import Orchestrator

def main():
    runner = LlamaRunner(
        llama_binary_path="~/WORKSPACE/HieuNT/benchmark/llama.cpp/build/bin/llama-cli",
        model_path="~/WORKSPACE/HieuNT/benchmark/llama.cpp/models/qwen2.5-3b/qwen2.5-3b-instruct-q4_k_m.gguf",
        context_size=2048,
        temperature=0.7,
        timeout_seconds=30,
    )

    prompt_builder = PromptBuilder()
    orchestrator = Orchestrator(
        runtime=runner,
        prompt_builder=prompt_builder,
    )

    user_input = "What is the capital of Vietnam?"
    response = orchestrator.handle(user_input)

    print("=== LLM RESPONSE ===")
    print(response)

if __name__ == "__main__":
    main()
