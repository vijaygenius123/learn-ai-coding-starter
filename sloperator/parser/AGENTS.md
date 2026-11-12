# Parser conventions

Two rules for `sloperator/parser/`. Follow them when adding or changing grammar.

## 1. One method per grammar rule

Each rule in `docs/spec.md` gets exactly one method on `Parser`, named after the rule
(`function_decl`, `var_decl`, `if_stmt`, `logic_or`, `unary`, `primary`, …). A method
parses its whole rule and returns the AST node for it — no rule is split across methods
and no method parses two rules.

- Recursive descent: a rule's method calls the methods of the rules it references, in
  precedence order (`expression` → `logic_or` → `logic_and` → `comparison` → `equality`
  → `term` → `factor` → `unary` → `call` → `primary`).
- Left-associative loops (`while self.match(...)`) stay inside the rule's own method.
- Helpers that are not grammar rules (`match`, `check`, `advance`, `peek`, `peek_next`,
  `previous`, `at_end`, `expect`, `error`, `terminator`) are fine, but they must not
  consume tokens for a rule on their own.
- When the grammar changes, update the rule's method and `docs/spec.md` together.

## 2. Syntax errors describe what token was found

Every `SlopSyntaxError` raised by the parser must say what was expected **and** what was
actually found. Route all of them through `self.error(token, message)` (or `self.expect`,
which calls it), never construct `SlopSyntaxError` directly for a token mismatch.

`error()` appends the found token, so the message you pass is only the expectation:

```python
raise self.error(self.peek(), "expected ')' after parameters")
# → "expected ')' after parameters, found '✨'"
# → "expected ')' after parameters, but reached end of file"   (at EOF)
```

- Pass the offending token — usually `self.peek()` — so the line number points at it.
- Quote the found lexeme with single quotes; `error()` does that for you.
- Keep the expectation lowercase and specific: name the token (`'='`, `✨`, `clanker
  name`) rather than saying "invalid syntax".
- Semantic checks that are not token mismatches (e.g. `ship` outside a `clanker`,
  duplicate parameter names) may raise `SlopSyntaxError` directly, but should still name
  the offending lexeme in the message.
- Tests in `tests/test_parser.py` and `tests/test_errors.py` assert the full message
  including the `, found '…'` suffix — update them when a message changes.
