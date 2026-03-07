"""Unit tests for FinanceService."""

import pytest

from services.finance.finance_service import FinanceService, FinanceServiceError
from services.finance.models import Expense
from services.finance.storage import ExpenseStorage


@pytest.fixture
def service(tmp_path):
    storage = ExpenseStorage(storage_path=tmp_path / "expenses.json")
    return FinanceService(storage=storage)


# ── add_expense ────────────────────────────────────────────────────────────────

def test_add_expense_returns_expense(service):
    expense = service.add_expense(
        amount=50000.0,
        category="food",
        description="bun bo",
        date="2026-03-07",
    )
    assert isinstance(expense, Expense)
    assert expense.amount == 50000.0
    assert expense.category == "food"
    assert expense.description == "bun bo"
    assert expense.date == "2026-03-07"


def test_add_expense_normalizes_category_to_lowercase(service):
    expense = service.add_expense(50000, "FOOD", "test", "2026-03-07")
    assert expense.category == "food"


def test_add_expense_strips_description_whitespace(service):
    expense = service.add_expense(50000, "food", "  bun bo  ", "2026-03-07")
    assert expense.description == "bun bo"


def test_add_expense_persists_to_storage(service):
    service.add_expense(100.0, "coffee", "morning", "2026-03-07")
    results = service.query_expenses()
    assert len(results) == 1


def test_add_expense_zero_amount_raises(service):
    with pytest.raises(FinanceServiceError, match="positive"):
        service.add_expense(0, "food", "test", "2026-03-07")


def test_add_expense_negative_amount_raises(service):
    with pytest.raises(FinanceServiceError, match="positive"):
        service.add_expense(-100, "food", "test", "2026-03-07")


def test_add_expense_non_numeric_amount_raises(service):
    with pytest.raises(FinanceServiceError, match="number"):
        service.add_expense("abc", "food", "test", "2026-03-07")


def test_add_expense_empty_category_raises(service):
    with pytest.raises(FinanceServiceError, match="non-empty"):
        service.add_expense(100, "  ", "test", "2026-03-07")


def test_add_expense_invalid_date_raises(service):
    with pytest.raises(FinanceServiceError, match="ISO 8601"):
        service.add_expense(100, "food", "test", "07-03-2026")


# ── query_expenses ─────────────────────────────────────────────────────────────

def test_query_expenses_returns_all_when_no_filter(service):
    service.add_expense(10.0, "food", "a", "2026-01-01")
    service.add_expense(20.0, "coffee", "b", "2026-01-02")
    results = service.query_expenses()
    assert len(results) == 2


def test_query_expenses_filters_by_category(service):
    service.add_expense(10.0, "food", "a", "2026-01-01")
    service.add_expense(20.0, "coffee", "b", "2026-01-02")
    results = service.query_expenses(category="food")
    assert len(results) == 1
    assert results[0].category == "food"


def test_query_expenses_category_filter_is_case_insensitive(service):
    service.add_expense(10.0, "food", "a", "2026-01-01")
    results = service.query_expenses(category="FOOD")
    assert len(results) == 1


def test_query_expenses_filters_by_date_from(service):
    service.add_expense(10.0, "food", "a", "2026-01-01")
    service.add_expense(20.0, "food", "b", "2026-03-01")
    results = service.query_expenses(date_from="2026-02-01")
    assert len(results) == 1
    assert results[0].date == "2026-03-01"


def test_query_expenses_filters_by_date_to(service):
    service.add_expense(10.0, "food", "a", "2026-01-01")
    service.add_expense(20.0, "food", "b", "2026-03-01")
    results = service.query_expenses(date_to="2026-01-31")
    assert len(results) == 1
    assert results[0].date == "2026-01-01"


def test_query_expenses_date_range_inclusive(service):
    service.add_expense(10.0, "food", "a", "2026-01-01")
    service.add_expense(20.0, "food", "b", "2026-01-15")
    service.add_expense(30.0, "food", "c", "2026-01-31")
    results = service.query_expenses(date_from="2026-01-01", date_to="2026-01-31")
    assert len(results) == 3


def test_query_expenses_sorted_by_date_ascending(service):
    service.add_expense(10.0, "food", "a", "2026-03-05")
    service.add_expense(20.0, "food", "b", "2026-01-01")
    service.add_expense(30.0, "food", "c", "2026-02-15")
    results = service.query_expenses()
    dates = [r.date for r in results]
    assert dates == sorted(dates)


def test_query_expenses_invalid_date_from_raises(service):
    with pytest.raises(FinanceServiceError):
        service.query_expenses(date_from="not-a-date")


def test_query_expenses_empty_returns_empty_list(service):
    results = service.query_expenses()
    assert results == []
