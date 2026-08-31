# Functions, Parameters, Arguments and Return Values

## Core model
- Function = reusable sequence of statements. `main` must return `int`, can't be called explicitly, implicitly returns 0. Not always first to run: global initializers (and their function calls) execute before `main`.
- Status codes: `0` / `EXIT_SUCCESS` / `EXIT_FAILURE` (macros in `<cstdlib>`); returned to the OS, readable by the launching process.
- One return value; use struct/pair/tuple + structured bindings for more. Small structs (≤16B) return in RAX:RDX on SysV.
- Call overhead: push return address, save/restore registers, shuffle args per ABI, stack frame; plus the call is an optimization barrier. Inline expansion removes all of it, at the cost of code size (i-cache pressure). Net effect can be positive, negative, or zero.
- `inline` keyword: historically an expansion hint (ignored freely; -O2 inlines small functions without it). Modern meaning: "multiple definitions allowed" (ODR rule 3). Requirements: full definition visible in every TU that uses it, once per TU, all definitions identical (else UB).
- Why not inline everything in headers: each TU compiles the definition again (6 includes = 6 compiles, linker dedupes), and any change recompiles every includer. Build-time cascade, not runtime.

## Questions (getcracked)
- [x] Once or twice? — 29/08 — ok

## Compile errors vs UB
Compile error:
- Two definitions of an inline function in ONE TU; calling an undeclared function.

UB:
- Flowing off the end of a non-void function: `int f() { }` then using the result. (main is the one exception — implicit return 0.)
- `inline` function with external linkage defined differently across TUs (NDR flavor).

Unspecified (not UB, still bites):
- Cross-TU order of global constructors — the static initialization order fiasco: `extern Logger log; Config c{log};` in another TU may run before log is built.

## Traps / interview one-liners
- "`inline` today is about linkage/ODR, not performance. The optimizer decides inlining on its own."
- "The real cost of a call isn't `call`/`ret`, it's that the optimizer can't see through it."
- "Return a struct, not out-params; the ABI returns it in registers if it's small, and RVO elides the copy if it's big."
- "Global initializers run before `main`, and their order across TUs is unspecified: static initialization order fiasco."
