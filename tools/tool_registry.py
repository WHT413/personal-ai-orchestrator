"""
ToolRegistry — central registry for all callable tools.

Responsibilities:
- Register tools by dot-notation name (e.g. 'finance.add_expense')
- Look up a tool by name for dispatch
- List all registered tool names

Non-responsibilities:
- Tool implementation logic
- Argument validation
- Execution
"""

from typing import Callable


class ToolNotFoundError(Exception):
    """
    Raised when a requested tool name is not registered.
    """
    pass


class ToolRegistry:
    """
    Registry mapping tool names to callable functions.

    Contract:
    - Tool names follow dot-notation: '<domain>.<action>'
    - Each name maps to exactly one callable
    - Duplicate registration raises ValueError
    """

    def __init__(self) -> None:
        self._tools: dict[str, Callable] = {}

    def register(self, name: str, fn: Callable) -> None:
        """
        Register a tool function under the given name.

        Args:
            name: Dot-notation tool name (e.g. 'finance.add_expense').
            fn: Callable that implements the tool.

        Raises:
            ValueError: If the name is already registered.
        """
        if not name or not name.strip():
            raise ValueError("Tool name must be a non-empty string")
        if name in self._tools:
            raise ValueError(f"Tool already registered: {name!r}")
        self._tools[name] = fn

    def get(self, name: str) -> Callable:
        """
        Retrieve a tool function by name.

        Args:
            name: Dot-notation tool name.

        Returns:
            The registered callable.

        Raises:
            ToolNotFoundError: If the name is not registered.
        """
        if name not in self._tools:
            raise ToolNotFoundError(f"No tool registered for name: {name!r}")
        return self._tools[name]

    def list_tools(self) -> list[str]:
        """
        Return all registered tool names, sorted alphabetically.

        Returns:
            Sorted list of tool name strings.
        """
        return sorted(self._tools.keys())
