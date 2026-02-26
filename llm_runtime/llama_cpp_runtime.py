from interfaces.llm_runtime import LLMRuntime, LLMResult, LLMRuntimeError
from llm_runtime.llama_runner import LlamaRunner, LlamaRunnerError

class LlamaCppRuntime(LLMRuntime):

    def __init__(self, runner: LlamaRunner):
        self._runner = runner

    def run(self, prompt: str) -> LLMResult:
        try:
            result = self._runner.run(prompt)

            return LLMResult(
                text=result.text,
                elapsed_ms=result.elapsed_ms,
            )

        except LlamaRunnerError as exc:
            raise LLMRuntimeError(str(exc)) from exc