# C++ Notes — Concept Index

These notes are organized by concept. Each topic explains the material in full sentences, places small examples beside the relevant explanation, and ends with interview Q&A and the original practice history. Read the notes to learn the topic; use the Q&A afterward to practise explaining it aloud.

The default baseline is C++20/23 unless a section names another version. C++26 changes are labeled separately. Concrete sizes and performance observations describe a stated platform or a typical implementation, rather than universal language guarantees. CE means a compile-time diagnostic is required, UB means undefined behavior, and NDR means no diagnostic is required.

The additional syntax examples are independent sketches, including deliberately invalid cases. They are not intended to compile as one program. Practice logs preserve earlier answers and observations; corrections in the concept notes take precedence over historical shorthand.

For a missed question, make an Anki card with the question on the front and a short explanation of the mechanism on the back. The card supplements the notes rather than replacing their coverage.

## Files

| File | Owns |
|---|---|
| [build_linkage.md](build_linkage.md) | build pipeline, ODR, inline, preprocessor/macros, headers, identifiers, namespaces |
| [types_conversions.md](types_conversions.md) | promotions, signed/unsigned, shifts, fixed-width ints, enums, bools, overload ranks |
| [floating_point.md](floating_point.md) | IEEE-754, numeric_limits, float traps |
| [initialization_deduction.md](initialization_deduction.md) | init forms, narrowing, designated init, vexing parse, auto/auto&/auto&&, static init phases, constinit, thread_local |
| [value_categories.md](value_categories.md) | identity, lvalue/xvalue/prvalue, glvalue/rvalue diagram, reference binding, std::move, reference collapsing, forwarding references |
| [expressions.md](expressions.md) | sequencing, maximal munch, comma/ternary, ++/--, operator overloading |
| [control_flow.md](control_flow.md) | if/else, early return, switch (labels, fallthrough, [[fallthrough]], case scoping), while/do-while/for, break/continue, halts (exit/abort/terminate) |
| [memory_layout.md](memory_layout.md) | sizeof, padding/alignment, vptr, virtual bases, EBO, reference storage, memory segments / stack vs heap |
| [bits_punning.md](bits_punning.md) | bitset, bitwise promotion, strict aliasing, reinterpret_cast, memcpy, bit_cast |
| [functions_scope_lambdas.md](functions_scope_lambdas.md) | calls/ABI, RVO/NRVO, scope/duration/linkage, lambdas, tuple |
| [pointers_references.md](pointers_references.md) | pointers vs references, null/dangling/wild, const×pointer matrix, function pointers, pass by address, nullptr_t overloads |
| [error_handling.md](error_handling.md) | std::optional (access tiers, in_place, monadic ops), std::expected (C++23), exceptions (matching, unwinding, rethrow, function try, throwing dtors, cost model) |
| [ub_catalog.md](ub_catalog.md) | behavior taxonomy + master UB list with pointers |
| [smart_pointers_move.md](smart_pointers_move.md) | why raw owning pointers fail, hand-rolled smart pointer, shallow copy → double delete, auto_ptr history (copy-as-move, removed C++17), why C++11 added rvalue references, unique_ptr move example, std::move versus the move operation (swap, push_back, when to use), move ctor/assign (steal-and-null, noexcept + vector), implicit move rules, rule of five/zero, implicit move on return, shared_ptr/weak_ptr overview |
| [allocators.md](allocators.md) | bump vs stack vs general-purpose reclamation, address alignment with headers, std::align, placement new, std::byte, uintptr_t, 24-byte ownership, pointer validation on free |

## Where is...? (every concept, A-Z)

- ABI / RAX:RDX struct return → functions_scope_lambdas
- ADL (friend found only by) → expressions (operator overloading)
- aggregate rules → initialization_deduction
- alignment / alignof / alignas → memory_layout (data), bits_punning (casts)
- alignment in allocators (align the address not the size; user-address-first with headers; round-up sentence; std::align) → allocators
- aliasing (strict) rule + audit checklist → bits_punning
- allocator taxonomy: bump (bulk reclamation) vs stack (pop top only) vs general-purpose (reuse freed blocks) → allocators
- Anki-priority repeat miss: auto& keeps const → initialization_deduction
- anonymous namespace / internal linkage → build_linkage
- argv[argc] == 0 guarantee (null-terminated argv) → pointers_references
- array decay / pointer arithmetic (&x+1 vs x+1 stride) → pointers_references
- ASCII anchors ('A'=65, 'a'=97, '0'=48) → types_conversions
- assignment vs initialization → initialization_deduction (+ build_linkage traps)
- auto / auto& / const auto& / auto&& (legal-binding model) → initialization_deduction
- auto_ptr (copy-as-move, pass-by-value steals, delete not delete[], deprecated C++11 / removed C++17) → smart_pointers_move
- bump allocator (cursor allocation; optional headers and deallocation without individual space reclamation) → allocators
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
- circular reference / shared_ptr cycle leak (self-reference case; fix with weak_ptr one direction) → smart_pointers_move
- comma operator (precedence, return a,b) → expressions
- comments don't nest / #if 0 → build_linkage
- const return-by-value can block moves (distinguish direct prvalue construction) → initialization_deduction
- const value param: top-level const not in signature (header/impl mismatch legal) → initialization_deduction
- const vs constexpr vs constinit (globals) → initialization_deduction
- constant expressions (what qualifies, required contexts, as-if optional folding, const-integral exception vs const double) → initialization_deduction
- constexpr variables (must have constant initializer, implicitly const, not part of the type, any literal type, no params, string/vector limits) → initialization_deduction
- cv-qualified / cv-unqualified vocabulary; volatile ≠ threads → initialization_deduction
- constant-init / zero-init / dynamic-init phases (statics) → initialization_deduction
- conversion vs promotion ranks (overloads) → types_conversions
- copy elision (guaranteed) vs NRVO → functions_scope_lambdas
- const × pointer matrix (ptr-to-const vs const-ptr, right-to-left) → pointers_references
- const ref = read-only view not immutability (aliasing writes visible) → pointers_references
- dangling pointer (distinguish ended lifetime from released storage) → pointers_references
- data races → ub_catalog (pointer)
- default args don't apply through function pointers → pointers_references
- default-init vs value-init (uninitialized scalar vs zero) → initialization_deduction
- designated initializers (all 6 CE cases) → initialization_deduction
- do-while (semicolon, scope-outside-block gotcha) → control_flow
- double delete from shallow-copied owning pointer → smart_pointers_move
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
- forwarding references / std::forward / reference collapsing → value_categories
- forward progress rule (including the C++26 trivial-loop exception) → control_flow, ub_catalog
- function pointers (syntax, decay, overload disambiguation, no void* conversion) → pointers_references
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
- jump table (one possible switch implementation) → control_flow
- keywords & special identifiers → build_linkage
- lambdas (captures, mutable, sizes, passing, generic, constexpr) → functions_scope_lambdas
- lifetime extension (eligible temporary bindings; does not renew through a reference return) → initialization_deduction, pointers_references
- lvalue / xvalue / prvalue and glvalue / rvalue diagram → value_categories
- lvalue references (no reseat, binding rules, conversion-temporary trap) → pointers_references
- loop counters (signed! unsigned >= 0 bug) → control_flow
- linkage (none/internal/external) → functions_scope_lambdas (+ build_linkage)
- lvalue ternary / prefix++ returns lvalue → expressions
- magic number / canary in allocator headers (constant tag, double-free detection, address-dependent strengthening, bitmap for exactness) → allocators
- macro scope (none) → build_linkage
- make_unique (type once, no naked new, pre-C++17 argument exception-safety hole) → smart_pointers_move
- max/min tie-breaking (first arg) + const& return dangling → pointers_references
- monadic optional ops and_then/transform/or_else, nested-optional trap → error_handling
- malloc/free (size tracked by allocator, brk/sbrk/mmap, calloc/realloc) → memory_layout
- memory errors, the OSTEP seven (overflow, leak, dangling, double/invalid free) → memory_layout, ub_catalog
- main() specialness → build_linkage
- maximal munch (x+++++y, a+++b, >>) → expressions
- memcpy as blessed pun → bits_punning
- memory segments (code/data/BSS/heap/stack) → memory_layout
- memory leaks: pointers vs pointees → functions_scope_lambdas traps
- most vexing parse → initialization_deduction
- placement new (construct in existing storage; keep its returned pointer; buffer owner releases storage) → allocators
- pointer validation on free (uintptr_t explained, range/alignment/magic checks, null contract, exactness limits) → allocators
- moved-from state ("valid but unspecified"; unique_ptr guaranteed null; SSO copy) → ub_catalog
- move constructor / move assignment (syntax, steal-and-null, when selected, self-move check, swap recursion trap) → smart_pointers_move
- implicit move operations (suppressed by any user-declared copy/move/dtor; memberwise; raw pointer copied not nulled) → smart_pointers_move
- implicit move on return (local lvalue treated as rvalue; don't write return std::move) → smart_pointers_move, value_categories
- NaN != NaN / signed zero → floating_point
- narrowing (list-init CE, value-checked) → initialization_deduction
- noexcept on move operations (vector reallocation, move_if_noexcept, strong exception guarantee) → smart_pointers_move
- NDR (ill-formed, no diagnostic) → ub_catalog, build_linkage
- cout << functionName prints 1 (fp→bool, no void* conversion) → pointers_references
- nullptr vs NULL vs 0 (overload resolution) / std::nullptr_t (prvalue, not a pointer type) → pointers_references
- destructor exception specifications (implicit noexcept and termination cases) → error_handling
- nullopt / bad_optional_access / value_or / in_place / emplace → error_handling
- optional (std::optional, all of it) → error_handling
- numeric_limits quartet → floating_point
- ODR rules 1/2/3 → build_linkage
- operator overloading (homes, can't-overload list, && short-circuit loss, <=>) → expressions
- operator void() oddity → initialization_deduction
- overload ambiguity foo(-1.5) → types_conversions
- padding / tail padding / offsets / pahole → memory_layout
- pass by address (null-check patterns, optional params, int*& reseating) → pointers_references
- pass by value vs const& (2×pointer cheap-to-copy rule, string_view by value) → pointers_references
- out params / in-out params (why discouraged) → pointers_references
- pointer indirection cost x->foo() vs y.foo() (locality, SROA/aliasing) → memory_layout
- pointers vs references (object vs name; the 5 differences) → pointers_references
- pointers-to-int (uintptr_t round-trip) → bits_punning
- popcount / <bit> / countl_zero → bits_punning
- prefix vs postfix ++ (lvalue/rvalue, class-type cost) → expressions
- range-based for (auto/auto&/const auto&, decayed-array CE, no index, views::reverse, C++23 temporary fix) → control_flow
- recursion (stack depth, static-local memo, no guaranteed TCO, --x sequencing trap) → functions_scope_lambdas
- preprocessor pipeline & translation phases → build_linkage
- promotion flips comparison (unsigned short a-b) → types_conversions
- references: sizeof(int&) vs reference members → memory_layout
- reinterpret_cast legal-pattern checklist → bits_punning
- RAII for heap memory (why smart pointers exist; early return / exception skips delete) → smart_pointers_move (unwinding: error_handling)
- rule of five / rule of zero (declare one special member, decide all five; deleted move blocks copy fallback) → smart_pointers_move
- rvalue references (syntax, binding rules, lifetime extension, modify through non-const, named is lvalue, don't return one) → value_categories
- reverse iteration (views::reverse, rbegin/rend, base() off-by-one, i-- > 0 idiom) → control_flow
- reserved identifiers (_x, _X, __) → build_linkage
- rethrow (bare throw vs throw e slicing) → error_handling
- return by reference / address (lifetime conditions, static-local aliasing, assignment through T&) → pointers_references
- RVO / NRVO / -fno-elide-constructors → functions_scope_lambdas
- scope vs duration vs lifetime → functions_scope_lambdas
- sequencing (C++14 vs C++17 table) → expressions
- sequential/stacked case labels (≠ fallthrough) → control_flow
- shadowing / -Wshadow → functions_scope_lambdas
- shifts (count rule, value rules, x86 masking) → types_conversions
- signature (excludes return type) → build_linkage
- size_t underflow loops → types_conversions
- sizeof class rules / vptr / vbase / EBO / [[no_unique_address]] → memory_layout
- smart pointers: copyable-with-count vs move-only fork (shared_ptr vs unique_ptr), why C++11 needed rvalue refs → smart_pointers_move
- shared_ptr<void> / type erasure of pointee and deleter (why it works, why unique_ptr<void> doesn't, no CTAD from raw pointer) → smart_pointers_move
- shared_ptr (control block, two-raw-pointer double delete, make_shared single allocation + weak_ptr caveat, 16 bytes, deleter in block not type, atomic count = thread-safe count not object, pass by const& or T*, unique→shared only) → smart_pointers_move
- stack unwinding (search-then-unwind, dtors per frame, zero-cost tables) → error_handling
- stack vs heap (SP mechanics, frame contents, sizes, overflow, OSTEP 14.1) → memory_layout
- static init order fiasco → functions_scope_lambdas (+ build_linkage)
- static local in generic lambda (per-instantiation) → functions_scope_lambdas
- static members (not in sizeof) → memory_layout
- std::function costs / bad_function_call → functions_scope_lambdas
- std::move (expression cast versus actual move; named rvalue references) → value_categories, smart_pointers_move
- string literal = lvalue in .rodata; std::string temporary = prvalue (stack object, SSO/heap payload) → memory_layout
- strings: literals deduce const char*, ""s/""sv → initialization_deduction
- SSO (small string optimization; data() inside the object) → memory_layout
- std::align (rounds pointer up, shrinks space by padding, nullptr if no fit) → allocators
- std::byte (raw-memory type, bitwise operations, representation access, byte-stride pointer) → allocators
- structured bindings / std::tie / std::ignore / tie-comparator → functions_scope_lambdas
- switch (condition types, default, execution flow) → control_flow
- tail call optimization (not guaranteed in C++) → functions_scope_lambdas
- terminate (uncaught throw; unwind impl-defined) → error_handling
- ternary (precedence, branch unification, lvalue) → expressions
- thread_local (per-thread copy, lazy locals, fs-segment access) → initialization_deduction
- top-level vs low-level const (deduction drop rules, auto* vs auto) → initialization_deduction
- tuple (get rules, apply, CE list, forward_as_tuple dangling) → functions_scope_lambdas
- UB taxonomy + master list → ub_catalog
- unique_ptr ownership (sink vs borrow params, param-destruction timing) → pointers_references
- unique_ptr API (get/reset/release, bool, T[], returning by value, as member → move-only + pimpl, custom deleter and size, misuses) → smart_pointers_move
- unique_ptr<std::byte[]> as buffer owner (verify 24-byte layout; matching delete[]; no ownership flag) → allocators
- uninitialized reads → initialization_deduction, ub_catalog
- unsigned wrap (arithmetic + conversion) → types_conversions
- weak_ptr (cycle breaking, lock() over expired(), keeps control block not object, make_shared storage caveat, enable_shared_from_this / bad_weak_ptr) → smart_pointers_move
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
| Pointers / pass-by-address / function pointers (learncpp 12.7-12.11, 20.1 — read 02/09) | pointers_references | &x+1 vs x+1 ok |
| Dev problem: Bump Memory Allocator (07/09) | allocators | solved with guidance; 1 hidden-test fail on Deallocate(nullptr) |

## Quizzes

| Date | Quiz | Score | Time | Percentile | Notes |
|---|---|---|---|---|---|
| 29/08/2026 | Beginner C++ (getcracked) | 11/20 | 18:11 | top 9.7% of 248 ("Cracked") | Baseline, cold. 2 coding Qs skipped. Missed: full-specialization member def (no `template<>`), fold `sum(2,0.5,..)` is double (arith conversions per `+`), macro double-eval `121`, `delete` on `malloc`, `const alias` = top-level const (`int* const`), `class A; struct A{}` same entity. Priority: Templates, Pointers/const, new/delete, Classes. Retake after tree. |
| 31/08/2026 | Claude notes quiz #1 (11 Q) | 8 clean | ~30m | — | MISSED: SQUARE(2+3)=11 (macro paste), auto& keeps const (REPEAT). Precision dings: padding offsets map, 1<<31=INT_MIN, NRVO vs guaranteed elision. |
| 01/09/2026 | Claude quiz #2 (10 Q, day's material + exceptions) | 8.5/10 | ~30m | — | HALVES: catch(...)-first is CE not catch-everything; uncaught→unwind impl-defined (dtors not guaranteed); switch decl-vs-init terminology + "garbage" for UB (REPEAT). Clean: ctor-throw member destruction, exit cleanup order, segments, access tiers, and_then retest, slicing rethrow, constinit. |

## Template for each concept file

```markdown
# <Concept>

## <First concept or mechanism>

Explain what it is, how it works, and why it matters in full sentences.
Place a small example beside the explanation and walk through its result.

## <Related concepts and practical choices>

Cover the topic independently of which interview questions are included.
Keep important caveats near the rule, and label version or ABI assumptions.

## Errors and pitfalls

Distinguish invalid programs, undefined behavior, permitted variation,
and ordinary logical errors. Explain why each example belongs there.

## Additional syntax examples

Keep useful independent syntax sketches, clearly marking invalid cases.

## Interview Q&A

### <Question>

Give a natural spoken answer with the reasoning and practical consequence.
Include follow-up questions where they help reinforce the topic.

## Practice history

Preserve dated quizzes, missed questions, and Anki reminders here.
```

The concept index and quiz tables are navigation and history, so their compact labels are intentional.
