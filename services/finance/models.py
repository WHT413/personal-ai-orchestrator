"""
Domain model for the Finance service.

This module defines the core data structure for expense entries.
No business logic lives here — this is a pure data model.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class Expense:
    """
    Represents a single expense entry.

    Contract:
    - id: Unique identifier (UUID v4), auto-generated if not provided.
    - amount: Positive float value in the user's local currency.
    - category: Non-empty string describing the expense category (e.g. 'food', 'transport').
    - description: Human-readable note about the expense.
    - date: The date the expense occurred, ISO 8601 format (YYYY-MM-DD).
    - created_at: Timestamp when the record was created, ISO 8601 with UTC timezone.
    """

    amount: float
    category: str
    description: str
    date: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        """
        Serialize the Expense to a plain dictionary.

        Returns:
            dict representation suitable for JSON serialization.
        """
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Expense":
        """
        Deserialize an Expense from a plain dictionary.

        Args:
            data: Dictionary previously produced by to_dict().

        Returns:
            Expense instance.

        Raises:
            KeyError: If required fields are missing.
        """
        return cls(
            id=data["id"],
            amount=data["amount"],
            category=data["category"],
            description=data["description"],
            date=data["date"],
            created_at=data["created_at"],
        )
