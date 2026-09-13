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
| [strings.md](strings.md) | literal vs const char* vs std::string vs string_view, constructor table and its traps, size/capacity/access, editing, find/npos, compare, stoi vs from_chars vs stringstream |
| [iostreams.md](iostreams.md) | stream hierarchy and standard streams, formatted vs unformatted input, getline/ignore/peek, flags and manipulators, precision, width/fill/alignment, flushing; file streams and modes; filesystem paths, queries, operations, and traversal |
| [allocators.md](allocators.md) | bump vs stack vs general-purpose reclamation, address alignment with headers, std::align, placement new, std::byte, uintptr_t, 24-byte ownership, pointer validation on free |
| [classes.md](classes.md) | procedural vs OOP, class invariants, struct vs class (defaults only, class-key mismatch legal), member functions and the implicit object / this, in-class = inline, declaration-order init UB, const member functions / mutable, access specifiers (per-class rule), access functions, returning references to members (dangling from temporaries), data hiding vs encapsulation, prefer non-member functions, constructors (non-aggregate, never const), member initializer lists (declaration order, three-source priority, body assignment is worse), default constructors (one only, implicit vs = default vs user-provided and zero-init), delegating constructors, temporaries + six init forms for class types, copy constructor (reference param, = default / = delete), converting constructors + explicit (one user-defined conversion), destructors (reverse order, implicit, std::exit skips), nested types (class as scope, nested enum/alias/class, no outer this but member access), friends (non-member, class, member-function friends and the ordering fix; not reciprocal/transitive/inherited), the four overload aspects (arity, param types w/o top-level const, cv-qualifier, ref-qualifier), & / && ref-qualifiers, pointers to member functions (.* ->* std::invoke std::mem_fn, C++23 explicit object parameter) |
| [arrays.md](arrays.md) | C-style array declaration/init rules (constexpr length, `int i[0]` ill-formed, omitted length, value-init), sizeof vs std::size/ssize, decay (four non-decay contexts, parameter adjustment, length loss, auto vs auto&, typeid), pointer arithmetic and subscripting (`a[n]` = `*(a+n)`, `n[a]`, relative indices, negative index, begin/end traversal, range-for expansion, multidim flattening), multidimensional arrays (row-major, nested braces, `int (*)[3]` decay, row-pointer subscripts), variable-length arrays (stack pointer bump, extension), heap arrays (`delete[]` needs the original pointer) and stack limits (huge local array) |
| [containers.md](containers.md) | std::array (aggregate, constexpr, CTAD, to_array, double braces / brace elision, size_type, at vs [] vs std::get, passing by template T/N, returning copies) and std::vector (list ctor vs explicit length ctor, {10} vs (10), at vs [], unsigned size_type / ssize, pass by const&, return by value moves, resize vs reserve, capacity and reallocation, push_back vs emplace_back, braced-list evaluation order) |
| [inheritance.md](inheritance.md) | base pointers see static type, virtual functions and exact-signature overrides (const counts), implicit virtual, covariant returns, default args bind statically, slicing, no virtual calls in ctor/dtor, override/final, devirtualization and inlining, multiple inheritance + diamond (ABACD), virtual destructors + Sutter's rule, calling Base::f explicitly |
| [templates.md](templates.md) | function templates: primary/instantiation, deduction never converts, `<>` vs plain call and non-template preference, static locals per instance, multiple type params + auto return, abbreviated templates, partial ordering, non-type params (auto, converted constant expressions, ambiguity), templates in headers + implicit inline, full specialization (`template<>`, same signature, not inline), member function templates cannot be virtual |

## Where is...? (every concept, A-Z)

- [[fallthrough]] attribute / fallthrough rules → control_flow
- [except.ctor] return-object-destroyed-by-unwinding rule (bcad; compilers non-conforming) → error_handling
- `delete[]` must get the pointer `new[]` returned (`arr++; delete[] arr;` UB); array of shared_ptr still needs `delete[]` → arrays
- `obj(i);` declares a variable named i (parenthesized declarator), not a temporary → classes
- abbreviated function templates (`auto` parameters, C++20) → templates
- ABI / RAX:RDX struct return → functions_scope_lambdas
- access functions / getters and setters (naming styles, behavior over setAlive, value vs const& return) → classes
- access specifiers (public/private/protected; per-class not per-object; struct/class default) → classes
- ADL (friend found only by) → expressions (operator overloading)
- aggregate rules → initialization_deduction
- aliasing (strict) rule + audit checklist → bits_punning
- alignment / alignof / alignas → memory_layout (data), bits_punning (casts)
- alignment in allocators (align the address not the size; user-address-first with headers; round-up sentence; std::align) → allocators
- allocator taxonomy: bump (bulk reclamation) vs stack (pop top only) vs general-purpose (reuse freed blocks) → allocators
- Anki-priority repeat miss: auto& keeps const → initialization_deduction
- anonymous namespace / internal linkage → build_linkage
- argv[argc] == 0 guarantee (null-terminated argv) → pointers_references
- array decay (four non-decay contexts: sizeof, typeid, unary &, class member, reference binding; parameter `int arr[]` is `int*`) → arrays; &x+1 vs x+1 → pointers_references
- array decay / pointer arithmetic (&x+1 vs x+1 stride) → pointers_references
- array length: sizeof idiom vs std::size / std::ssize (refuse pointers) vs template `T(&)[N]` → arrays
- ASCII anchors ('A'=65, 'a'=97, '0'=48) → types_conversions
- assignment vs initialization → initialization_deduction (+ build_linkage traps)
- at() vs operator[] (bounds check + throw vs UB; both return references) → containers
- auto / auto& / const auto& / auto&& (legal-binding model) → initialization_deduction
- auto_ptr (copy-as-move, pass-by-value steals, delete not delete[], deprecated C++11 / removed C++17) → smart_pointers_move
- basic_string template / char types / raw string literals R"()" → strings
- bit_cast → bits_punning
- bitset (set/reset/flip/test, sizeof, [] vs test) → bits_punning
- bool (boolalpha, cin failure, non-0/1 byte UB) → types_conversions
- braced initializer list evaluates left to right (function args do not) → containers
- braces: auto x{1,2} / initializer_list → initialization_deduction
- break vs return (switch + loops, innermost-only, no labeled break) → control_flow
- bump allocator (cursor allocation; optional headers and deallocation without individual space reclamation) → allocators
- C-style array declaration (constexpr length, `int i[0]` ill-formed, omitted length, too many initializers, `auto arr[]` invalid) → arrays
- case labels (constant, unique, '6'==54 collision) → control_flow
- case scoping / init-in-case CE / explicit block fix → control_flow
- catch matching (no conversions, derived→base, const&) / catch-all must be last → error_handling
- char arithmetic & promotion → types_conversions
- CHAR_BIT / byte width (≥8 through C++23, exactly 8 in C++26; digits vs CHAR_BIT; exact-width types optional, least/fast always) → types_conversions
- circular reference / shared_ptr cycle leak (self-reference case; fix with weak_ptr one direction) → smart_pointers_move
- class invariant (why classes over structs) → classes
- class vs struct (only default access differs; `class A; struct A{}` same entity, -Wmismatched-tags) → classes
- comma operator (precedence, return a,b) → expressions
- comments don't nest / #if 0 → build_linkage
- conditional operator value category (lvalue only if both branches same-type lvalues; mixed → prvalue copy, const& binds temporary not x) → expressions
- conditional operator with two class types (`flag ? C{} : D{}` converts toward the reachable type; auto deduces it) → expressions, classes (Q&A)
- const / constexpr / consteval / constinit four-way table; constinit not usable in constant expressions; keyword combinations → initialization_deduction
- const member functions / mutable / this is const X* → classes
- const ref = read-only view not immutability (aliasing writes visible) → pointers_references
- const return-by-value can block moves (distinguish direct prvalue construction) → initialization_deduction
- const value param: top-level const not in signature (header/impl mismatch legal) → initialization_deduction
- const vs constexpr vs constinit (globals) → initialization_deduction
- const × pointer matrix (ptr-to-const vs const-ptr, right-to-left) → pointers_references
- const-default-constructible (`const C c;` needs user-provided ctor or member initializers; `= default` is not user-provided) → classes
- constant expressions (what qualifies, required contexts, as-if optional folding, const-integral exception vs const double) → initialization_deduction
- constant-init / zero-init / dynamic-init phases (statics) → initialization_deduction
- consteval / immediate functions (must be compile time, functions only, no address) → initialization_deduction
- constexpr functions (may run at compile time or run time; constexpr vs const member functions) → initialization_deduction
- constexpr variables (must have constant initializer, implicitly const, not part of the type, any literal type, no params, string/vector limits) → initialization_deduction
- constructor basics (runs after storage exists; class name, no return type; never const; any ctor makes non-aggregate) → classes
- continue (runs for's end-expression; while-loop infinite-loop trap) → control_flow
- conversion vs promotion ranks (overloads) → types_conversions
- converting constructor / one user-defined conversion per implicit sequence (`printEmployee("Joe")` fails) → classes
- copy constructor (memberwise implicit; must take reference; = default / = delete; no side effects) → classes
- copy elision (guaranteed) vs NRVO → functions_scope_lambdas
- copy-initialization `C c2 = c1;` is one copy-constructor call, not construct-then-assign → classes
- cout << functionName prints 1 (fp→bool, no void* conversion) → pointers_references
- covariant return types (pointer/reference to derived; static return type at the call) → inheritance
- cv-qualified / cv-unqualified vocabulary; volatile ≠ threads → initialization_deduction
- dangling pointer (distinguish ended lifetime from released storage) → pointers_references
- data hiding vs encapsulation (five benefits; public-first member order; prefer non-member functions) → classes
- data races → ub_catalog (pointer)
- declaration vs out-of-class definition (names, top-level const incl. `int* const`, default argument once, cv/ref/noexcept must match) → classes
- deduction never converts (`max(2, 3.5)` fails; explicit `<double>` or two params + auto) → templates
- default args don't apply through function pointers → pointers_references
- default arguments on virtual functions bind statically (`D1`) → inheritance
- default constructor (only one allowed; all-defaulted params count; implicit one suppressed by any ctor; `= default` vs empty body zero-init difference) → classes
- default-init vs value-init (uninitialized scalar vs zero) → initialization_deduction
- delegating constructors (`: Foo{...}` in the initializer list; delegate or initialize, not both; body-call makes a temporary) → classes
- designated initializers (all 6 CE cases) → initialization_deduction
- destructor basics (~T, one per class, reverse order, implicit runs member dtors, std::exit skips locals) → classes; throwing dtors → error_handling
- destructor exception specifications (implicit noexcept and termination cases) → error_handling
- devirtualization / final / can virtual functions be inlined → inheritance
- diamond inheritance (two base subobjects, ABACD, ambiguity; virtual base fixes) → inheritance
- do-while (semicolon, scope-outside-block gotcha) → control_flow
- double delete from shallow-copied owning pointer → smart_pointers_move
- early return → control_flow
- emplace_back vs push_back (in-place, uses explicit ctors, no aggregate before C++20) → containers
- endian / std::endian → bits_punning
- endl vs '\n' → build_linkage
- enum / enum class / to_underlying / using enum → types_conversions
- epsilon vs denorm_min vs min vs lowest → floating_point
- erroneous behavior (C++26) → ub_catalog, types_conversions
- exceptions (all of it: throw/try/catch, unwinding, terminate, cost model) → error_handling
- EXIT_SUCCESS / status codes → build_linkage
- expected (std::expected/unexpected/unexpect, error(), transform_error) → error_handling
- explicit constructors (blocks copy-init, copy-list-init, implicit args, `return {x}`; allows direct, direct-list, T{x}, static_cast) → classes
- explicit destructor call `a.~A()` on an automatic object = double destruction UB (placement-new the only legitimate follow-up) → classes, ub_catalog
- explicit object parameter (C++23 `this X& self`; member pointer becomes plain function pointer) → classes
- file streams (ifstream/ofstream/fstream, RAII, open modes, text vs binary, buffering, safe read loops) → iostreams
- filesystem (path composition/decomposition, queries and mutations, error_code overloads, directory traversal, race/symlink pitfalls) → iostreams
- fixed-point prices ×10^4 (ITCH/venues) → floating_point traps
- fixed-width ints / size_t / ptrdiff_t / uint8_t-prints-as-char → types_conversions
- float→int out-of-range UB → floating_point
- fold expressions (quiz miss context) → README quiz table
- for loop (order of parts, omitted parts, multi-counter comma, != vs <) → control_flow
- forward declarations → build_linkage
- forward progress rule (including the C++26 trivial-loop exception) → control_flow, ub_catalog
- forwarding references / std::forward / reference collapsing → value_categories
- friend functions / friend classes / friend member functions (granted by the accessed class; not reciprocal, transitive, or inherited; ordering fix for friend member) → classes; hidden friends + ADL → expressions
- full specialization (`template<>`, same signature, not implicitly inline; prefer non-template overload) → templates
- function pointers (syntax, decay, overload disambiguation, no void* conversion) → pointers_references
- function try blocks (ctor init-list catches, implicit rethrow) → error_handling
- function-like macros (paste, double-eval, SQUARE=11) → build_linkage
- getter returning const& (match member type; dangling when called on a temporary; never non-const& to private) → classes
- halts: std::exit / atexit / abort / terminate / quick_exit (cleanup matrix, RAII break) → control_flow
- header guards / #pragma once → build_linkage
- huge local array → stack overflow at frame entry (`int a[10000000]`) → arrays; stack vs heap → memory_layout
- IEEE-754 layout, bias, hidden bit, subnormals, Inf/NaN, round-to-even → floating_point
- if (x) non-bool condition conversion → control_flow
- if-else vs switch (when to use which) → control_flow
- implicit copy assignment on an owning raw pointer (`B = A` leaks B's array, shares A's, double delete) → classes (Q&A), smart_pointers_move
- implicit move on return (local lvalue treated as rvalue; don't write return std::move) → smart_pointers_move, value_categories
- implicit move operations (suppressed by any user-declared copy/move/dtor; memberwise; raw pointer copied not nulled) → smart_pointers_move
- implicit object / this / member access before declaration → classes
- infinite loops (while(true) idiom, semicolon null-body, unsigned counter wrap) → control_flow
- initialization forms for class types (six forms; copy forms skip explicit; list forms reject narrowing, prefer initializer_list) → classes
- initializer_list copies elements at construction; copying the list copies only the handle → classes
- inline (ODR meaning, requirements, why not everything) → build_linkage
- input/output streams (hierarchy, cin/cout/cerr/clog, >> vs get/getline, ignore/peek/unget/putback, flags/manipulators, precision/width/fill/alignment, flush/endl) → iostreams
- integral promotion (sub-int → signed int) → types_conversions
- jump table (one possible switch implementation) → control_flow
- keywords & special identifiers → build_linkage
- lambdas (captures, mutable, sizes, passing, generic, constexpr) → functions_scope_lambdas
- lifetime extension (eligible temporary bindings; does not renew through a reference return) → initialization_deduction, pointers_references
- linkage (none/internal/external) → functions_scope_lambdas (+ build_linkage)
- loop counters (signed! unsigned >= 0 bug) → control_flow
- lvalue / xvalue / prvalue and glvalue / rvalue diagram → value_categories
- lvalue references (no reseat, binding rules, conversion-temporary trap) → pointers_references
- lvalue ternary / prefix++ returns lvalue → expressions
- macro scope (none) → build_linkage
- magic number / canary in allocator headers (constant tag, double-free detection, address-dependent strengthening, bitmap for exactness) → allocators
- main() specialness → build_linkage
- make_unique (type once, no naked new, pre-C++17 argument exception-safety hole) → smart_pointers_move
- malloc/free (size tracked by allocator, brk/sbrk/mmap, calloc/realloc) → memory_layout
- max/min tie-breaking (first arg) + const& return dangling → pointers_references
- maximal munch (x+++++y, a+++b, >>) → expressions
- member function defined in-class is implicitly inline → classes
- member functions: overload aspects (arity, param types, cv-qualifier, ref-qualifier; top-level const dropped) → classes
- member initializer list (colon syntax, braces not `=`; declaration order not list order; list > default member initializer > default-init) → classes
- memcpy as blessed pun → bits_punning
- memory errors, the OSTEP seven (overflow, leak, dangling, double/invalid free) → memory_layout, ub_catalog
- memory leaks: pointers vs pointees → functions_scope_lambdas traps
- memory segments (code/data/BSS/heap/stack) → memory_layout
- monadic optional ops and_then/transform/or_else, nested-optional trap → error_handling
- most vexing parse `Y y(X());` (function taking X(*)(), error at y.f()) → initialization_deduction (+ classes Q&A)
- most vexing parse → initialization_deduction
- move constructor / move assignment (syntax, steal-and-null, when selected, self-move check, swap recursion trap) → smart_pointers_move
- move ctor forwarding by name (`Base(other)` copies; needs `Base(std::move(other))`) → classes; named rvalue ref is an lvalue → value_categories
- moved-from state ("valid but unspecified"; unique_ptr guaranteed null; SSO copy) → ub_catalog
- multidimensional array pointer arithmetic (`int(*p)[5][2]`, p+1 skips a block, flatten the index) → arrays
- multidimensional arrays (row-major, leftmost length omission, `int (*)[3]`, `a[y][x]`) → arrays
- mutable (modify from const member function) → classes
- NaN != NaN / signed zero → floating_point
- narrowing (list-init CE, value-checked) → initialization_deduction
- NDR (ill-formed, no diagnostic) → ub_catalog, build_linkage
- nested types (enum, alias, class inside a class; `Outer::Type`; nested class has no outer `this` but has member access; forward-declare only inside or after) → classes
- noexcept on move operations (vector reallocation, move_if_noexcept, strong exception guarantee) → smart_pointers_move
- non-type template parameters (constexpr values, `auto` C++17, converted constant expressions, overload ambiguity) → templates
- nullopt / bad_optional_access / value_or / in_place / emplace → error_handling
- nullptr vs NULL vs 0 (overload resolution) / std::nullptr_t (prvalue, not a pointer type) → pointers_references
- numeric_limits quartet → floating_point
- ODR rules 1/2/3 → build_linkage
- operator overloading (homes, can't-overload list, && short-circuit loss, <=>) → expressions
- operator void() oddity → initialization_deduction
- optional (std::optional, all of it) → error_handling
- out params / in-out params (why discouraged) → pointers_references
- overload ambiguity foo(-1.5) → types_conversions
- override (exact signature incl. const; error when nothing overridden; implies virtual) → inheritance
- padding / tail padding / offsets / pahole → memory_layout
- pass by address (null-check patterns, optional params, int*& reseating) → pointers_references
- pass by value vs const& (2×pointer cheap-to-copy rule, string_view by value) → pointers_references
- placement new (construct in existing storage; keep its returned pointer; buffer owner releases storage) → allocators
- pointer indirection cost x->foo() vs y.foo() (locality, SROA/aliasing) → memory_layout
- pointer to member function (`&X::foo`, `(x.*mf)(42)`, `(px->*mf)(42)`, type `void (X::*)(int)`, 16 bytes Itanium) → classes
- pointer validation on free (uintptr_t explained, range/alignment/magic checks, null contract, exactness limits) → allocators
- pointers vs references (object vs name; the 5 differences) → pointers_references
- pointers-to-int (uintptr_t round-trip) → bits_punning
- popcount / <bit> / countl_zero → bits_punning
- prefix vs postfix ++ (lvalue/rvalue, class-type cost) → expressions
- preprocessor pipeline & translation phases → build_linkage
- promotion flips comparison (unsigned short a-b) → types_conversions
- RAII for heap memory (why smart pointers exist; early return / exception skips delete) → smart_pointers_move (unwinding: error_handling)
- range-based for (auto/auto&/const auto&, decayed-array CE, no index, views::reverse, C++23 temporary fix) → control_flow
- recursion (stack depth, static-local memo, no guaranteed TCO, --x sequencing trap) → functions_scope_lambdas
- ref-qualifiers `&` / `&&` on member functions (optional::value overloads, consume-only members) → classes
- references: sizeof(int&) vs reference members → memory_layout
- reinterpret_cast legal-pattern checklist → bits_punning
- reserve vs resize; capacity vs length; reallocation cost; shrink_to_fit non-binding → containers
- reserved identifiers (_x, _X, __) → build_linkage
- rethrow (bare throw vs throw e slicing) → error_handling
- return by reference / address (lifetime conditions, static-local aliasing, assignment through T&) → pointers_references
- reverse iteration (views::reverse, rbegin/rend, base() off-by-one, i-- > 0 idiom) → control_flow
- rule of five / rule of zero (declare one special member, decide all five; deleted move blocks copy fallback) → smart_pointers_move
- rvalue references (syntax, binding rules, lifetime extension, modify through non-const, named is lvalue, don't return one) → value_categories
- RVO / NRVO / -fno-elide-constructors → functions_scope_lambdas
- scope vs duration vs lifetime → functions_scope_lambdas
- sequencing (C++14 vs C++17 table) → expressions
- sequential/stacked case labels (≠ fallthrough) → control_flow
- shadowing / -Wshadow → functions_scope_lambdas
- shared_ptr (control block, two-raw-pointer double delete, make_shared single allocation + weak_ptr caveat, 16 bytes, deleter in block not type, atomic count = thread-safe count not object, pass by const& or T*, unique→shared only) → smart_pointers_move
- shared_ptr<void> / type erasure of pointee and deleter (why it works, why unique_ptr<void> doesn't, no CTAD from raw pointer) → smart_pointers_move
- shifts (count rule, value rules, x86 masking) → types_conversions
- signature (excludes return type) → build_linkage
- size_t underflow loops → types_conversions
- sizeof class rules / vptr / vbase / EBO / [[no_unique_address]] → memory_layout
- slicing (by-value Base parameter loses dynamic type) → inheritance
- smart pointers: copyable-with-count vs move-only fork (shared_ptr vs unique_ptr), why C++11 needed rvalue refs → smart_pointers_move
- special-member call trace (`x = T()` = ctor+move-assign+dtor; `return std::move(param)` moves, params never elided; param + discarded return value die at the call; `A b = A()` = one ctor) → classes (Q&A)
- SSO (small string optimization; data() inside the object) → memory_layout
- stack unwinding (search-then-unwind, dtors per frame, zero-cost tables) → error_handling
- stack vs heap (SP mechanics, frame contents, sizes, overflow, OSTEP 14.1) → memory_layout
- static init order fiasco → functions_scope_lambdas (+ build_linkage)
- static local in generic lambda (per-instantiation) → functions_scope_lambdas
- static local variables are per template instantiation → templates
- static members (not in sizeof) → memory_layout
- std::align (rounds pointer up, shrinks space by padding, nullptr if no fit) → allocators
- std::array (aggregate, constexpr length, CTAD, double braces, std::get compile-time check, pass as `<T, N>` template, returns copy) → containers
- std::byte (raw-memory type, bitwise operations, representation access, byte-stride pointer) → allocators
- std::function costs / bad_function_call → functions_scope_lambdas
- std::invoke / std::mem_fn / reference_wrapper is callable → classes
- std::move (expression cast versus actual move; named rvalue references) → value_categories, smart_pointers_move
- std::string API (size/capacity/reserve/resize, [] vs at, data/c_str invalidation, append/insert/erase/replace, substr, starts_with/contains, find/npos, compare/<=>) → strings
- std::string constructor overloads (const char* + count vs std::string + pos; (5,'a') vs ('a',5); prefer substr / iterator pair) → strings (table), initialization_deduction
- std::vector `{10}` vs `(10)`; explicit length ctor; `vector<const int>` invalid; not constexpr → containers
- string literal = lvalue in .rodata; std::string temporary = prvalue (stack object, SSO/heap payload) → memory_layout
- string ↔ number (stoi family throws; from_chars/to_chars non-throwing, locale-free, hot-path; to_string formatting; stringstream cost) → strings
- string_view (pointer + length, by value, implicit from literal/string, explicit back; remove_prefix/suffix and substr O(1); NOT null-terminated; lifetime tied to source) → strings (parameters: pointers_references)
- strings on the hot path (SSO limits per lib 15/22, growth, fixed char arrays in messages, string_view + from_chars zero-alloc parse, heterogeneous lookup is_transparent) → strings
- strings: literals deduce const char*, ""s/""sv → initialization_deduction
- struct: no constructors (keeps aggregate); no-data class → namespace → classes
- structured bindings / std::tie / std::ignore / tie-comparator → functions_scope_lambdas
- subscripting = `*((a)+(n))`: `n[a]`, `2["123"]`, relative/negative indices, `(*arr + 1)` trap → arrays
- switch (condition types, default, execution flow) → control_flow
- tail call optimization (not guaranteed in C++) → functions_scope_lambdas
- templates go in headers (instances implicitly inline; .cpp definition = link error) → templates
- temporary class objects (`T{}` vs `T()`, dies at end of full expression, prvalue) → classes; lifetime extension → initialization_deduction
- terminate (uncaught throw; unwind impl-defined) → error_handling
- ternary (precedence, branch unification, lvalue) → expressions
- thread_local (per-thread copy, lazy locals, fs-segment access) → initialization_deduction
- top-level vs low-level const (deduction drop rules, auto* vs auto) → initialization_deduction
- tuple (get rules, apply, CE list, forward_as_tuple dangling) → functions_scope_lambdas
- typeid on arrays (strips references; `int[2]` != `int[3]`; decayed `auto` is `int*`) → arrays
- UB taxonomy + master list → ub_catalog
- uninitialized reads → initialization_deduction, ub_catalog
- unique_ptr API (get/reset/release, bool, T[], returning by value, as member → move-only + pimpl, custom deleter and size, misuses) → smart_pointers_move
- unique_ptr ownership (sink vs borrow params, param-destruction timing) → pointers_references
- unique_ptr<std::byte[]> as buffer owner (verify 24-byte layout; matching delete[]; no ownership flag) → allocators
- unsigned wrap (arithmetic + conversion) → types_conversions
- variable-length array (extension; stack pointer adjusted, no heap) → arrays
- vexing parse → initialization_deduction
- virtual destructor: public virtual or protected non-virtual (Sutter); delete through base without it leaks/UB → inheritance
- virtual function resolution (most-derived between static and dynamic type; pointer/reference only; not in ctor/dtor) → inheritance
- virtual inheritance sizes → memory_layout
- virtual member function template is invalid; class template virtual dtor is fine → templates, inheritance
- vptr → memory_layout
- weak_ptr (cycle breaking, lock() over expired(), keeps control block not object, make_shared storage caveat, enable_shared_from_this / bad_weak_ptr) → smart_pointers_move
- while / do-while / for (full loop notes) → control_flow

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
| I/O Streams: Console (learncpp 28.1-28.3 — read 12/09) | iostreams | 4/5 ok; 1s in chat if you're cooked MISSED (uint8_t extraction) |
| I/O Streams: File (learncpp 28.6 — read 12/09) | iostreams | no questions |
| std::filesystem (C++ Stories — read 12/09) | iostreams | no questions |
| Classes and Structs (learncpp 14.1-14.2 — read 12/09) | classes | Class vs Struct ok, Struct over Class ok; Class inStruction MISSED, wtf const MISSED |
| Member Functions (learncpp 14.3 — read 12/09) | classes | X ways ok, skibidi pointer ok; Haha… MISSED, Invoke me. MISSED |
| Const Classes and Functions & Access Specifiers (learncpp 14.4-14.8 — read 12/09) | classes | & and && ok; Drop these. MISSED |
| Special Member Functions (learncpp 14.9-14.16, 15.4 — read 12-13/09) | classes + smart_pointers_move | 5 ok; wrong first attempt: Stop! Don't move!, Copying and Not Copying, r-expression, Tear it out root and stem, ? 1 : 2 -> auto, 96% of you will fail this., Who'd you call? |
| Friends and Enemies (learncpp 15.3, 15.8, 15.9 — read 13/09) | classes + expressions | no questions |
| C-Style Arrays (learncpp 17.7-17.9 — read 13/09) | arrays + pointers_references | 6 ok; wrong first attempt: Indexing arrays, [0]; 3D Space problem not attempted |
| Multidimensional C-Style Arrays (learncpp 17.12 — read 13/09) | arrays | What a Jump! ok |
| std::array (learncpp 17.1-17.4, 17.6 + Chen Inside STL — read 13/09) | containers + arrays | Array extensioooooons wrong first attempt |
| std::vector (learncpp 16.1-16.5, 16.10-16.11 — read 13/09) | containers | Don't @ me ok, Containers for containers. ok; A, B, C, initializer_list wrong first attempt; 2 problems not attempted |
| Multiple Inheritance (Issues) (learncpp 24.9 — read 13/09) | inheritance | In a Diamond ok |
| Base Class References & Pointers (learncpp 25.1-25.2 — read 13/09) | inheritance | 4/4 ok |
| Override and Final (learncpp 25.3 + MS final classes — read 13/09) | inheritance | We're virtually there. wrong first attempt; 3 not attempted |
| Virtual Destructor (learncpp 25.4 — read 13/09) | inheritance | Herb's Destructor ok |
| Templates: Functions (learncpp 11.6-11.10, 26.3 — read 13/09) | templates | Virtually a template. ok; 7 not attempted |

## Quizzes

| Date | Quiz | Score | Time | Percentile | Notes |
|---|---|---|---|---|---|
| 29/08/2026 | Beginner C++ (getcracked hub quiz; the tree's own end-of-tree quiz is separate and still 0/1) | 11/20 | 18:11 | top 9.7% of 248 ("Cracked") | Baseline, cold. 2 coding Qs skipped. Missed: full-specialization member def (no `template<>`), fold `sum(2,0.5,..)` is double (arith conversions per `+`), macro double-eval `121`, `delete` on `malloc`, `const alias` = top-level const (`int* const`), `class A; struct A{}` same entity. Priority: Templates, Pointers/const, new/delete, Classes. Retake after tree. |
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

<!-- gc-questions:start -->

## Questions without a concept file yet

Tree nodes not yet mapped to a concept file (mostly Intermediate material). When a file is created for one of these, add the mapping in `cpp/tools/gc_links.py`.

- **Internals** — 0/5 attempted
- **Iterator Categories** — 0/1 attempted
- **STL Algorithms** — 0/5 attempted
- **Hashing** — 0/1 attempted
- **std::unordered_map & std::map** — 0/3 attempted
- **std::set & std::unordered_set** — 0/2 attempted
- **std::queue, std::deque & std::priority_queue** — 0/1 attempted
- **Access Modifiers** — 0/1 attempted
- **Construction Order** — 0/7 attempted
- **Adding & Hiding Functionality** — 0/3 attempted
- **Pure Virtual Functions and Abstract Classes** — 0/1 attempted
- **Templates: Classes** — 0/6 attempted
- **Class Template Argument Deduction** — 0/2 attempted
- **Template Non-Type Parameters** — 0/1 attempted
- **Class Template Specialization** — 0/1 attempted
- **Partial Class Template Specialization** — 0/1 attempted
- **Variadic Templates** — 0/1 attempted
- **Templates and Pointers** — 0/1 attempted

<!-- gc-questions:end -->
