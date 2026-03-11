from dataclasses import dataclass
from typing import Optional
import subprocess
import time
import os


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
        timeout_seconds: int = 300,
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
        self._llama_binary_path = os.path.expanduser(llama_binary_path)
        self._model_path = os.path.expanduser(model_path)
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

        # Build command — keep -p at the very end so all flags are parsed first
        cmd = [
            self._llama_binary_path,
            "-m", self._model_path,
            "-c", str(self._context_size),
            "--temp", str(self._temperature),
            "--n-predict", "256",
            "--no-display-prompt",
            "-no-cnv",
        ]

        if self._gpu_layers != 0:
            cmd.extend(["-ngl", str(self._gpu_layers)])

        cmd.extend(["-p", prompt])

        try:
            env = os.environ.copy()
            if self._gpu_layers == 0:
                env["CUDA_VISIBLE_DEVICES"] = ""

            process = subprocess.run(
                cmd,
                stdin=subprocess.DEVNULL,   # EOF → llama-cli exits after n-predict
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                env=env,
                start_new_session=True,     # detach from controlling tty so
                                            # llama-cli's interactive UI has no
                                            # terminal to write > prompts to
            )
        except subprocess.TimeoutExpired as exc:
            raise LlamaRunnerError("llama.cpp execution timed out") from exc
        except Exception as exc:
            raise LlamaRunnerError(f"Failed to execute llama.cpp: {exc}") from exc

        elapsed_ms = int((time.time() - start_time) * 1000)

        if process.returncode != 0:
            raise LlamaRunnerError(
                f"llama.cpp exited with code {process.returncode}\n"
                f"stderr: {process.stderr}"
            )

        raw_output = process.stdout

        # Strip echoed prompt in case --no-display-prompt didn't fully suppress it.
        generated_text = raw_output.replace(prompt, "", 1).strip()

        if not generated_text:
            raise LlamaRunnerError("llama.cpp produced no output")

        return LlamaRunResult(
            text=generated_text,
            elapsed_ms=elapsed_ms,
            exit_code=exit_code,
            raw_output=raw_output,
        )