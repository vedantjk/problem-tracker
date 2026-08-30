# Undefined Behavior

## Core model
- UB = executing code whose behavior the language doesn't define. Result can be anything, including "works correctly", which is what makes it dangerous.
- Uninitialized variable = never given a value by the program. Reading it is UB.
- Distinct bucket: ill-formed, no diagnostic required (NDR). The program is invalid but the compiler needn't complain. Practically indistinguishable from UB.
- Reserved identifiers (using one is ill-formed NDR): `_x` at global scope; `_X` (underscore + uppercase) and anything containing `__` everywhere.

## Questions
- [x] _global_variable — 29/08 — ok

## Traps / interview one-liners
- "UB isn't 'random': the optimizer assumes it never happens and deletes branches that depend on it. Classic: a null check after a dereference gets removed."
- "Common UB: uninitialized read, signed overflow, out-of-bounds, dangling pointer/reference, data race, `-INT_MIN`, shift by >= width."
- "Tools: `-fsanitize=undefined,address`, `-Wall -Wextra`, and compiling at -O2 to see if behavior changes."
