from sloperator.lexer import tokenize
from sloperator.parser import parse
from sloperator.parser.ast import Call, ExprStmt, Literal, Variable
from sloperator.runner import run_source


def only_expression(source: str):
    (statement,) = parse(tokenize(source))
    assert isinstance(statement, ExprStmt)
    return statement.expression


def run(source: str) -> str:
    result = run_source(source)
    assert result.stderr == "", result.stderr
    return result.stdout


def test_call_used_directly_as_an_argument():
    expr = only_expression("hallucinate(add(1, 2))✨")
    assert isinstance(expr, Call) and len(expr.arguments) == 1
    assert isinstance(expr.callee, Variable) and expr.callee.name.lexeme == "hallucinate"
    argument = expr.arguments[0]
    assert isinstance(argument, Call) and len(argument.arguments) == 2
    assert isinstance(argument.callee, Variable) and argument.callee.name.lexeme == "add"
    left, right = argument.arguments
    assert isinstance(left, Literal) and left.value == 1
    assert isinstance(right, Literal) and right.value == 2


def test_nested_call_evaluates_before_the_outer_call():
    source = """clanker add(left, right) {
    ship left + right✨
}
hallucinate(add(1, 2))✨"""
    assert run(source) == "3\n"
