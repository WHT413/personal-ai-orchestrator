"""Unit tests for Calendar Storage."""

import pytest
import os
import pathlib
import json

from services.calendar.models import CalendarEvent
from services.calendar.storage import CalendarStorage, CalendarStorageError


@pytest.fixture
def storage(tmp_path):
    return CalendarStorage(tmp_path / "events.json")


def test_load_all_returns_empty_when_file_missing(storage):
    assert storage.load_all() == []


def test_save_and_load_events(storage):
    event = CalendarEvent("1", "Daily Standup", "2026-03-08", "09:30", "", "now")
    storage.save_all([event])
    
    loaded = storage.load_all()
    assert len(loaded) == 1
    assert loaded[0].id == "1"
    assert loaded[0].title == "Daily Standup"
    assert loaded[0].time == "09:30"


def test_load_raises_storage_error_on_corrupt_file(storage, tmp_path):
    file_path = tmp_path / "events.json"
    file_path.write_text("{not valid json}")
    with pytest.raises(CalendarStorageError, match="Corrupt JSON"):
        storage.load_all()


def test_save_creates_missing_directories(tmp_path):
    deep_path = tmp_path / "nested" / "dir" / "events.json"
    store = CalendarStorage(deep_path)
    store.save_all([])
    assert deep_path.exists()
