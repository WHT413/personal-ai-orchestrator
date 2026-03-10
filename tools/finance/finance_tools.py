"""
Finance tool wrappers for the Orchestrator's Tool Layer.

These functions are thin, JSON-serializable wrappers over FinanceService.
They represent the public tool interface exposed to the Orchestrator.

Tool naming convention:
  finance.add_expense
  finance.query_expenses

Contract:
- All functions accept primitive types only (str, float, int, None).
- All functions return plain dict — no domain objects cross the tool boundary.
- Raises ToolError on failure.
"""

from services.finance.finance_service import FinanceService, FinanceServiceError


class ToolError(Exception):
    """
    Raised when a tool execution fails.
    """
    pass


class FinanceTools:
    """
    Wraps FinanceService methods into flat, dict-returning tool functions.
    """

    def __init__(self, service: FinanceService):
        self._service = service

    def add_expense(
        self,
        user_input: str | None = None,
        amount: float = 0.0,
        category: str = "",
        description: str = "",
        date: str = "",
        **kwargs
    ) -> dict:
        """
        Tool: finance.add_expense

        Record a new expense and return the persisted record.

        Args:
            amount: Expense amount (positive number).
            category: Category label (e.g. 'food', 'transport').
            description: Free-form note.
            date: Date in YYYY-MM-DD format.

        Returns:
            dict with keys: id, amount, category, description, date, created_at.

        Raises:
            ToolError: On validation or storage failure.
        """
        if not category: category = "other"
        if not description and user_input: description = user_input
        if not date:
            from datetime import date as dt_date
            date = dt_date.today().isoformat()

        try:
            expense = self._service.add_expense(
                amount=amount,
                category=category,
                description=description,
                date=date,
            )
            return expense.to_dict()
        except FinanceServiceError as exc:
            raise ToolError(str(exc)) from exc


    def query_expenses(
        self,
        user_input: str | None = None,
        category: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        **kwargs
    ) -> dict:
        """
        Tool: finance.query_expenses

        Query recorded expenses with optional filters.

        Args:
            category: Optional category filter (case-insensitive).
            date_from: Optional start date (inclusive), YYYY-MM-DD.
            date_to: Optional end date (inclusive), YYYY-MM-DD.

        Returns:
            dict with key 'expenses' containing a list of expense dicts.

        Raises:
            ToolError: On storage or validation failure.
        """
        try:
            expenses = self._service.query_expenses(
                category=category,
                date_from=date_from,
                date_to=date_to,
            )
            return {"expenses": [e.to_dict() for e in expenses]}
        except FinanceServiceError as exc:
            raise ToolError(str(exc)) from exc
