"""
ToolDispatcher — execute a parsed tool call via the ToolRegistry.

Responsibilities:
- Look up the tool in the registry
- Execute it with the provided arguments
- Return the result dict

Non-responsibilities:
- Parsing LLM output (handled by IntentParser)
- Tool implementation (handled by tool modules)
- Argument type-casting
"""

from core.tool_registry import ToolRegistry, ToolNotFoundError
from core.intent_parser import ToolCall


class DispatchError(Exception):
    """
    Raised when tool dispatch fails — either tool not found or tool execution error.
    """
    pass


class ToolDispatcher:
    """
    Execute tool calls resolved via ToolRegistry.

    Contract:
    - dispatch() always returns a dict on success
    - Raises DispatchError on any failure (not found, execution error)
    """

    def __init__(self, registry: ToolRegistry) -> None:
        """
        Args:
            registry: Populated ToolRegistry instance.
        """
        self._registry = registry

    def dispatch(self, tool_call: ToolCall) -> dict:
        """
        Execute the tool identified in tool_call.

        Args:
            tool_call: A ToolCall produced by IntentParser.

        Returns:
            Result dict returned by the tool function.

        Raises:
            DispatchError: If tool is not found or execution fails.
        """
        try:
            fn = self._registry.get(tool_call.tool)
        except ToolNotFoundError as exc:
            raise DispatchError(f"Tool not found: {tool_call.tool!r}") from exc

        try:
            result = fn(**tool_call.args)
        except Exception as exc:
            raise DispatchError(
                f"Tool {tool_call.tool!r} raised an error: {exc}"
            ) from exc

        if not isinstance(result, dict):
            raise DispatchError(
                f"Tool {tool_call.tool!r} must return a dict, got {type(result).__name__}"
            )

        return result
