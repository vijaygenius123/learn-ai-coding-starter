import pytest

from sloperator.lexer import TokenType, tokenize
from sloperator.parser import parse
from sloperator.parser.ast import Binary, ExprStmt, Grouping, Literal
from sloperator.runner import run_source


def only_expression(source: str):
    (statement,) = parse(tokenize(source))
    assert isinstance(statement, ExprStmt)
    return statement.expression


def run(source: str) -> str:
    result = run_source(source)
    assert result.stderr == "", result.stderr
    return result.stdout


def test_multiplication_binds_tighter_than_addition():
    expr = only_expression("1 + 2 * 3✨")
    assert isinstance(expr, Binary) and expr.operator.type is TokenType.PLUS
    assert isinstance(expr.left, Literal) and expr.left.value == 1
    assert isinstance(expr.right, Binary) and expr.right.operator.type is TokenType.STAR
    assert isinstance(expr.right.left, Literal) and expr.right.left.value == 2
    assert isinstance(expr.right.right, Literal) and expr.right.right.value == 3


def test_grouping_overrides_multiplication_precedence():
    expr = only_expression("(1 + 2) * 3✨")
    assert isinstance(expr, Binary) and expr.operator.type is TokenType.STAR
    assert isinstance(expr.left, Grouping)
    assert isinstance(expr.left.expression, Binary)
    assert expr.left.expression.operator.type is TokenType.PLUS


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("1 + 2 * 3", "7"),
        ("2 * 3 + 4 * 5", "26"),
        ("10 - 2 * 3", "4"),
        ("(1 + 2) * 3", "9"),
    ],
)
def test_multiplication_before_addition_evaluates(expression: str, expected: str):
    assert run(f"hallucinate({expression})✨") == f"{expected}\n"
