# Initialization & Type Deduction

## Objects, variables, init forms
- Object = storage holding a value; variable = named object; identifier = the name.
- Initialization (at creation, ctor) ≠ assignment (later, operator=). Same `=`, different mechanism.
- Forms: `int a = 5;` copy-init · `int a(5);` direct · `int a{5};` direct-list (**prefer**) · `int a{};` value-init → 0 · `int a;` default-init.
- Default-init: automatic/heap scalar → indeterminate (reading = UB); static/namespace storage → zero first; class types run default ctor. `struct S{int a; std::string b;}; S s;` in a function: `a` garbage, `b` empty.
- List-init forbids narrowing, checked on the VALUE for constant expressions: `int x{4L}` ok, `unsigned u{-1}` CE, `int y{4.5}` CE, `int z{dbl_var}` CE regardless of contents.
- Most vexing parse: whatever can be a function declaration, is. `std::string s();`, `Double d(MyInt(i));`. Fix: `{}` or extra parens. Direct-list-init of a temporary needs a one-word type: `unsigned int{5}` CE, `int{5}` fine (alias multi-word types).

## Static-storage init phases + constinit (cppstories storage-init, read 01/09)
- Non-local static/thread objects initialize in phases: **static initialization** first — either **constant-init** (value computable at compile time → baked into the data segment) or **zero-init** (everything else zeroed → BSS; pointers = nullptr) — then **dynamic initialization** at runtime before main for whatever couldn't be done at compile time (ctor calls, non-constexpr expressions).
- This is *why* "static storage → zero first" in the default-init rule above: statics are always at least zero-initialized before anything else runs.
- **Static init order fiasco** (→ functions_scope_lambdas): *dynamic* init order across translation units is unspecified — a global in TU1 whose initializer reads a dynamically-initialized global in TU2 may see it pre-init (zeroed). Constant-initialized globals are immune (done at compile time). Fixes: Meyers singleton (function-local static, lazy + thread-safe since C++11), or make the dependency constant-init.
- **const vs constexpr vs constinit (C++20)** on globals:
  - `const`: immutable, but init may still be dynamic (runtime). Gives internal linkage on non-extern globals.
  - `constexpr`: forces constant-init AND immutable.
  - `constinit`: forces constant-init (CE if the initializer isn't a constant expression) but stays **mutable** — "diagnose the fiasco away without giving up mutation". constexpr = constinit + const, roughly.
- **thread_local**: one object per thread, initialized when the thread starts (or lazily for function-locals, like static locals), destroyed at thread exit. `static thread_local` at namespace scope ≡ `thread_local` (static is implied). Uses: per-thread RNG, per-thread counters/scratch. Cost note: TLS access goes through a segment register (fs on x86-64 Linux) — cheap but not free.
- Linkage footnote: C++20 modules add **module linkage** to the none/internal/external trio.

## Aggregates & designated initializers (C++20)
- Aggregate = array, or class with: no private/protected non-static members, no user-declared ctors, no virtual/private/protected bases, no virtual functions (default member initializers OK since C++14).
- `T o{.a = 1, .b{2}}`: aggregates only, non-static members, declaration order, may skip (skipped → default member init, else value-init), no positional mix, no duplicates, no nesting (C-only).

## auto deduction — ask "what type makes this binding legal and exact?"
For `const std::string& src`:
- `auto x = src` → `std::string` — VALUE: copies; sheds ref and top-level const (your copy, yours to mutate).
- `auto& x = src` → `const std::string&` — binds as-is; **const STAYS** or the binding would be illegal. ("drops const" is ONLY about the by-value form.)
- `const auto& x = src` → same, and also binds temporaries (lifetime-extension).
- `auto&& x = src` → `const std::string&` — forwarding: lvalue collapses to lvalue-ref; rvalue → rvalue-ref.
- String literals: `auto s = "hi"` → `const char*` never std::string; `"s"s` / `"sv"sv` from std::literals fix it.
- Braces: `auto x = {1,2}` → initializer_list; `auto x{5}` → int; `auto x{1,2}` → CE.
- `operator void()` never used by casts: `(void)x`, `static_cast<void>(x)` just discard; only `x.operator void()` calls it.

## Compile errors vs UB
- CE: narrowing list-init; designated out-of-order/mixed/nested/duplicate/static-member; `auto x{1,2}`; `auto x;`; plain `auto&` to a temporary.
- UB: reading default-initialized automatic scalar; `const auto&`/`auto&&` into a member of a dead temporary through a function return (the compiling version dangles — plain `auto&` would have been CE).
- Vexing parse: not an error — compiles as a declaration; the CE arrives later at `w.foo()`.

## Questions (getcracked)
- [x] Schrödinger's Initializer — 29/08 — ok
- [x] The designated representative. — 29/08 — ok
- [x] Forgot one? — 29/08 — ok

## Quiz log (Claude)
- 30/08 MISS + 31/08 REPEAT MISS: `auto& b = f()` where f returns `const T&` — said `T&` both times. auto& keeps const; deduction never produces an illegal binding. **Twice-missed: drill this.**
- 31/08: bit_cast sizes + `auto&`/`const auto&` temporary pair (Q11) — all ok.

## Syntax anchors
```cpp
int a = 5;   // copy-init
int b(5);    // direct-init
int c{5};    // direct-list-init (preferred)
int d{};     // value-init -> 0
int w1{4.5}; // CE: narrowing

struct Point { double x{0.0}; double y{0.0}; };
const Point p { .x = 10.0, .y = 20.0 };      // designated (C++20)
const Point o { .x{100.0}, .y{-100.0} };     // brace form ok
const Point t { .x = 50.0, .y{-40.0} };      // = and {} mix ok

struct Date { int year; int month; int day; static int mode; };
Date d1{ .mode = 10 };              // CE: static member
Date d2{ .day = 1, .year = 2010 };  // CE: out of order
Date d3{ 2050, .month = 12 };       // CE: positional + designated
Date d4{ .mh.min = 55 };            // CE: nested (C-only)

std::string foo();        // vexing parse: function decl
Double d(MyInt(i));       // vexing parse again
Double ok((MyInt(i)));    // fix; or Double ok{MyInt(i)};

struct X { operator void() { std::cout << "G"; } };
X x; (void)x; static_cast<void>(x);  // nothing printed
x.operator void();                    // G

unsigned int c2 = int{5};  // ok; unsigned int{5} is CE (multi-word)

const int ci{5};
auto b2{ci};       // int (const dropped - VALUE form only)
auto s{"hello"};   // const char*
using namespace std::literals;
auto s1{"goo"s};   // std::string
auto s2{"moo"sv};  // std::string_view

auto  v1 = obj.getRef();  // int   (copy)
auto& v2 = obj.getRef();  // int&  (or const int& if source is const!)

// ---- storage-init (cppstories) ----
// the three init pathways for globals:
double z = 100.0;   // constant-init: baked into data segment at compile time
int x;              // zero-init: BSS, guaranteed 0 (local `int x;` would be garbage!)
Value v{ 42 };      // dynamic-init: ctor runs at startup, before main

// static init order fiasco, minimal repro:
// b.cpp
Point createPoint(double x, double y) { return Point{ x, y }; }
Point center = createPoint(100, 200);          // dynamic-init
// a.cpp
extern Point center;
Point offset = { center.x + 100, center.y + 200 };  // reads center — may still be ZEROED
// link order decides; offset = {100,200} or {200,400}. Fix: Meyers singleton / constant-init.

// constinit vs constexpr (C++20):
constinit std::pair<int, double> global { 42, 42.2 };  // compile-time init, MUTABLE
constexpr std::pair<int, double> constG { 42, 42.2 };  // compile-time init, const
global = { 10, 10.1 };   // ok
// constG = { 10, 10.1 };  // CE

// thread_local: one per thread, ctor/dtor per thread
struct Value {
    Value(int x) : v(x) { std::cout << "Value(" << v << ")\n"; }
    ~Value() noexcept   { std::cout << "~Value(" << v << ")\n"; }
    int v{ 0 };
};
thread_local Value tls{ 42 };
void foo() { tls.v = 100; }        // touches THIS thread's copy
// { std::jthread w1{foo}, w2{foo}; }  → two Value(42)/~Value(42) pairs + main's

// static local: lazy init (first call), persists across calls
int counter_up() { static int counter = 0; return ++counter; }
// 4 calls → returns 4
```

## Traps / interview one-liners
- "Prefer {}: no narrowing, no vexing parse, {} alone = zero not garbage."
- "`vector<int> v(10,1)` = ten 1s; `v{10,1}` = two elements — initializer_list ctor wins with braces."
- "auto = copy without const; auto& = reference WITH const. The type you wrote is never the full story."
- "Uninitialized local read is UB, not 'random value'."
- "Designated init reads like named args and survives field additions."
