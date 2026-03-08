"""
JSON-based storage for Calendar events.
"""
import json
import os
import pathlib
from typing import List

from services.calendar.models import CalendarEvent


class CalendarStorageError(Exception):
    """Raised when storage operations fail."""
    pass


class CalendarStorage:
    """
    Persistence layer for CalendarEvents.
    
    Responsibilities:
    - Read/write events to a JSON file.
    - Ensure atomic writes.
    - Handle missing files gracefully.
    """

    def __init__(self, data_file: str | pathlib.Path):
        self._file = pathlib.Path(data_file)

    def load_all(self) -> List[CalendarEvent]:
        """Load all events from disk."""
        if not self._file.exists():
            return []

        try:
            with open(self._file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise CalendarStorageError("Root of JSON must be a list.")
                
            return [CalendarEvent.from_dict(item) for item in data]
        except json.JSONDecodeError as exc:
            raise CalendarStorageError(f"Corrupt JSON file: {exc}") from exc
        except Exception as exc:
            raise CalendarStorageError(f"Failed to read events: {exc}") from exc

    def save_all(self, events: List[CalendarEvent]) -> None:
        """Save all events to disk atomically."""
        self._file.parent.mkdir(parents=True, exist_ok=True)
        tmp_file = self._file.with_suffix(".json.tmp")

        try:
            data = [ev.to_dict() for ev in events]
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            os.replace(tmp_file, self._file)
        except Exception as exc:
            if tmp_file.exists():
                tmp_file.unlink()
            raise CalendarStorageError(f"Failed to save events: {exc}") from exc
