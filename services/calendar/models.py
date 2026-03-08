"""
Domain model for Calendar events.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class CalendarEvent:
    """
    Represents a scheduled event or task.
    
    Attributes:
        id: Unique identifier for the event.
        title: Short description or name of the event.
        date: ISO 8601 date string (YYYY-MM-DD).
        time: Optional HH:MM string.
        description: Optional longer text details.
        created_at: ISO 8601 timestamp.
    """
    id: str
    title: str
    date: str
    time: Optional[str]
    description: str
    created_at: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date,
            "time": self.time,
            "description": self.description,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CalendarEvent":
        try:
            return cls(
                id=data["id"],
                title=data["title"],
                date=data["date"],
                time=data.get("time"),
                description=data.get("description", ""),
                created_at=data["created_at"],
            )
        except KeyError as exc:
            missing_key = exc.args[0]
            raise ValueError(f"Missing required field in event data: {missing_key!r}")
