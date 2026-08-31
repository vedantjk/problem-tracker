# Compiler Basics & Basic Program Structure (learncpp ch.0 + 1.1-1.11)

## Core model
- Build pipeline: **preprocessor** (handles `#include`/`#define`, emits a translation unit) → **compiler** (translation unit → object file `.o`, unresolved references) → **linker** (all `.o` + std lib → executable).
- Compile error = language rule broken inside one translation unit. Linker error = compiler accepted a declaration, no definition found anywhere ("undefined reference"), or found twice ("multiple definition").
- Statement = smallest unit of execution. Expression = combination of literals/variables/operators that evaluates to a value. Expression + `;` = expression statement.
- Every program has exactly one `int main()`, the entry point. Omitted `return` in `main` returns 0 (only `main`).
- `int x = 5;` is a definition with copy-initialization. `x = 5;` is assignment. Same `=`, different mechanism.
- `std::endl` = `'\n'` + flush (syscall). Use `'\n'`.
- Whitespace separates tokens (`intmain` vs `int main`), otherwise ignored except inside string literals. Adjacent string literals concatenate.
- Comments: `//` line, `/* */` block. Neither nests; use `#if 0` to comment out a block containing `/* */`.

## Quiz 29/08 (Claude, oral, no notes)
1. Stages source → executable? **Missed**: said compile + link; no preprocessor, no object files.
2. What's a statement; what must every program have? ok.
3. Classify `int x = 5;` vs `x = 5;`? **Missed**: called the first "copy assignment"; it's copy-initialization of a definition.
4. `endl` vs `'\n'`? ok.
5. Literal vs variable; `x` and `x + 5` classified? ok (`x + 5` isn't a statement until `;`).
6. Whitespace rules; comment forms and nesting? **Half**: whitespace ok, didn't know neither comment form nests.
7. Compile error vs linker error + examples? ok.

## Questions (getcracked)
- [ ] Munch munch munch! — 30/08 — MISSED: `x+++++y` — knew maximal munch, mis-split it. Lexing is left-to-right, each token maximal: `x ++ ++ + y` → `(x++)++` on an rvalue → CE. Spaces would make `x++ + ++y` = 10. Related: `a+++b` = `a++ +b` compiles; pre-C++11 `vector<vector<int>>` `>>` munch.
- Steps to C++ Development, Installing your IDE, Comments/Whitespace/Formatting/Printing: no questions.

## Compile vs link errors
Compile errors (one TU breaks a rule):
- `x = 5;` with no `int x;` in sight; missing semicolon; `void main()` (gcc/clang reject or warn — main must return int).
- Calling `main()` from code is ill-formed.

Link errors (compiler happy, program incomplete):
- `int foo();` declared, called, never defined → `undefined reference to foo`.
- `int x = 1;` in two .cpp files → `multiple definition of x`.

## Traps / interview one-liners
- "Undefined reference is a linker error: the compiler saw a declaration and trusted you."
- "Initialization constructs the object; assignment modifies an existing one. For class types that's ctor vs `operator=`."
- "`endl` flushes; in a hot loop that's a syscall per line."
- "`/* */` doesn't nest."
