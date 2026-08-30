# The Preprocessor and Header Guards

## Core model
- Preprocessor runs before compilation, top to bottom, per file: strips comments, ensures trailing newline, expands `#include` (textual paste), `#define`, conditional compilation. Output = translation unit.
- Translation phases: map source chars → splice lines → lex → preprocess → string literal encoding → concatenate adjacent literals → compile → instantiate templates → link.
- Conditional compilation: `#ifdef` / `#ifndef` / `#if 0` / `#endif`. `#if 0` = the way to comment out a block that contains `/* */`.
- Macro scope: none. The preprocessor doesn't know what a function is; `#define` inside `foo()` behaves like a define at top of file, from that line down. Defines don't leak across files unless the file is `#include`d.
- Header guard: `#ifndef X_H / #define X_H / ... / #endif`. Prevents one *translation unit* from seeing the header twice (ODR rule 1). Does nothing across TUs: a non-inline definition in a guarded header still gives "multiple definition" at link if two .cpp include it (ODR rule 2). Fix: `inline`, or `extern` in header + one definition in a .cpp.
- `#pragma once`: non-standard, universally supported, widely used. Fails only when the same header exists as two copies on disk (compiler can't tell they're identical); classic guards dedupe by macro name and survive that.

## Questions (getcracked)
- [x] Bodyguard — 29/08 — ok

## Traps / interview one-liners
- "Guards solve within-TU duplication; `inline`/`extern` solve across-TU duplication. Different problems."
- "Standard headers never break because they're guarded and contain only declarations, types, templates, inline."
- "Macros have no scope, so SCREAMING_CASE to avoid colliding with real identifiers."
- "`#include` is a textual paste; that's why include order can matter and why headers must be self-contained."
