"""Unit tests for the JSON candidate parsing fixed in the security review."""
from app.core.tools.json_tools import _best_candidate, _clean_json_string


def test_clean_json_string_strips_leading_whitespace_before_fence():
    raw = "\n\n```json\n[{\"a\": 1}]\n```"
    assert _clean_json_string(raw).strip() == '[{"a": 1}]'


def test_clean_json_string_strips_bare_fence():
    raw = "```\n[{\"a\": 1}]\n```"
    assert _clean_json_string(raw).strip() == '[{"a": 1}]'


def test_best_candidate_scored_array():
    raw = '[{"score": 10, "task": "a"}, {"score": 90, "task": "b"}]'
    best, _ = _best_candidate(raw)
    assert best == {"task": "b"}


def test_best_candidate_non_dict_array_falls_back():
    raw = "[1, 2, 3]"
    best, cleaned = _best_candidate(raw)
    assert best is None
    assert cleaned == raw


def test_best_candidate_invalid_json_falls_back():
    raw = "not json at all"
    best, cleaned = _best_candidate(raw)
    assert best is None
    assert cleaned == raw
