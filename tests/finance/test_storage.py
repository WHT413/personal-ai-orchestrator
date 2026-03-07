"""Unit tests for ExpenseStorage."""

import json
import pytest
from pathlib import Path

from services.finance.models import Expense
from services.finance.storage import ExpenseStorage, StorageError


@pytest.fixture
def storage(tmp_path):
    return ExpenseStorage(storage_path=tmp_path / "expenses.json")


@pytest.fixture
def sample_expense():
    return Expense(
        amount=75000.0,
        category="food",
        description="pho",
        date="2026-03-07",
    )


def test_load_all_returns_empty_when_file_missing(storage):
    result = storage.load_all()
    assert result == []


def test_save_and_load_single_expense(storage, sample_expense):
    storage.save(sample_expense)
    loaded = storage.load_all()

    assert len(loaded) == 1
    assert loaded[0].id == sample_expense.id
    assert loaded[0].amount == sample_expense.amount
    assert loaded[0].category == sample_expense.category


def test_save_multiple_expenses(storage):
    e1 = Expense(amount=10.0, category="coffee", description="c1", date="2026-01-01")
    e2 = Expense(amount=20.0, category="food", description="c2", date="2026-01-02")

    storage.save(e1)
    storage.save(e2)

    loaded = storage.load_all()
    assert len(loaded) == 2


def test_save_creates_missing_directories(tmp_path):
    nested_path = tmp_path / "a" / "b" / "c" / "expenses.json"
    storage = ExpenseStorage(storage_path=nested_path)
    expense = Expense(amount=1.0, category="test", description="d", date="2026-01-01")

    storage.save(expense)

    assert nested_path.exists()


def test_load_raises_storage_error_on_corrupt_file(tmp_path):
    path = tmp_path / "expenses.json"
    path.write_text("not valid json", encoding="utf-8")

    storage = ExpenseStorage(storage_path=path)

    with pytest.raises(StorageError):
        storage.load_all()


def test_round_trip_preserves_all_fields(storage, sample_expense):
    storage.save(sample_expense)
    loaded = storage.load_all()[0]

    assert loaded.id == sample_expense.id
    assert loaded.amount == sample_expense.amount
    assert loaded.category == sample_expense.category
    assert loaded.description == sample_expense.description
    assert loaded.date == sample_expense.date
    assert loaded.created_at == sample_expense.created_at
