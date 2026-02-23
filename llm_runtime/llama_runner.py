from dataclasses import dataclass
from typing import Optional
import subprocess
import time


class LlamaRunnerError(Exception):
    """
    Raised when llama.cpp execution fails or times out.
    """
    pass


@dataclass
class LlamaRunResult:
    """
    Result of a single LLM inference run.

    Contract:
    - text: Final generated text (already post-processed).
    - elapsed_ms: Total wall-clock time in milliseconds.
    - exit_code: Process exit code from llama.cpp.
    - raw_output: Full raw stdout for debugging or future parsing.
    """
    text: str
    elapsed_ms: int
    exit_code: int
    raw_output: str


class LlamaRunner:
    """
    Boundary wrapper around llama.cpp runtime.

    This class is responsible for:
    - Spawning llama.cpp as a subprocess
    - Enforcing timeout and resource control
    - Returning a structured inference result

    It must NOT:
    - Contain business logic
    - Perform prompt templating beyond minimal concatenation
    """

    def __init__(
        self,
        llama_binary_path: str,
        model_path: str,
        context_size: int = 4096,
        gpu_layers: int = -1,
        temperature: float = 0.7,
        timeout_seconds: int = 30,
    ):
        """
        Initialize runner configuration.

        Args:
            llama_binary_path: Path to llama.cpp executable.
            model_path: Path to GGUF model file.
            context_size: Max context length.
            gpu_layers: Number of layers offloaded to GPU (-1 = all).
            temperature: Sampling temperature.
            timeout_seconds: Hard timeout for a single inference call.
        """
        self._llama_binary_path = llama_binary_path
        self._model_path = model_path
        self._context_size = context_size
        self._gpu_layers = gpu_layers
        self._temperature = temperature
        self._timeout_seconds = timeout_seconds

    def run(self, prompt: str) -> LlamaRunResult:
        """
        Run a single inference with batch size = 1.

        Contract:
        - Blocking call
        - One prompt in, one completion out
        - Raises LlamaRunnerError on failure or timeout

        Args:
            prompt: Fully prepared prompt text.

        Returns:
            LlamaRunResult
        """
        start_time = time.time()

        # TODO: build llama.cpp command arguments
        cmd = []

        try:
            # TODO: invoke subprocess with stdout capture
            process = subprocess.run(
                cmd,
                input=prompt,
                text=True,
                capture_output=True,
                timeout=self._timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise LlamaRunnerError("llama.cpp execution timed out") from exc
        except Exception as exc:
            raise LlamaRunnerError("Failed to execute llama.cpp") from exc

        elapsed_ms = int((time.time() - start_time) * 1000)

        if process.returncode != 0:
            raise LlamaRunnerError(
                f"llama.cpp exited with code {process.returncode}"
            )

        # TODO: parse model output from stdout
        generated_text = ""

        return LlamaRunResult(
            text=generated_text,
            elapsed_ms=elapsed_ms,
            exit_code=process.returncode,
            raw_output=process.stdout,
        )