"""
Input Validator — guardrail to protect the Orchestrator from malformed input.
"""


class ValidationError(Exception):
    """Raised when user input violates validation rules."""
    pass


class Validator:
    """
    Validates user input before it reaches the Orchestrator.
    
    Responsibilities:
    - Check for empty or purely whitespace input.
    - Enforce maximum length constraints.
    - Sanitize or reject malicious payloads (basic for Phase 1).
    """

    MAX_LENGTH = 2000

    @classmethod
    def validate(cls, user_input: str) -> None:
        """
        Validate the raw user input.
        
        Args:
            user_input: Raw string from the interface layer.
            
        Raises:
            ValidationError: If input is invalid.
        """
        if not isinstance(user_input, str):
            raise ValidationError(f"Input must be a string, got {type(user_input).__name__}")

        if not user_input.strip():
            raise ValidationError("Input cannot be empty or just whitespace.")

        if len(user_input) > cls.MAX_LENGTH:
            raise ValidationError(f"Input exceeds maximum length of {cls.MAX_LENGTH} characters.")
