"""
Calendar Tools — wrapper functions exposing CalendarService to the Orchestrator.
"""

from services.calendar.calendar_service import CalendarService


class CalendarTools:
    """
    Wraps CalendarService methods into flat, dict-returning tool functions.
    
    Responsibilities:
    - Receive flat primitive arguments (from IntentRouter/user).
    - Call the underlying CalendarService domain logic.
    - Return plain dictionaries (JSON-serializable).
    - Extract fields implicitly from raw user_input if needed.
    """

    def __init__(self, service: CalendarService):
        self._service = service

    def create_event(self, user_input: str, **kwargs) -> dict:
        """
        Creates a new calendar event.
        
        Args:
            user_input: Raw text passed from IntentRouter.
            **kwargs: Can contain pre-extracted 'date' and 'time' if implemented.
            
        Returns:
            Dict containing the created event or error.
        """
        # Feature extraction heuristic (very simple for Phase 1 deterministic)
        # Since IntentRouter doesn't perfectly extract title/description, 
        # we will use the raw text minus the date part if we can, or just save the whole text.
        date = kwargs.get("date")
        time = kwargs.get("time")
        
        # If no date provided in kwargs, default to today
        if not date:
            from datetime import date as dt_date
            date = dt_date.today().isoformat()
            
        try:
            event = self._service.create_event(
                title=user_input.strip(),  # Use the raw input as the event title for now
                date=date,
                time=time,
                description=""
            )
            return {"status": "success", "event": event.to_dict()}
        except ValueError as exc:
            return {"status": "error", "message": str(exc)}

    def list_events(self, user_input: str, **kwargs) -> dict:
        """
        Lists events for a given date.
        
        Args:
            user_input: Raw text passed from IntentRouter.
            **kwargs: Can contain pre-extracted 'date'.
        
        Returns:
            Dict containing the list of events or error.
        """
        date = kwargs.get("date")
        
        # Default to today if not provided
        if not date:
            from datetime import date as dt_date
            date = dt_date.today().isoformat()
            
        try:
            events = self._service.list_events(date=date)
            return {
                "status": "success", 
                "date": date, 
                "events": [e.to_dict() for e in events]
            }
        except ValueError as exc:
            return {"status": "error", "message": str(exc)}
