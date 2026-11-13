# AGENTS.md

Sloperator: a tree-walking interpreter for SlopLang (`.slop`), pure Python 3.13, no runtime deps.

## Layout

`sloperator.py` (CLI) → `sloperator/runner.py` (`run_program`, `check_program`, `run_source`) → `lexer/` → `parser/` → `evaluator/`. Errors are `SlopError` subclasses in `sloperator/errors.py`; the CLI prints them to stderr and exits 1 (2 for usage/IO), never a traceback. `examples/` holds runnable `.slop` programs, `tests/` the pytest suite, `playground/` a local web playground.

## Validation

Always use `uv run` (never bare `python`/`pytest`). Run all four before committing:

```bash
uv run pytest                  # tests
uv run ruff format --check     # format check (line-length 100)
uv run ruff check              # lint (E,F,I,UP,B)
uv run ty check                # type check
```

The `validate` skill (`.agents/skills/validate/SKILL.md`) runs pytest + ruff format + ruff check.

## Regression tests

Add a regression test whenever you fix a bug or change observable behavior — error messages, exit codes, precedence, or scanner edge cases. Put it where the behavior lives:

- Parser and syntax-error messages → `tests/test_parser.py`; full end-to-end error text and exit codes → `tests/test_errors.py`.
- Scanner edge cases (smart quotes, emoji, variation selectors) → `tests/test_lexer_regression.py`.
- Runtime semantics → `tests/test_evaluator.py`; CLI behavior → `tests/test_cli.py`.

Tests use `run_source()` from `sloperator/runner.py` for in-process execution. `tests/test_examples.py` parametrizes over every `examples/*.slop` and requires each to exit 0 with non-empty stdout, so a new example must run cleanly.

## Language behavior

`docs/spec.md` is the authoritative grammar and semantics reference — read it before changing the language, and update it in the same change as any behavior change. Parser-specific conventions live in `sloperator/parser/AGENTS.md`.
