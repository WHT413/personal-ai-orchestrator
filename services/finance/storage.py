"""
JSON-file-based persistence for Expense records.

This module handles all I/O for finance data.
Business logic must NOT live here.

Storage format:
  data/finance/expenses.json — a flat JSON array of Expense dicts.
"""

import json
import os
from pathlib import Path

from services.finance.models import Expense


class StorageError(Exception):
    """
    Raised when a storage read or write operation fails.
    """
    pass


class ExpenseStorage:
    """
    Persist and load Expense records from a local JSON file.

    Contract:
    - All writes are atomic (write-to-tmp then rename).
    - The storage file and parent directories are created automatically.
    - Raises StorageError on any I/O failure.

    Non-responsibilities:
    - Business validation
    - Querying / filtering (return the full list, let the service filter)
    """

    DEFAULT_PATH = Path("data/finance/expenses.json")

    def __init__(self, storage_path: Path | None = None):
        """
        Args:
            storage_path: Path to the JSON file. Defaults to DEFAULT_PATH.
        """
        self._path = Path(storage_path) if storage_path else self.DEFAULT_PATH

    def save(self, expense: Expense) -> None:
        """
        Append a single expense to the storage file.

        Args:
            expense: A fully-constructed Expense instance.

        Raises:
            StorageError: On I/O failure.
        """
        try:
            expenses = self.load_all()
            expenses.append(expense)
            self._write(expenses)
        except StorageError:
            raise
        except Exception as exc:
            raise StorageError(f"Failed to save expense: {exc}") from exc

    def load_all(self) -> list[Expense]:
        """
        Load all expenses from the storage file.

        Returns:
            List of Expense instances. Empty list if file does not exist.

        Raises:
            StorageError: On I/O or parse failure.
        """
        if not self._path.exists():
            return []

        try:
            raw = self._path.read_text(encoding="utf-8")
            data = json.loads(raw)
            return [Expense.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError) as exc:
            raise StorageError(f"Failed to parse storage file: {exc}") from exc
        except Exception as exc:
            raise StorageError(f"Failed to read storage file: {exc}") from exc

    def _write(self, expenses: list[Expense]) -> None:
        """
        Write the full list of expenses to disk atomically.

        Args:
            expenses: List of Expense instances to persist.
        """
        self._path.parent.mkdir(parents=True, exist_ok=True)

        tmp_path = self._path.with_suffix(".tmp")
        payload = json.dumps(
            [e.to_dict() for e in expenses],
            ensure_ascii=False,
            indent=2,
        )

        try:
            tmp_path.write_text(payload, encoding="utf-8")
            os.replace(tmp_path, self._path)
        except Exception as exc:
            raise StorageError(f"Failed to write storage file: {exc}") from exc
