# C++ Notes — Concept Index

Notes organized by **concept** (not by getcracked tree node). Each file: Core model · Questions/Quiz misses · Compile-errors-vs-UB · Syntax anchors · Traps.
Missed questions → Anki card (front = question, back = the one-line reason).

## Files
| File | Owns |
|---|---|
| [build_linkage.md](build_linkage.md) | build pipeline, ODR, inline, preprocessor/macros, headers, identifiers, namespaces |
| [types_conversions.md](types_conversions.md) | promotions, signed/unsigned, shifts, fixed-width ints, enums, bools, overload ranks |
| [floating_point.md](floating_point.md) | IEEE-754, numeric_limits, float traps |
| [initialization_deduction.md](initialization_deduction.md) | init forms, narrowing, designated init, vexing parse, auto/auto&/auto&&, static init phases, constinit, thread_local |
| [expressions.md](expressions.md) | sequencing, maximal munch, comma/ternary, ++/--, operator overloading |
| [control_flow.md](control_flow.md) | if/else, early return, switch (labels, fallthrough, [[fallthrough]], case scoping), while/do-while/for, break/continue, halts (exit/abort/terminate) |
| [memory_layout.md](memory_layout.md) | sizeof, padding/alignment, vptr, virtual bases, EBO, reference storage, memory segments / stack vs heap |
| [bits_punning.md](bits_punning.md) | bitset, bitwise promotion, strict aliasing, reinterpret_cast, memcpy, bit_cast |
| [functions_scope_lambdas.md](functions_scope_lambdas.md) | calls/ABI, RVO/NRVO, scope/duration/linkage, lambdas, tuple |
| [error_handling.md](error_handling.md) | std::optional (access tiers, in_place, monadic ops), std::expected (C++23), exceptions (matching, unwinding, rethrow, function try, throwing dtors, cost model) |
| [ub_catalog.md](ub_catalog.md) | behavior taxonomy + master UB list with pointers |

## Where is...? (every concept, A-Z)
- ABI / RAX:RDX struct return → functions_scope_lambdas
- ADL (friend found only by) → expressions (operator overloading)
- aggregate rules → initialization_deduction
- alignment / alignof / alignas → memory_layout (data), bits_punning (casts)
- aliasing (strict) rule + audit checklist → bits_punning
- Anki-priority repeat miss: auto& keeps const → initialization_deduction
- anonymous namespace / internal linkage → build_linkage
- ASCII anchors ('A'=65, 'a'=97, '0'=48) → types_conversions
- assignment vs initialization → initialization_deduction (+ build_linkage traps)
- auto / auto& / const auto& / auto&& (legal-binding model) → initialization_deduction
- bit_cast → bits_punning
- bitset (set/reset/flip/test, sizeof, [] vs test) → bits_punning
- bool (boolalpha, cin failure, non-0/1 byte UB) → types_conversions
- break vs return (switch + loops, innermost-only, no labeled break) → control_flow
- continue (runs for's end-expression; while-loop infinite-loop trap) → control_flow
- case labels (constant, unique, '6'==54 collision) → control_flow
- case scoping / init-in-case CE / explicit block fix → control_flow
- catch matching (no conversions, derived→base, const&) / catch-all must be last → error_handling
- braces: auto x{1,2} / initializer_list → initialization_deduction
- char arithmetic & promotion → types_conversions
- comma operator (precedence, return a,b) → expressions
- comments don't nest / #if 0 → build_linkage
- const vs constexpr vs constinit (globals) → initialization_deduction
- constant-init / zero-init / dynamic-init phases (statics) → initialization_deduction
- conversion vs promotion ranks (overloads) → types_conversions
- copy elision (guaranteed) vs NRVO → functions_scope_lambdas
- data races → ub_catalog (pointer)
- default-init vs value-init (garbage vs zero) → initialization_deduction
- designated initializers (all 6 CE cases) → initialization_deduction
- do-while (semicolon, scope-outside-block gotcha) → control_flow
- early return → control_flow
- endian / std::endian → bits_punning
- endl vs '\n' → build_linkage
- enum / enum class / to_underlying / using enum → types_conversions
- epsilon vs denorm_min vs min vs lowest → floating_point
- erroneous behavior (C++26) → ub_catalog, types_conversions
- exceptions (all of it: throw/try/catch, unwinding, terminate, cost model) → error_handling
- [except.ctor] return-object-destroyed-by-unwinding rule (bcad; compilers non-conforming) → error_handling
- expected (std::expected/unexpected/unexpect, error(), transform_error) → error_handling
- EXIT_SUCCESS / status codes → build_linkage
- [[fallthrough]] attribute / fallthrough rules → control_flow
- fixed-point prices ×10^4 (ITCH/venues) → floating_point traps
- fixed-width ints / size_t / ptrdiff_t / uint8_t-prints-as-char → types_conversions
- float→int out-of-range UB → floating_point
- fold expressions (quiz miss context) → README quiz table
- for loop (order of parts, omitted parts, multi-counter comma, != vs <) → control_flow
- forward declarations → build_linkage
- forward progress rule (side-effect-free infinite loop UB) → control_flow, ub_catalog
- function try blocks (ctor init-list catches, implicit rethrow) → error_handling
- halts: std::exit / atexit / abort / terminate / quick_exit (cleanup matrix, RAII break) → control_flow
- function-like macros (paste, double-eval, SQUARE=11) → build_linkage
- header guards / #pragma once → build_linkage
- IEEE-754 layout, bias, hidden bit, subnormals, Inf/NaN, round-to-even → floating_point
- if (x) non-bool condition conversion → control_flow
- if-else vs switch (when to use which) → control_flow
- infinite loops (while(true) idiom, semicolon null-body, unsigned counter wrap) → control_flow
- inline (ODR meaning, requirements, why not everything) → build_linkage
- integral promotion (sub-int → signed int) → types_conversions
- jump table (why switch is integral-only) → control_flow
- keywords (92) & special identifiers → build_linkage
- lambdas (captures, mutable, sizes, passing, generic, constexpr) → functions_scope_lambdas
- lifetime extension (const&/&& on temporaries; doesn't chain) → initialization_deduction
- loop counters (signed! unsigned >= 0 bug) → control_flow
- linkage (none/internal/external) → functions_scope_lambdas (+ build_linkage)
- lvalue ternary / prefix++ returns lvalue → expressions
- macro scope (none) → build_linkage
- monadic optional ops and_then/transform/or_else, nested-optional trap → error_handling
- malloc/free (size tracked by allocator, brk/sbrk/mmap, calloc/realloc) → memory_layout
- memory errors, the OSTEP seven (overflow, leak, dangling, double/invalid free) → memory_layout, ub_catalog
- main() specialness → build_linkage
- maximal munch (x+++++y, a+++b, >>) → expressions
- memcpy as blessed pun → bits_punning
- memory segments (code/data/BSS/heap/stack) → memory_layout
- memory leaks: pointers vs pointees → functions_scope_lambdas traps
- most vexing parse → initialization_deduction
- NaN != NaN / signed zero → floating_point
- narrowing (list-init CE, value-checked) → initialization_deduction
- NDR (ill-formed, no diagnostic) → ub_catalog, build_linkage
- noexcept destructors (default since C++11; throwing dtor → terminate) → error_handling
- nullopt / bad_optional_access / value_or / in_place / emplace → error_handling
- optional (std::optional, all of it) → error_handling
- numeric_limits quartet → floating_point
- ODR rules 1/2/3 → build_linkage
- operator overloading (homes, can't-overload list, && short-circuit loss, <=>) → expressions
- operator void() oddity → initialization_deduction
- overload ambiguity foo(-1.5) → types_conversions
- padding / tail padding / offsets / pahole → memory_layout
- pointer indirection cost x->foo() vs y.foo() (locality, SROA/aliasing) → memory_layout
- pointers-to-int (uintptr_t round-trip) → bits_punning
- popcount / <bit> / countl_zero → bits_punning
- prefix vs postfix ++ (lvalue/rvalue, class-type cost) → expressions
- range-based for (auto/auto&/const auto&, decayed-array CE, no index, views::reverse, C++23 temporary fix) → control_flow
- recursion (stack depth, static-local memo, no guaranteed TCO, --x sequencing trap) → functions_scope_lambdas
- preprocessor pipeline & translation phases → build_linkage
- promotion flips comparison (unsigned short a-b) → types_conversions
- references: sizeof(int&) vs reference members → memory_layout
- reinterpret_cast legal-pattern checklist → bits_punning
- reverse iteration (views::reverse, rbegin/rend, base() off-by-one, i-- > 0 idiom) → control_flow
- reserved identifiers (_x, _X, __) → build_linkage
- rethrow (bare throw vs throw e slicing) → error_handling
- RVO / NRVO / -fno-elide-constructors → functions_scope_lambdas
- scope vs duration vs lifetime → functions_scope_lambdas
- sequencing (C++14 vs C++17 table) → expressions
- sequential/stacked case labels (≠ fallthrough) → control_flow
- shadowing / -Wshadow → functions_scope_lambdas
- shifts (count rule, value rules, x86 masking) → types_conversions
- signature (excludes return type) → build_linkage
- size_t underflow loops → types_conversions
- sizeof class rules / vptr / vbase / EBO / [[no_unique_address]] → memory_layout
- stack unwinding (search-then-unwind, dtors per frame, zero-cost tables) → error_handling
- stack vs heap (SP mechanics, frame contents, sizes, overflow, OSTEP 14.1) → memory_layout
- static init order fiasco → functions_scope_lambdas (+ build_linkage)
- static local in generic lambda (per-instantiation) → functions_scope_lambdas
- static members (not in sizeof) → memory_layout
- std::function costs / bad_function_call → functions_scope_lambdas
- strings: literals deduce const char*, ""s/""sv → initialization_deduction
- structured bindings / std::tie / std::ignore / tie-comparator → functions_scope_lambdas
- switch (condition types, default, execution flow) → control_flow
- tail call optimization (not guaranteed in C++) → functions_scope_lambdas
- terminate (uncaught throw; unwind impl-defined) → error_handling
- ternary (precedence, branch unification, lvalue) → expressions
- thread_local (per-thread copy, lazy locals, fs-segment access) → initialization_deduction
- tuple (get rules, apply, CE list, forward_as_tuple dangling) → functions_scope_lambdas
- UB taxonomy + master list → ub_catalog
- uninitialized reads → initialization_deduction, ub_catalog
- unsigned wrap (arithmetic + conversion) → types_conversions
- while / do-while / for (full loop notes) → control_flow
- vexing parse → initialization_deduction
- virtual inheritance sizes → memory_layout
- vptr → memory_layout

## getcracked node → file map
| Node | File | Q result |
|---|---|---|
| Steps to C++ Dev / IDE / Comments & Printing | build_linkage | no questions |
| Variables, Objects, Initialization | initialization_deduction | 3/3 ok |
| Keywords and Identifiers | build_linkage | no questions |
| Undefined Behavior | ub_catalog | 1/1 ok (_global_variable) |
| Literals/Operators, "The other behaviors" | expressions | One after the other: MISSED |
| Declarations/Definitions/Multiple files | build_linkage | no questions |
| Preprocessor + header guards | build_linkage | Bodyguard ok |
| Functions | functions_scope_lambdas | Once or twice? ok |
| Scope | functions_scope_lambdas | I am the shadows. ok |
| Namespaces | build_linkage | no questions |
| Anonymous Functions | functions_scope_lambdas | 3/3 ok; sizeof-lambda tree Q MISSED |
| Object Sizes | memory_layout | (tree Qs pending) |
| Signed vs Unsigned | types_conversions | Down shift: MISSED |
| Fixed Width Integers | types_conversions | (pending) |
| Floating Point | floating_point | A very small value: MISSED |
| Bools | types_conversions | (pending) |
| Enumerations | types_conversions | FeePriority ok |
| Tuple | functions_scope_lambdas | (pending) |
| auto | initialization_deduction | (pending) |
| Bitflags/bitset | bits_punning | sizeof-bitset seen in quiz |
| reinterpret_cast & memcpy | bits_punning | (pending) |
| std::bit_cast | bits_punning | (pending) |
| Comma and ? | expressions | Munch munch munch!: MISSED |
| Operator overloading (intro) | expressions | (pending) |
| if / switch / loops (learncpp 4.10, 8.5-8.6, 8.8-8.10 — read 01/09) | control_flow | (pending) |

## Quizzes
| Date | Quiz | Score | Time | Percentile | Notes |
|---|---|---|---|---|---|
| 29/08/2026 | Beginner C++ (getcracked) | 11/20 | 18:11 | top 9.7% of 248 ("Cracked") | Baseline, cold. 2 coding Qs skipped. Missed: full-specialization member def (no `template<>`), fold `sum(2,0.5,..)` is double (arith conversions per `+`), macro double-eval `121`, `delete` on `malloc`, `const alias` = top-level const (`int* const`), `class A; struct A{}` same entity. Priority: Templates, Pointers/const, new/delete, Classes. Retake after tree. |
| 31/08/2026 | Claude notes quiz #1 (11 Q) | 8 clean | ~30m | — | MISSED: SQUARE(2+3)=11 (macro paste), auto& keeps const (REPEAT). Precision dings: padding offsets map, 1<<31=INT_MIN, NRVO vs guaranteed elision. |
| 01/09/2026 | Claude quiz #2 (10 Q, day's material + exceptions) | 8.5/10 | ~30m | — | HALVES: catch(...)-first is CE not catch-everything; uncaught→unwind impl-defined (dtors not guaranteed); switch decl-vs-init terminology + "garbage" for UB (REPEAT). Clean: ctor-throw member destruction, exit cleanup order, segments, access tiers, and_then retest, slicing rethrow, constinit. |

## Template (per concept file)
```
# <Concept>
## Core model
## Questions (getcracked) / Quiz log
## Compile errors vs UB
## Syntax anchors
## Traps / interview one-liners
```
