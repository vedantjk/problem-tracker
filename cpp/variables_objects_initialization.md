# Variables, Objects, Initialization

## Core model
- Object = region of storage that holds a value. Variable = named object. Identifier = the name. Type = what kind of value the object holds and how big it is.
- Initialization gives the value at creation; assignment gives it later. Different mechanics (ctor vs `operator=`), not just timing.
- Forms: `int a = 5;` (copy-init), `int a(5);` (direct), `int a{5};` (direct-list, **prefer**), `int a{};` (value-init → zero), `int a;` (default-init).
- Default-init: automatic/heap storage → indeterminate, reading is UB. Static/namespace scope → zero-initialized first. Class types run the default ctor.
- List-init forbids narrowing. Checked on the *value* when it's a constant expression: `int x{4L}` ok, `unsigned u{-1}` error, `int y{4.5}` error, `int z{dbl_var}` error regardless of contents.
- Most vexing parse: anything parseable as a function declaration is one. `std::string s();` declares a function. `Double d(MyInt(i));` declares a function taking a function. Fix: `{}` or extra parens `Double d((MyInt(i)));`.
- Aggregate = array, or class with: no private/protected non-static data members, no user-declared ctors (C++20 tightened from "user-provided"), no virtual/private/protected bases, no virtual functions. Default member initializers are allowed (since C++14).
- C++20 designated initializers `T o{.a = 1, .b{2}}`: aggregates only, non-static members only, declaration order, may skip members (skipped → default member init, else value-init), no mixing with positional, no duplicates, no nesting (`.mh.min` is C, not C++).

## Questions
- [x] Schrödinger's Initializer — 29/08 — ok
- [x] The designated representative. — 29/08 — ok
- [x] Forgot one? — 29/08 — ok

## Compile errors vs UB
Compile errors:
- Narrowing in list-init: `int x{4.5};` `unsigned u{-1};` `char c{300};` — all CE (with `=` they'd be legal conversions).
- Designated init: `Date d{.day=1, .year=2020};` (out of order), `Date d{2050, .month=12};` (mixed), `Date d{.mh.min=5};` (nested), `Date d{.mode=1};` (static member) — all CE.
- Most vexing parse isn't an error — worse, it compiles as a function declaration: `Widget w();` then `w.foo()` is the CE.

UB:
- `int x; std::cout << x;` — reading a default-initialized automatic scalar. (Static-storage `int x;` is 0 — fine.)

## Traps / interview one-liners
- "Prefer `{}`: no narrowing, no vexing parse, and `{}` alone means value-init (zero) instead of garbage."
- "Uninitialized local read is UB, not 'random value': the compiler may assume it never happens."
- "`std::vector<int> v(10, 1)` vs `v{10, 1}`: parens = 10 ones, braces = two elements. `initializer_list` ctor wins when braces are used."
- "Designated initializers exist so `Config c{.timeout = 30}` reads like named args and stays correct when fields are added."
