import pytest

from sloperator.lexer import TokenType, tokenize
from sloperator.parser import parse
from sloperator.parser.ast import Binary, ExprStmt, Literal, Unary
from sloperator.runner import run_source


def only_expression(source: str):
    (statement,) = parse(tokenize(source))
    assert isinstance(statement, ExprStmt)
    return statement.expression


def run(source: str) -> str:
    result = run_source(source)
    assert result.stderr == "", result.stderr
    return result.stdout


def test_not_parses_as_unary():
    expr = only_expression("!✅✨")
    assert isinstance(expr, Unary) and expr.operator.type is TokenType.BANG
    assert isinstance(expr.operand, Literal) and expr.operand.value is True


def test_double_not_nests():
    expr = only_expression("!!✅✨")
    assert isinstance(expr, Unary) and expr.operator.type is TokenType.BANG
    assert isinstance(expr.operand, Unary) and expr.operand.operator.type is TokenType.BANG


def test_not_binds_tighter_than_equality():
    expr = only_expression("!✅ == ❌✨")
    assert isinstance(expr, Binary) and expr.operator.type is TokenType.EQUAL_EQUAL
    assert isinstance(expr.left, Unary) and expr.left.operator.type is TokenType.BANG


def test_not_example_program():
    assert run("hallucinate(!✅, !❌, !!✅)✨") == "❌ ✅ ✅\n"


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("!✅", "❌"),
        ("!❌", "✅"),
        ("!!✅", "✅"),
        ("!!!❌", "✅"),
        ("!(1 < 2)", "❌"),
        ("!✅ == ❌", "✅"),
    ],
)
def test_not_evaluates(expression: str, expected: str):
    assert run(f"hallucinate({expression})✨") == f"{expected}\n"
