from abc import ABC, abstractmethod
from dataclasses import dataclass 

class LLMRuntimeError(Exception):
    """
    Raised when LLM runtime fails to produce a valid response.
    """
    pass

@dataclass(frozen=True)
class LLMResult:
    """.
    Result of a single LLM inference.

    Contract:
    - text: Final generated text
    - elapsed_ms: End-to-end latency in milliseconds
    """
    text: str
    elapsed_ms: int

class LLMRuntime(ABC):
    """
    Abstract interface for a local or remote LLM runtime.

    This interface defines the minimal capability required by the system
    to perform a single-turn inference.

    Constraints:
    - Blocking call
    - Batch size = 1
    - No streaming
    """

    @abstractmethod
    def run(self, prompt: str) -> LLMResult:
        """
        Execute one inference call.

        Args:
            prompt: Fully constructed prompt text.

        Returns:
            LLMResult

        Raises:
            LLMRuntimeError on failure.
        """
        raise NotImplementedError        





    