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

from tools.tool_registry import ToolRegistry, ToolNotFoundError


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

    def dispatch(self, intent: str, params: dict) -> dict:
        """
        Execute the tool identified by intent.

        Args:
            intent: The dot-notation name of the tool (e.g. 'finance.add_expense').
            params: The arguments to pass to the tool.

        Returns:
            Result dict returned by the tool function.

        Raises:
            DispatchError: If tool is not found or execution fails.
        """
        try:
            fn = self._registry.get(intent)
        except ToolNotFoundError as exc:
            raise DispatchError(f"Tool not found: {intent!r}") from exc

        try:
            result = fn(**params)
        except Exception as exc:
            raise DispatchError(
                f"Tool {intent!r} raised an error: {exc}"
            ) from exc

        if not isinstance(result, dict):
            raise DispatchError(
                f"Tool {intent!r} must return a dict, got {type(result).__name__}"
            )

        return result
