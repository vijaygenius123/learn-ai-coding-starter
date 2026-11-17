import pytest

from sloperator.runner import run_source


def run(source: str) -> str:
    result = run_source(source)
    assert result.stderr == "", result.stderr
    return result.stdout


def fails(source: str) -> str:
    result = run_source(source)
    assert result.exit_code == 1
    return result.stderr.rstrip("\n")


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("“ab” + “cd”", "abcd"),
        ("“” + “”", ""),
        ("“a” + “”", "a"),
        ("“” + “b”", "b"),
        ("“a” + “b” + “c”", "abc"),
        ("“a” + (“b” + “c”)", "abc"),
        ("(“a” + “b”) + “c”", "abc"),
        ("“a” + “b” == “ab”", "✅"),
        ("“a” + “b” == “a” + “c”", "❌"),
    ],
)
def test_string_concatenation(expression: str, expected: str):
    assert run(f"hallucinate({expression})✨") == f"{expected}\n"


def test_concatenation_preserves_escapes():
    assert run("hallucinate(“a\\n” + “b\\tc”)✨") == "a\nb\tc\n"


def test_concatenation_does_not_mutate_operands():
    source = """slop a = “x”✨
slop b = a + “y”✨
hallucinate(a)✨
hallucinate(b)✨"""
    assert run(source) == "x\nxy\n"


def test_concatenation_works_on_variables_and_call_results():
    source = """clanker greet(name) {
    ship “hi, ” + name✨
}
slop who = “Boots”✨
hallucinate(greet(who) + “!”)✨"""
    assert run(source) == "hi, Boots!\n"


def test_concatenation_in_a_loop_accumulates():
    source = """slop out = “”✨
slop i = 0✨
ralph i < 3 {
    out = out + “ab”✨
    i = i + 1✨
}
hallucinate(out)✨"""
    assert run(source) == "ababab\n"


@pytest.mark.parametrize(
    ("expression", "message"),
    [
        (
            "“a” + 1",
            "operands of '+' must both be numbers or both be strings, got string and number",
        ),
        (
            "1 + “a”",
            "operands of '+' must both be numbers or both be strings, got number and string",
        ),
        (
            "“a” + ✅",
            "operands of '+' must both be numbers or both be strings, got string and boolean",
        ),
        (
            "nothing() + “a”",
            "operands of '+' must both be numbers or both be strings, got nil and string",
        ),
        (
            "“a” + hallucinate",
            "operands of '+' must both be numbers or both be strings, got string and clanker",
        ),
    ],
)
def test_mixed_type_addition_is_a_runtime_error(expression: str, message: str):
    source = f"clanker nothing() {{ }}\nhallucinate({expression})✨"
    assert fails(source) == f"SlopLang runtime error at line 2: {message}"


def test_number_addition_still_works():
    assert run("hallucinate(1 + 2)✨") == "3\n"
