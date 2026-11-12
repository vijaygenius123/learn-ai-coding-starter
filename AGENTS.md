# AGENTS.md

Sloperator: a tree-walking interpreter for SlopLang (`.slop`), pure Python 3.13, no runtime deps.

## Commands

Always use `uv run` (never bare `python`/`pytest`):

```bash
uv run pytest                              # all tests
uv run pytest tests/test_parser.py -k name # single test
uv run ruff format --check                 # format check (line-length 100)
uv run ruff check                          # lint (E,F,I,UP,B)
uv run ty check                            # type check
uv run sloperator.py examples/fib.slop     # run a program
uv run sloperator.py --check prog.slop     # syntax-check only
uv run playground/server.py                # playground on :8080
```

The `validate` skill (`.agents/skills/validate/SKILL.md`) runs pytest + ruff format + ruff check.
The `run_slop` tool (`.opencode/plugins/run-slop.ts`) runs a `.slop` file via `uv run sloperator.py`.

## SlopLang gotchas

- Source is UTF-8 with **smart quotes** `“ ”` (straight `"` is a lexical error), em-dash `—` comments, and emoji tokens `✨` (statement terminator), `✅`/`❌` (booleans). Emoji may carry a trailing U+FE0F variation selector.
- `✨` follows declarations, assignments, `ship`, and expression statements — never a block's closing `}`.
- Keywords: `slop` (let), `loadbearing` (const), `clanker` (fn), `vibe`/`nah` (if/else), `ralph` (while), `ship` (return), `hallucinate` (print, the only built-in).
- No floats, arrays, maps, nested functions, `break`/`continue`/`for`, or imports. Functions must be declared before first call.
- `docs/spec.md` is the authoritative grammar/semantics reference; keep it in sync with behavior changes.

## Layout

`sloperator.py` (CLI) → `sloperator/runner.py` (`run_program`, `check_program`, `run_source`) → `lexer/` → `parser/` → `evaluator/`. Errors are `SlopError` subclasses in `sloperator/errors.py`; the CLI prints them to stderr and exits 1 (2 for usage/IO), never a traceback.

## Tests

- `tests/test_examples.py` parametrizes over every `examples/*.slop` and requires each to exit 0 with non-empty stdout — a new example must run cleanly.
- `tests/test_cli.py` shells out to `sloperator.py` via `sys.executable`; `tests/test_lexer_regression.py` guards known scanner edge cases.
- Tests use `run_source()` from `sloperator/runner.py` for in-process execution.

## Repo notes

- `opencode.jsonc` denies `read` on `*.env`; don't try to read `.env`.
- `opencode-desktop-mac-arm64.dmg` is an untracked 0-byte artifact — leave it out of commits.
- `uv.lock` is gitignored (`.ignore`).
