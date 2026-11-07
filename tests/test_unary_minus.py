"""Regression tests: unary minus accepts numbers only, never booleans."""

import pytest

from sloperator.runner import run_source


def test_unary_minus_rejects_true():
    result = run_source("hallucinate(-✅)✨")
    assert result.stdout == ""
    assert result.stderr == (
        "SlopLang runtime error at line 1: operand of unary '-' must be a number, got boolean\n"
    )
    assert result.exit_code == 1


def test_unary_minus_rejects_false():
    result = run_source("hallucinate(-❌)✨")
    assert result.stdout == ""
    assert result.stderr == (
        "SlopLang runtime error at line 1: operand of unary '-' must be a number, got boolean\n"
    )
    assert result.exit_code == 1


@pytest.mark.parametrize(("source", "expected"), [("hallucinate(-1)✨", "-1\n")])
def test_unary_minus_still_accepts_numbers(source: str, expected: str):
    result = run_source(source)
    assert result.stdout == expected
    assert result.stderr == ""
    assert result.exit_code == 0
