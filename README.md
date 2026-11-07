# Sloperator

A tree-walking interpreter for [SlopLang](docs/spec.md), written in Python.

## Run

```bash
uv run sloperator.py examples/fib.slop   # run a program
uv run sloperator.py --check prog.slop   # syntax-check only
uv run playground/server.py              # playground at http://localhost:8080
```

## Validate

```bash
uv run pytest              # tests
uv run ruff format --check # formatting
uv run ruff check          # linting
uv run ty check            # type checking
```

## Language

SlopLang has smart quotes, emoji tokens, and its own vocabulary: `slop` declares
a variable, `clanker` defines a function, `vibe`/`nah` branch, `ralph` loops,
`ship` returns, and `hallucinate` prints. Statements end with `✨`; comments
start with `—`.

```slop
clanker describe(count) {
    vibe count > 1 { ship “big slop”✨ } nah { ship “small slop”✨ }
}
slop count = 0✨
ralph count < 3 {
    hallucinate(describe(count))✨
    count = count + 1✨
}
```

The full specification — grammar, values, operators, scoping, errors, and how to
type the special characters — is in [docs/spec.md](docs/spec.md).

## Layout

`sloperator.py` is the CLI entrypoint. `sloperator/` holds the pipeline —
`lexer/`, `parser/`, `evaluator/`, and `runner.py`. Examples live in `examples/`,
tests in `tests/`, and the web playground in `playground/`.
