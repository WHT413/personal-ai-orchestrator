"""Unit tests for Calendar Event model."""

import pytest
from services.calendar.models import CalendarEvent

def test_event_to_dict():
    event = CalendarEvent(
        id="abc",
        title="meeting",
        date="2026-03-08",
        time="09:00",
        description="team sync",
        created_at="now"
    )
    data = event.to_dict()
    assert data["id"] == "abc"
    assert data["time"] == "09:00"

def test_event_from_dict():
    data = {"id": "1", "title": "A", "date": "2026-03-08", "time": "15:30", "description": "", "created_at": "ts"}
    event = CalendarEvent.from_dict(data)
    assert event.id == "1"
    assert event.time == "15:30"

def test_event_from_dict_missing_field_raises():
    with pytest.raises(ValueError, match="id"):
        CalendarEvent.from_dict({"title": "A"})
