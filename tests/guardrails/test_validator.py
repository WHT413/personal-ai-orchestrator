"""Unit tests for Guardrails Validator."""

import pytest
from guardrails.validator import Validator, ValidationError


def test_validator_accepts_valid_string():
    Validator.validate("xin chào")


def test_validator_raises_on_non_string():
    with pytest.raises(ValidationError, match="Input must be a string"):
        Validator.validate(123)


def test_validator_raises_on_empty_string():
    with pytest.raises(ValidationError, match="Input cannot be empty"):
        Validator.validate("")


def test_validator_raises_on_whitespace_string():
    with pytest.raises(ValidationError, match="Input cannot be empty"):
        Validator.validate("   \n \t  ")


def test_validator_raises_on_too_long_string():
    long_string = "a" * 2001
    with pytest.raises(ValidationError, match="exceeds maximum length"):
        Validator.validate(long_string)
