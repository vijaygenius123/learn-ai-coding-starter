import pytest

from sloperator.lexer import TokenType, tokenize
from sloperator.parser import parse
from sloperator.parser.ast import Binary, ExprStmt, Literal, Logical
from sloperator.runner import run_source


def only_expression(source: str):
    (statement,) = parse(tokenize(source))
    assert isinstance(statement, ExprStmt)
    return statement.expression


def run(source: str) -> str:
    result = run_source(source)
    assert result.stderr == "", result.stderr
    return result.stdout


def test_comparison_binds_tighter_than_equality():
    expr = only_expression("1 < 2 == ✅✨")
    assert isinstance(expr, Binary) and expr.operator.type is TokenType.EQUAL_EQUAL
    assert isinstance(expr.left, Binary) and expr.left.operator.type is TokenType.LESS
    assert isinstance(expr.right, Literal) and expr.right.value is True


def test_equality_binds_tighter_than_logic_and():
    expr = only_expression("✅ && 1 == 1✨")
    assert isinstance(expr, Logical) and expr.operator.type is TokenType.AND
    assert isinstance(expr.right, Binary) and expr.right.operator.type is TokenType.EQUAL_EQUAL


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("1 < 2 == ✅", "✅"),
        ("1 > 2 == ❌", "✅"),
        ("1 < 2 == 1 > 2", "❌"),
        ("✅ && 1 == 1", "✅"),
        ("❌ || 1 < 2", "✅"),
        ("1 + 1 == 2", "✅"),
        ("2 * 3 > 5", "✅"),
    ],
)
def test_comparison_precedence_evaluates(expression: str, expected: str):
    assert run(f"hallucinate({expression})✨") == f"{expected}\n"
