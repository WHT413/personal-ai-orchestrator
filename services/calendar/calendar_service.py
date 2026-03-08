"""
CalendarService — core business logic for managing events.
"""

from datetime import datetime
import uuid
from typing import List

from services.calendar.models import CalendarEvent
from services.calendar.storage import CalendarStorage


class CalendarService:
    """
    Manages CalendarEvents.
    
    Responsibilities:
    - Validate inputs.
    - Create new events.
    - Query events by date.
    - Delegate persistence to CalendarStorage.
    """

    def __init__(self, storage: CalendarStorage):
        self._storage = storage

    def create_event(
        self,
        title: str,
        date: str,
        time: str | None = None,
        description: str = "",
    ) -> CalendarEvent:
        """
        Create and persist a new calendar event.
        
        Args:
            title: Short description or name of the event.
            date: ISO 8601 date string (YYYY-MM-DD).
            time: Optional HH:MM string.
            description: Optional detailed text.
        
        Returns:
            The created CalendarEvent object.
            
        Raises:
            ValueError: If inputs are invalid.
        """
        title = title.strip()
        if not title:
            raise ValueError("Event title cannot be empty.")
            
        # Validate date string format
        try:
            datetime.fromisoformat(date).date()
        except ValueError:
            raise ValueError(f"Invalid date format: {date!r}. Expected YYYY-MM-DD.")
            
        # Validate time format if provided
        if time:
            time = time.strip()
            try:
                datetime.strptime(time, "%H:%M")
            except ValueError:
                raise ValueError(f"Invalid time format: {time!r}. Expected HH:MM.")
        else:
            time = None

        event = CalendarEvent(
            id=uuid.uuid4().hex,
            title=title,
            date=date,
            time=time,
            description=description.strip(),
            created_at=datetime.now().isoformat()
        )

        events = self._storage.load_all()
        events.append(event)
        self._storage.save_all(events)

        return event

    def list_events(self, date: str | None = None) -> List[CalendarEvent]:
        """
        List calendar events, optionally filtered by date.
        
        Args:
            date: ISO 8601 date string. If None, returns all events.
        
        Returns:
            List of events sorted by date and time.
            
        Raises:
            ValueError: If date format is invalid.
        """
        if date is not None:
            try:
                datetime.fromisoformat(date).date()
            except ValueError:
                raise ValueError(f"Invalid date filter: {date!r}. Expected YYYY-MM-DD.")

        events = self._storage.load_all()
        
        if date:
            events = [e for e in events if e.date == date]
            
        # Sort by date, then by time (putting None times at the start of the day)
        events.sort(key=lambda e: (e.date, e.time or "00:00"))
        
        return events
