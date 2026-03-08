"""Unit tests for CalendarService."""

import pytest
from datetime import date
from unittest.mock import MagicMock

from services.calendar.models import CalendarEvent
from services.calendar.storage import CalendarStorage
from services.calendar.calendar_service import CalendarService


@pytest.fixture
def mock_storage():
    storage = MagicMock(spec=CalendarStorage)
    storage.load_all.return_value = []
    return storage


@pytest.fixture
def service(mock_storage):
    return CalendarService(mock_storage)


def test_create_event_success(service, mock_storage):
    event = service.create_event(
        title="Team Sync",
        date="2026-03-10",
        time="10:00",
        description="Weekly sync call"
    )
    assert event.title == "Team Sync"
    assert event.date == "2026-03-10"
    assert event.time == "10:00"
    
    mock_storage.save_all.assert_called_once()
    saved_list = mock_storage.save_all.call_args[0][0]
    assert len(saved_list) == 1
    assert saved_list[0].id == event.id


def test_create_event_empty_title_raises(service):
    with pytest.raises(ValueError, match="empty"):
        service.create_event(title="   ", date="2026-03-10")


def test_create_event_invalid_date_raises(service):
    with pytest.raises(ValueError, match="Invalid date format"):
        service.create_event(title="Sync", date="10-03-2026")


def test_create_event_invalid_time_raises(service):
    with pytest.raises(ValueError, match="Invalid time format"):
        service.create_event(title="Sync", date="2026-03-10", time="25:00")


def test_list_events_no_filter_returns_all_sorted(service, mock_storage):
    ev1 = CalendarEvent("1", "A", "2026-03-10", "15:00", "", "now")
    ev2 = CalendarEvent("2", "B", "2026-03-09", None, "", "now")
    ev3 = CalendarEvent("3", "C", "2026-03-10", "09:00", "", "now")
    
    # Store unsorted
    mock_storage.load_all.return_value = [ev1, ev2, ev3]
    
    results = service.list_events()
    assert len(results) == 3
    # Expected sort: ev2 (09th), ev3 (10th 09:00), ev1 (10th 15:00)
    assert results[0].id == "2"
    assert results[1].id == "3"
    assert results[2].id == "1"


def test_list_events_with_date_filter(service, mock_storage):
    ev1 = CalendarEvent("1", "A", "2026-03-10", "15:00", "", "now")
    ev2 = CalendarEvent("2", "B", "2026-03-09", None, "", "now")
    mock_storage.load_all.return_value = [ev1, ev2]
    
    results = service.list_events(date="2026-03-10")
    assert len(results) == 1
    assert results[0].id == "1"


def test_list_events_invalid_date_raises(service):
    with pytest.raises(ValueError, match="Invalid date filter"):
        service.list_events(date="2026/03/10")
