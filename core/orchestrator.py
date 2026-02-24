from interfaces.llm_runtime import LLMRuntime, LLMRuntimeError
from core.prompt_builder import PromptBuilder

class OrchestratorError(Exception):
    """
    Raised when the orchestrator fails.
    """
    pass

class Orchestrator:
    """
    Coordinate prompt building and LLM execution.

    Responsibilities:
    - Accept user input
    - Build prompt via PromptBuilder
    - Execute LLM runtime
    - Return final text output

    Non-responsibilities:
    - LLM implementation details
    - Prompt strategy logic
    - Retry or fallback policies
    """

    def __init__(self, runtime: LLMRuntime, prompt_builder: PromptBuilder):
        self._runtime = runtime
        self._prompt_builder = prompt_builder

    def handle(self, user_input: str) -> str:
        """
        Handle a single user request.

        Contract:
        - One input, one output
        - Blocking call
        - Raises OrchestratorError on failure

        Args:
            user_input: Raw user input text.

        Returns:
            Final response text.
        """
        try:
            prompt = self._prompt_builder.build(user_input)
            result = self._runtime.run(prompt)
            return result.text
        except LLMRuntimeError as exc:
            raise OrchestratorError("LLM runtime failed") from exc
        except Exception as exc:
            raise OrchestratorError("Unexpected error in orchestrator") from exc

