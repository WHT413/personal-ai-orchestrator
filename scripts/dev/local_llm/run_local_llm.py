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

from llm_runtime.llama_cpp_runtime import LlamaCppRuntime
from llm_runtime.llama_runner import LlamaRunner
from core.prompt_builder import PromptBuilder
from core.orchestrator import Orchestrator
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--binary", required=True)
    args = parser.parse_args()

    runner = LlamaRunner(
        llama_binary_path=args.binary,
        model_path=args.model,
        context_size=2048,
        temperature=0.7,
        timeout_seconds=10,
    )

    runtime = LlamaCppRuntime(runner=runner)
    prompt_builder = PromptBuilder()
    orchestrator = Orchestrator(
        runtime=runtime,
        prompt_builder=prompt_builder,
    )

    user_input = "What is the capital of Vietnam?"
    response = orchestrator.handle(user_input)

    print("=== LLM RESPONSE ===")
    print(response)

if __name__ == "__main__":
    main()
