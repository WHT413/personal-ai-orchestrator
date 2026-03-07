"""Unit tests for IntentParser."""

import pytest
from core.intent_parser import IntentParser, ToolCall, ParseError


@pytest.fixture
def parser():
    return IntentParser()


def test_parse_valid_tool_call(parser):
    raw = 'TOOL_CALL: {"tool": "finance.add_expense", "args": {"amount": 50000, "category": "food", "description": "bun bo", "date": "2026-03-07"}}'
    result = parser.parse(raw)
    assert isinstance(result, ToolCall)
    assert result.tool == "finance.add_expense"
    assert result.args == {
        "amount": 50000,
        "category": "food",
        "description": "bun bo",
        "date": "2026-03-07",
    }


def test_parse_plain_text_returns_none(parser):
    result = parser.parse("Hello! How can I help you today?")
    assert result is None


def test_parse_empty_string_returns_none(parser):
    result = parser.parse("")
    assert result is None


def test_parse_tool_call_with_empty_args(parser):
    raw = 'TOOL_CALL: {"tool": "finance.query_expenses", "args": {}}'
    result = parser.parse(raw)
    assert result.tool == "finance.query_expenses"
    assert result.args == {}


def test_parse_tool_call_without_args_field(parser):
    raw = 'TOOL_CALL: {"tool": "finance.query_expenses"}'
    result = parser.parse(raw)
    assert result.tool == "finance.query_expenses"
    assert result.args == {}


def test_parse_malformed_json_raises(parser):
    raw = "TOOL_CALL: {not valid json}"
    with pytest.raises(ParseError, match="invalid"):
        parser.parse(raw)


def test_parse_missing_tool_field_raises(parser):
    raw = 'TOOL_CALL: {"args": {"amount": 100}}'
    with pytest.raises(ParseError, match="'tool'"):
        parser.parse(raw)


def test_parse_non_dict_payload_raises(parser):
    raw = 'TOOL_CALL: ["not", "a", "dict"]'
    with pytest.raises(ParseError, match="JSON object"):
        parser.parse(raw)


def test_parse_tool_call_with_preamble(parser):
    """LLM may write reasoning text before the TOOL_CALL line."""
    raw = "I will record this expense.\nTOOL_CALL: {\"tool\": \"finance.add_expense\", \"args\": {\"amount\": 100}}"
    result = parser.parse(raw)
    assert result.tool == "finance.add_expense"
    assert result.args == {"amount": 100}


def test_parse_args_non_dict_raises(parser):
    raw = 'TOOL_CALL: {"tool": "finance.add_expense", "args": "not a dict"}'
    with pytest.raises(ParseError, match="'args'"):
        parser.parse(raw)
