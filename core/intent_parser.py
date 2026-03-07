"""
IntentParser — extract structured tool calls from LLM text output.

The LLM is instructed to emit a tool call in the following format
when it determines a tool must be invoked:

    TOOL_CALL: {"tool": "<name>", "args": {<key>: <value>, ...}}

If the LLM responds with plain text (no tool call), the parser returns None,
signalling the Orchestrator to use the text as a conversational response.

Non-responsibilities:
- Validating that the tool exists
- Executing the tool
"""

import json
from dataclasses import dataclass, field


TOOL_CALL_PREFIX = "TOOL_CALL:"


class ParseError(Exception):
    """
    Raised when a TOOL_CALL prefix is found but the JSON is malformed.
    """
    pass


@dataclass
class ToolCall:
    """
    Represents a parsed tool invocation request from LLM output.

    Attributes:
        tool: Dot-notation tool name (e.g. 'finance.add_expense').
        args: Dictionary of arguments to pass to the tool.
    """
    tool: str
    args: dict = field(default_factory=dict)


class IntentParser:
    """
    Parse structured tool calls from LLM output.

    Contract:
    - Returns a ToolCall if TOOL_CALL prefix is found and JSON is valid.
    - Returns None if no TOOL_CALL prefix is present.
    - Raises ParseError if prefix is found but content is malformed.
    """

    def parse(self, llm_output: str) -> ToolCall | None:
        """
        Parse LLM output and extract a tool call if present.

        Args:
            llm_output: Raw text produced by the LLM.

        Returns:
            ToolCall if a valid tool call was found, None otherwise.

        Raises:
            ParseError: If TOOL_CALL prefix exists but JSON is malformed.
        """
        text = llm_output.strip()

        # Find the TOOL_CALL prefix anywhere in the output
        # (LLM may prepend reasoning text before the call)
        prefix_index = text.find(TOOL_CALL_PREFIX)
        if prefix_index == -1:
            return None

        raw_json = text[prefix_index + len(TOOL_CALL_PREFIX):].strip()

        try:
            payload = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            raise ParseError(
                f"TOOL_CALL found but JSON is invalid: {exc}\nRaw: {raw_json!r}"
            ) from exc

        if not isinstance(payload, dict):
            raise ParseError(f"TOOL_CALL payload must be a JSON object, got: {type(payload)}")

        tool_name = payload.get("tool")
        if not tool_name or not isinstance(tool_name, str):
            raise ParseError("TOOL_CALL payload missing required string field 'tool'")

        args = payload.get("args", {})
        if not isinstance(args, dict):
            raise ParseError(f"TOOL_CALL 'args' must be a JSON object, got: {type(args)}")

        return ToolCall(tool=tool_name, args=args)
