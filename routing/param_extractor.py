"""
ParamExtractor — extract structured tool parameters from raw user input.

Called by HybridIntentRouter immediately after intent classification.
Ensures tools receive pre-extracted, structured parameters rather than raw text,
keeping tool functions deterministic and free of heuristic parsing.

Non-responsibilities:
- Intent classification
- Tool execution
"""

import re
from datetime import date as dt_date


class ParamExtractor:
    """
    Extract structured parameters for each supported intent.

    Responsibilities:
    - Parse primitive values (amounts, dates) from raw user text.
    - Return a typed parameter dict for the resolved intent.
    - Default to today's date when no date is found in input.
    """

    def extract(self, intent: str, user_input: str) -> dict:
        """
        Build a structured params dict for the given intent and raw input.

        Args:
            intent: Resolved intent name (e.g., 'finance.add_expense').
            user_input: Raw text from the user.

        Returns:
            Dict of structured parameters ready for tool dispatch.
        """
        today = dt_date.today().isoformat()

        if intent == "finance.add_expense":
            return self._extract_finance_add(user_input, today)
        if intent == "finance.query_expenses":
            return {"category": None, "date_from": None, "date_to": None}
        if intent == "calendar.create_event":
            return {"user_input": user_input, "date": today, "time": None}
        if intent == "calendar.list_events":
            return {"user_input": user_input, "date": today}
        # conversation or unknown — pass raw text through
        return {"user_input": user_input}

    @staticmethod
    def _extract_finance_add(text: str, today: str) -> dict:
        """Heuristic extraction of amount and metadata for add_expense."""
        amount = 0.0
        m = re.search(r'\b(\d+)(k|m|)\b', text, re.IGNORECASE)
        if m:
            val = float(m.group(1))
            suffix = m.group(2).lower()
            if suffix == 'k':
                val *= 1_000
            elif suffix == 'm':
                val *= 1_000_000
            amount = val
        return {
            "amount": amount,
            "category": "other",
            "description": text,
            "date": today,
        }
