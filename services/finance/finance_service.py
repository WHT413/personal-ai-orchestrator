"""
FinanceService — business logic for personal finance tracking.

This module enforces domain rules and delegates persistence to ExpenseStorage.
LLMs, prompt logic, and orchestration concerns must NOT live here.
"""

from datetime import date as date_type
from pathlib import Path

from services.finance.models import Expense
from services.finance.storage import ExpenseStorage, StorageError


class FinanceServiceError(Exception):
    """
    Raised when a FinanceService operation fails due to invalid input
    or a storage error.
    """
    pass


class FinanceService:
    """
    Provides finance-related operations for the orchestrator's Tool Layer.

    Responsibilities:
    - Validate inputs before persistence
    - Delegate storage to ExpenseStorage
    - Filter and return expense data

    Non-responsibilities:
    - HTTP / Telegram / interface concerns
    - LLM prompt construction
    - Data serialization (handled by Expense model)
    """

    def __init__(self, storage: ExpenseStorage | None = None):
        """
        Args:
            storage: Optional ExpenseStorage instance.
                     Defaults to ExpenseStorage with the default path.
        """
        self._storage = storage or ExpenseStorage()

    def add_expense(
        self,
        amount: float,
        category: str,
        description: str,
        date: str,
    ) -> Expense:
        """
        Record a new expense.

        Contract:
        - amount must be a positive number.
        - category must be a non-empty string.
        - date must be a valid ISO 8601 date (YYYY-MM-DD).
        - Returns the persisted Expense.
        - Raises FinanceServiceError on invalid input or storage failure.

        Args:
            amount: Expense amount (positive float).
            category: Expense category label (e.g. 'food', 'transport').
            description: Free-form note about the expense.
            date: Date of the expense in YYYY-MM-DD format.

        Returns:
            The created and persisted Expense.
        """
        self._validate_amount(amount)
        self._validate_category(category)
        self._validate_date(date)

        expense = Expense(
            amount=float(amount),
            category=category.strip().lower(),
            description=description.strip(),
            date=date,
        )

        try:
            self._storage.save(expense)
        except StorageError as exc:
            raise FinanceServiceError(f"Failed to save expense: {exc}") from exc

        return expense

    def query_expenses(
        self,
        category: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[Expense]:
        """
        Query expenses with optional filters.

        Contract:
        - All filters are optional — no filter means return all.
        - category is case-insensitive.
        - date_from and date_to are inclusive bounds (YYYY-MM-DD).
        - Returns a list ordered by date ascending.
        - Raises FinanceServiceError on storage failure.

        Args:
            category: Optional category filter.
            date_from: Optional start date (inclusive), YYYY-MM-DD.
            date_to: Optional end date (inclusive), YYYY-MM-DD.

        Returns:
            Filtered, date-sorted list of Expense instances.
        """
        if date_from:
            self._validate_date(date_from)
        if date_to:
            self._validate_date(date_to)

        try:
            expenses = self._storage.load_all()
        except StorageError as exc:
            raise FinanceServiceError(f"Failed to load expenses: {exc}") from exc

        if category:
            normalized = category.strip().lower()
            expenses = [e for e in expenses if e.category == normalized]

        if date_from:
            expenses = [e for e in expenses if e.date >= date_from]

        if date_to:
            expenses = [e for e in expenses if e.date <= date_to]

        return sorted(expenses, key=lambda e: e.date)

    # ── Validation helpers ────────────────────────────────────────────────────

    @staticmethod
    def _validate_amount(amount: float) -> None:
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise FinanceServiceError("amount must be a number")
        if amount <= 0:
            raise FinanceServiceError("amount must be a positive number")

    @staticmethod
    def _validate_category(category: str) -> None:
        if not isinstance(category, str) or not category.strip():
            raise FinanceServiceError("category must be a non-empty string")

    @staticmethod
    def _validate_date(date: str) -> None:
        try:
            date_type.fromisoformat(date)
        except (ValueError, TypeError) as exc:
            raise FinanceServiceError(
                f"date must be a valid ISO 8601 date (YYYY-MM-DD), got: {date!r}"
            ) from exc
