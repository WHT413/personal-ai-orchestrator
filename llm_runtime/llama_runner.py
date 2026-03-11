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
        n_predict: int = 2048,
    ):
        self._llama_binary_path = os.path.expanduser(llama_binary_path)
        self._model_path = os.path.expanduser(model_path)
        self._context_size = context_size
        self._gpu_layers = gpu_layers
        self._temperature = temperature
        self._timeout_seconds = timeout_seconds
        self._n_predict = n_predict

    def run(self, prompt: str) -> LlamaRunResult:
        """
        Run a single inference with batch size = 1.
        """
        start_time = time.time()

        # Build command — keep -p at the very end so all flags are parsed first
        # NOTE: use llama-completion binary; llama-cli (b8119+) is interactive-only
        # and does not support -no-cnv / --no-conversation.
        cmd = [
            self._llama_binary_path,
            "-m", self._model_path,
            "-c", str(self._context_size),
            "--temp", str(self._temperature),
            "--n-predict", str(self._n_predict),
            "--no-display-prompt",
            "-no-cnv",
            "--single-turn",
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
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                env=env,
                start_new_session=True,
            )
        except subprocess.TimeoutExpired as exc:
            elapsed_ms = int((time.time() - start_time) * 1000)
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
            exit_code=process.returncode,
            raw_output=raw_output,
        )