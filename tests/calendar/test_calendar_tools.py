"""Unit tests for CalendarTools."""

import pytest
from unittest.mock import MagicMock

from services.calendar.models import CalendarEvent
from services.calendar.calendar_service import CalendarService
from tools.calendar.calendar_tools import CalendarTools


@pytest.fixture
def mock_service():
    service = MagicMock(spec=CalendarService)
    return service

@pytest.fixture
def tools(mock_service):
    return CalendarTools(mock_service)


def test_create_event_tool_success(tools, mock_service):
    # Setup mock
    mock_event = CalendarEvent("abc", "Team Sync", "2026-03-10", "15:00", "", "now")
    mock_service.create_event.return_value = mock_event
    
    # Call tool
    result = tools.create_event("tạo lịch họp team", date="2026-03-10", time="15:00")
    
    assert result["status"] == "success"
    assert result["event"]["id"] == "abc"
    assert result["event"]["title"] == "Team Sync"
    
    # Verify service call
    mock_service.create_event.assert_called_once_with(
        title="tạo lịch họp team",
        date="2026-03-10",
        time="15:00",
        description=""
    )

def test_create_event_tool_validation_error(tools, mock_service):
    mock_service.create_event.side_effect = ValueError("Invalid time")
    
    result = tools.create_event("lịch lỗi", date="2026-03-10", time="60:00")
    
    assert result["status"] == "error"
    assert "Invalid time" in result["message"]

def test_create_event_tool_defaults_date(tools, mock_service):
    from datetime import date
    
    mock_service.create_event.return_value = CalendarEvent("x", "y", "2026-03-08", None, "z", "now")
    
    # Intentionally missing date/time kwargs
    tools.create_event("meeting")
    
    call_kwargs = mock_service.create_event.call_args[1]
    assert call_kwargs["title"] == "meeting"
    assert call_kwargs["date"] == date.today().isoformat()
    assert call_kwargs["time"] is None


def test_list_events_tool_success(tools, mock_service):
    mock_event = CalendarEvent("1", "A", "2026-03-10", None, "", "now")
    mock_service.list_events.return_value = [mock_event]
    
    result = tools.list_events("xem lịch", date="2026-03-10")
    
    assert result["status"] == "success"
    assert result["date"] == "2026-03-10"
    assert len(result["events"]) == 1
    assert result["events"][0]["id"] == "1"
    
    mock_service.list_events.assert_called_once_with(date="2026-03-10")

def test_list_events_tool_validation_error(tools, mock_service):
    mock_service.list_events.side_effect = ValueError("Invalid date")
    
    result = tools.list_events("xem lịch", date="bad-date")
    assert result["status"] == "error"
    assert "Invalid date" in result["message"]

def test_list_events_tool_defaults_date(tools, mock_service):
    from datetime import date
    
    mock_service.list_events.return_value = []
    
    tools.list_events("xem lịch hôm nay")
    
    mock_service.list_events.assert_called_once_with(date=date.today().isoformat())
