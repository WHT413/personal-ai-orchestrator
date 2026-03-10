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
        timeout_seconds=20,
    )

    runtime = LlamaCppRuntime(runner=runner)

    prompt = (
        "System: You are a helpful assistant.\n\n"
        "User: Why is the sky blue?\n\n"
        "Assistant:\n"
    )
    result = runtime.run(prompt)

    print("=== LLM RESPONSE ===")
    print(result.text)
    print(f"(elapsed: {result.elapsed_ms}ms)")

if __name__ == "__main__":
    main()
