"""
LLM Runtime implementation using the `llama-cpp-python` pip package.
"""

import time
from interfaces.llm_runtime import LLMRuntime, LLMResult, LLMRuntimeError
from llama_cpp import Llama


class LlamaCppPythonRuntime(LLMRuntime):
    """
    In-process LLM Runtime using python bindings for llama.cpp.
    Doesn't require an external compiled binary.
    """

    def __init__(self, model_path: str):
        try:
            # -1 means offloading all layers to the GPU
            self._llm = Llama(
                model_path=model_path,
                n_ctx=2048,
                n_gpu_layers=-1,
                verbose=False
            )
        except Exception as exc:
            raise LLMRuntimeError(f"Failed to load model from {model_path}: {exc}") from exc

    def run(self, prompt: str) -> LLMResult:
        start = time.time()
        try:
            response = self._llm(
                prompt,
                max_tokens=256,
                temperature=0.7,
                stop=["User:", "\n\n", "<|im_end|>"]
            )
            text = response['choices'][0]['text']
            elapsed_ms = int((time.time() - start) * 1000)
            return LLMResult(text=text.strip(), elapsed_ms=elapsed_ms)
        except Exception as exc:
            raise LLMRuntimeError(f"Inference failed: {exc}") from exc
