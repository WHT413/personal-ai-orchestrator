"""Unit tests for the Expense domain model."""

import pytest
from services.finance.models import Expense


def test_expense_creation_with_required_fields():
    expense = Expense(
        amount=50000.0,
        category="food",
        description="bun bo",
        date="2026-03-07",
    )
    assert expense.amount == 50000.0
    assert expense.category == "food"
    assert expense.description == "bun bo"
    assert expense.date == "2026-03-07"
    assert expense.id is not None
    assert expense.created_at is not None


def test_expense_id_is_unique():
    e1 = Expense(amount=1.0, category="food", description="a", date="2026-01-01")
    e2 = Expense(amount=1.0, category="food", description="a", date="2026-01-01")
    assert e1.id != e2.id


def test_expense_to_dict():
    expense = Expense(
        id="test-id",
        amount=100.0,
        category="transport",
        description="grab",
        date="2026-03-01",
        created_at="2026-03-01T00:00:00+00:00",
    )
    d = expense.to_dict()
    assert d == {
        "id": "test-id",
        "amount": 100.0,
        "category": "transport",
        "description": "grab",
        "date": "2026-03-01",
        "created_at": "2026-03-01T00:00:00+00:00",
    }


def test_expense_from_dict_round_trip():
    original = Expense(
        amount=200.0,
        category="coffee",
        description="highlands",
        date="2026-03-05",
    )
    restored = Expense.from_dict(original.to_dict())
    assert restored.id == original.id
    assert restored.amount == original.amount
    assert restored.category == original.category
    assert restored.description == original.description
    assert restored.date == original.date
    assert restored.created_at == original.created_at


def test_expense_from_dict_missing_key_raises():
    with pytest.raises(KeyError):
        Expense.from_dict({"amount": 100.0})
