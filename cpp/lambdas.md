# Anonymous Functions (Lambdas)

## Core model
- `[captures](params) -> ret { body }`. Anonymous functor: compiler generates a unique unnamed class with `operator()`. Not a function; that's how C++ gets "nested functions".
- Passing one: `std::function` (type-erased, may heap-allocate, indirect call, no inlining), template param `const T&` / `const auto&` (inlines, preferred in hot code), function pointer (captureless only; `+[]{}` forces the conversion).
- Generic lambda: `auto` params (C++14), one instantiation per deduced type, so a `static` local inside is per-instantiation.
- Implicitly `constexpr` since C++17 if captures and callees allow it.
- Captures: only automatic-duration variables need capturing; statics/globals/constexpr are visible directly. By-value capture = copy made at definition time, stored as a const member (operator() is const) → `mutable` to modify the copy. By-reference `&x` modifies the original; dangles if the original dies first.
- Defaults `[=]` / `[&]` must come first, may be mixed with explicit captures of the *other* kind, each variable once. Init-capture `[y = expr]` declares a new member.
- `[this]` captures the pointer, `[*this]` (C++17) copies the object. `[=]` implicitly capturing `this` is deprecated in C++20.
- Missing `return` in a non-void lambda: UB. `[] -> int {}` without `()` is C++23 only.

## Questions (getcracked)
- [x] Overloading lambdas! — 29/08 — ok
- [x] Am I missing something? — 29/08 — ok
- [x] Between two parts. — 29/08 — ok

## Quiz misses
- 30/08 (tree Q): sizeof of captureless lambda — said 8 ("functor ≈ pointer"); it's an empty struct → 1. Captures are the members; no captures, no data.

## Compile errors vs UB
Compile errors:
- `[x](){ x++; }` without `mutable` — assigning to a const member (the classic).
- Duplicate capture `[x, &x]`, default capture not first `[x, =]`, capturing at namespace scope (nothing to capture).
- `std::function<void(int)> f = [](auto,auto){};` — signature mismatch.
- `[] -> int { return 1; }` before C++23 (needs `()` with a trailing return type).

UB:
- By-ref capture outliving the variable: `auto f(){ int x=1; return [&x]{ return x; }; }` — dangles.
- Non-void lambda flowing off the end (same as any function).
- Calling a moved-from std::function: not UB but throws bad_function_call — know the difference.

## Traps / interview one-liners
- "A lambda is a struct with `operator()`; captures are its members. Everything else follows from that."
- "Closure sizes (verified): `[]` → 1 (empty struct), `[x]` int → 4 (copy), `[&x]` → 8 (reference stored as pointer). `sizeof(int&)` still reports 4: the language gives references no size of their own, but a reference member/capture costs pointer storage — `sizeof(struct{int&})` == 8."
- "`std::function` in a hot loop is an indirect call the optimizer can't see through; take a template parameter instead."
- "`mutable` exists because `operator()` is const by default."
- "Capturing a local by reference and returning the lambda is the classic dangling-reference bug."
- "`[=]` and `[&]` capture only what the body uses, not everything in scope."
