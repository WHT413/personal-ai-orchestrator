"""
Prompt construction utilities.

PromptBuilder       — single-turn, tool-unaware (conversational baseline)
ToolAwarePromptBuilder — includes tool catalog in system prompt, instructs
                         LLM to emit TOOL_CALL when appropriate
"""


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
        Args:
            system_prompt: Optional custom system instruction. Defaults to DEFAULT_SYSTEM_INSTRUCTION.
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


class ToolAwarePromptBuilder(PromptBuilder):
    """
    Extends PromptBuilder with a tool catalog injected into the system prompt.

    When the user's request maps to a known tool, the LLM must respond with:

        TOOL_CALL: {"tool": "<name>", "args": {<key>: <value>}}

    If no tool applies, respond normally in plain text.

    Non-responsibilities:
    - Tool registration or lookup
    - Argument validation
    """

    _TOOL_INSTRUCTION = (
        "You have access to the following tools. "
        "When the user's request requires a tool, respond ONLY with this exact format "
        "and nothing else:\n"
        "TOOL_CALL: {{\"tool\": \"<tool_name>\", \"args\": {{<key>: <value>}}}}\n\n"
        "Available tools:\n"
        "{tool_descriptions}\n\n"
        "If no tool is needed, respond normally in plain text."
    )

    def __init__(self, tool_descriptions: list[str], system_prompt: str | None = None) -> None:
        """
        Args:
            tool_descriptions: List of strings describing each tool.
                               e.g. ['finance.add_expense(amount, category, description, date)']
            system_prompt: Optional base system instruction.
        """
        tool_block = "\n".join(f"- {desc}" for desc in tool_descriptions)
        instruction = self._TOOL_INSTRUCTION.format(tool_descriptions=tool_block)
        combined = f"{system_prompt or self.DEFAULT_SYSTEM_INSTRUCTION}\n\n{instruction}"
        super().__init__(system_prompt=combined)
