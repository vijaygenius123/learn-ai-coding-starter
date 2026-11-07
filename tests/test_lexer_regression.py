"""Regression tests for lexical error paths that the main lexer suite covers thinly."""

import pytest

from sloperator.errors import LexicalError
from sloperator.lexer import tokenize


@pytest.mark.parametrize("char", ["#", "$", "%", "^", "~", "?", ":", ".", "[", "]", "'"])
def test_unexpected_character_reports_the_offending_char(char: str):
    with pytest.raises(LexicalError) as info:
        tokenize(f"a {char} b")
    assert info.value.line == 1
    assert info.value.message == f"unexpected character '{char}'"
    assert str(info.value) == f"SlopLang lexical error at line 1: unexpected character '{char}'"


def test_unexpected_character_reports_the_line_it_appears_on():
    with pytest.raises(LexicalError) as info:
        tokenize("slop x = 1✨\n\nslop y = 2 # nope")
    assert info.value.line == 3
    assert info.value.message == "unexpected character '#'"
