# Undefined Behavior

## Core model
- UB = executing code whose behavior the language doesn't define. Result can be anything, including "works correctly", which is what makes it dangerous.
- Uninitialized variable = never given a value by the program. Reading it is UB.
- Distinct bucket: ill-formed, no diagnostic required (NDR). The program is invalid but the compiler needn't complain. Practically indistinguishable from UB.
- Reserved identifiers (using one is ill-formed NDR): `_x` at global scope; `_X` (underscore + uppercase) and anything containing `__` everywhere.

## Questions
- [x] _global_variable — 29/08 — ok

## The full taxonomy (with one example each)
| Category | Meaning | Example |
|---|---|---|
| Compile error | rule violation, diagnostic required | `int x = "hi";` |
| Ill-formed NDR | invalid program, no diagnostic owed | `int __x;` (reserved name), mismatched ODR-rule-3 definitions |
| Implementation-defined | must pick & document a behavior | `sizeof(long)`, `char` signedness, right-shift of negative (pre-C++20) |
| Unspecified | one of several behaviors, needn't document | evaluation order in `f(a(), b())`, static-init order across TUs |
| UB | anything may happen | `INT_MAX + 1`, dangling deref, OOB index, data race, `-INT_MIN` |

## Traps / interview one-liners
- "UB isn't 'random': the optimizer assumes it never happens and deletes branches that depend on it. Classic: a null check after a dereference gets removed."
- "Common UB: uninitialized read, signed overflow, out-of-bounds, dangling pointer/reference, data race, `-INT_MIN`, shift by >= width."
- "Tools: `-fsanitize=undefined,address`, `-Wall -Wextra`, and compiling at -O2 to see if behavior changes."
