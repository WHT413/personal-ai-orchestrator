class PromptBuilder:
    """
    Build a deterministic prompt for a single-turn LLM inference.

    Responsibilities:
    - Combine system instructions and user input
    - Produce a single prompt string

    Non-responsibilities:
    - Calling the LLM
    - Managing conversation state
    - Handling retries or errors
    """

    DEFAULT_SYSTEM_INSTRUCTION = (
        "You are a helpful, concise, and accurate assistant. "
        "Answer the user's question clearly and directly."
    )

    def __init__(self, system_prompt: str | None = None):
        """
        Initialize the prompt builder.

        Args:
            system_prompt: Optional custom system instruction. If None, a default will be used.
        """
        self._system_prompt = system_prompt or self.DEFAULT_SYSTEM_INSTRUCTION

    def build(self, user_input: str) -> str:
        """
        Build the final prompt string.

        Contract:
        - Deterministic output for the same input
        - No side effects

        Args:
            user_input: Raw user input text.

        Returns:
            Final prompt string.
        """
        if not user_input or not user_input.strip():
            raise ValueError("user_input must be a non-empty string")

        return (
            f"System: {self._system_prompt}\n\n"
            f"User: {user_input.strip()}\n\n"
            f"Assistant:\n"
        )



