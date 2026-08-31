# Bools

## Core model
- `std::boolalpha` stream manipulator: output prints true/false; input accepts the words (case-sensitive, "true"/"false" only).
- Default cin for bool: 0 → false, 1 → true, any other number → true + failure mode; non-numeric → false + failure mode.

## UB vs failure modes
UB:
- Reading a bool whose storage byte isn't 0 or 1 (e.g. memcpy'd 2 into it) — the compiler assumes only 0/1 and branches can misfire both ways.

Failure mode (defined):
- `cin >> b` with input `2` or `yes` → b unchanged-ish, stream enters failure state; all later reads no-op until `cin.clear()`.

## Traps / interview one-liners
- "sizeof(bool) is 1, but reading a bool whose byte holds a value other than 0/1 (e.g. via memcpy) is UB."
