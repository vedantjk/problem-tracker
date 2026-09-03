# Pointers & References

(learncpp 12.3-12.15, 20.1 — read 02/09)

## Core model
- A pointer is an OBJECT holding an address; a reference is a NAME for an object (not an object itself — though a reference *member* costs pointer storage, → memory_layout). Consequences: pointers reseat/null/uninitialized-exist, references must bind at birth and never reseat.
- `&` is three operators by context: type suffix = lvalue reference, unary = address-of, binary = bitwise AND. `*` likewise: type suffix = pointer, unary = dereference, binary = multiply.
- `*(&x)` round-trips; dereference yields an **lvalue** (assignable through it).
- Pointer size = address width (8B on x86-64), independent of pointee type. Multiple declarations need per-name stars: `int* p1, p2;` — p2 is an `int` (the reason "east const" people write `int *p`).
- **Invariant to maintain**: a pointer holds the address of a valid object OR nullptr. Value-init (`int* p{};`) gives null; uninitialized = wild (garbage address).
- Pointer → bool: null → false, everything else → true (`if (ptr)`).
- **Dangling pointer nuance**: *dereferencing* a dangling pointer is UB, but merely *using its value* (copying it, `p == q`) after the pointee dies is **implementation-defined**, not UB — the standard only guarantees assigning a new value (e.g. `p = nullptr;`) is safe. So even `if (dangling)` is off the well-defined map.
- Destruction does NOT null your pointers — dangling detection is entirely on you; there's no way to distinguish a valid pointer from a dangling one at runtime.

## Lvalue references (12.3-12.6)
- Must initialize; no reseating — `ref = y` writes y's VALUE into the referent, it never rebinds. Reseating needs `std::reference_wrapper`.
- Non-const `T&` binds only to *modifiable lvalues* of matching type: no const objects, no rvalues, and no different-type lvalues either (conversion yields an rvalue → rejected).
- `int& r2{ r1 }` is NOT a reference-to-reference — r1 evaluates to its referent, r2 just aliases the same object. `int&&` was free syntax, repurposed for rvalue refs in C++11.
- Reference and referent have independent lifetimes; referent dying first = dangling (access UB). References aren't objects — often compiled away entirely.
- **`const T&` binds to everything**: modifiable lvalues (read-only view), const lvalues, and rvalues (with lifetime extension).
- **Conversion-on-binding trap**: binding `const int& r` to a `short s` (or `5.0`) creates a TEMPORARY int from the converted value and binds to *that*. Later writes to `s` are invisible through `r` — you're watching a snapshot, not the object. Same-type binding aliases; cross-type binding copies.
- **Lifetime extension**: a temporary DIRECTLY bound to a const local reference lives as long as the reference. Only direct binding — not through a function return (→ max/min dangling trap below), and it doesn't chain.
- **constexpr references** can only bind to static-storage objects (globals/static locals) — an automatic variable's address isn't a compile-time constant.

## Pass by reference (12.5-12.6) & in/out params (12.13)
- `T&` param: no copy, callee writes visible; accepts modifiable lvalues ONLY (`f(5)` CE, `f(constVar)` CE) — which is why non-const ref params are rare.
- `const T&` param: no copy + accepts everything incl. literals. Default for class types.
- **Cheap-to-copy rule**: pass by value when `sizeof(T) <= 2 * sizeof(void*)` (≤16B on x86-64) AND no setup cost (no allocation/ctor work). Fundamentals + small trivial structs by value; class types by const&; unsure → const&.
- Strings: **prefer `std::string_view` by value** (C++17+) — handles string/string_view/C-string args cheaply; `const std::string&` is only cheap for std::string args (a C-string literal argument constructs a whole temporary std::string). Caveat: string_view not guaranteed null-terminated.
- **Out params** (non-const ref/pointer, "Out" suffix, rightmost): discouraged — caller must pre-declare, call site hides which args get written, no temporaries. Prefer return values (RVO makes them free); non-const ref only for in-out params or perf-critical giant objects. Pass-by-address at least makes mutation visible at the call site (`&i`) at the cost of null handling.

## const × pointer matrix
Read right-to-left; const-left-of-* = pointee, const-right-of-* = pointer:

| Declaration | reseat? | write through? |
|---|---|---|
| `int* p` | yes | yes |
| `const int* p` (ptr-to-const) | yes | no |
| `int* const p` (const ptr) | no — must init | yes |
| `const int* const p` | no | no |

- `const int x; int* p{&x};` = CE (would launder away const). The reverse is fine: `const int*` may point at a non-const object (view-only through that pointer).

## Function pointers (learncpp 20.1)
- Syntax: `int (*fcnPtr)(int);` — parens mandatory (`int* fcnPtr(int)` declares a function returning int*). Const version: `int (*const fcnPtr)(int)`.
- **Function-to-pointer decay**: a function name without parens implicitly converts to a pointer — `&foo` and `foo` both work as initializers (mirror of array decay). Exception: an *overloaded* name needs the target type to disambiguate (init a typed pointer, or `static_cast<void(*)(int)>(foo)`).
- Calling: `(*fcnPtr)(5)` explicit or `fcnPtr(5)` implicit — identical. Null fp call = UB, check first.
- **Default arguments do NOT apply through a function pointer.** Defaults are call-site sugar resolved at compile time against the *declaration*; through a pointer the call resolves at runtime, so `fcnPtr()` on `void f(int x = 0)` is a CE (signature is `void(*)(int)`). Flip side: you can *use* this to pick an overload that defaults would otherwise make ambiguous.
- Function pointers do NOT implicitly convert to `void*` (object-pointer world and function-pointer world are formally separate; POSIX `dlsym` forces the cast anyway — conditionally-supported).
- **`std::cout << foo` prints `1`** (gc, 02/09): the name decays to a function pointer; there's no `operator<<` for function pointers, and *because* function pointers don't convert to `void*` (the overload that prints data-pointer addresses), the only viable conversion is → bool. Non-null → `1` (`true` under boolalpha). clang warns `-Wpointer-bool-conversion` ("will always evaluate to true"). Printing the actual address needs `reinterpret_cast<void*>(&foo)` (conditionally-supported).
- Ergonomics ladder: raw fp → `using ValidateFn = bool(*)(int,int);` → `std::function<bool(int,int)>` (type-erased, costs — → functions_scope_lambdas) → `auto fp{&foo};`.
- Callback anchor: `void selectionSort(int* arr, int size, bool (*cmp)(int,int));`.

## Pass by address (12.10-12.11)
- Ladder: pass-by-value copies the object; pass-by-reference binds; pass-by-address copies an 8-byte pointer. "Pass by reference when you can, pass by address when you must."
- Address-taking needs an lvalue: `f(&5)` CE. const-ref beats const-ptr partly *because* it also takes rvalues/temporaries.
- Param const style: `const int* ptr` yes; `int* const ptr` in a signature = noise (top-level const on params isn't part of the signature anyway, → initialization_deduction).
- Null-handling pattern: `assert(ptr);` (document + debug-trap) AND `if (!ptr) return;` (production) — assert is not a substitute for the check.
- Optional out/in-param via `const int* id = nullptr` works but **overloading is better** (no null-deref risk, literals work); today: `std::optional` for optional *values* (→ error_handling), pointer only when you need to *mutate* an optional target.
- **Reseating the caller's pointer needs `int*& refptr`** (reference to pointer). `int&*` is CE — "no pointers to references" (references aren't objects). Plain `int* ptr2` param: `ptr2 = nullptr;` changes only the copy.
- **What nullptr actually is**: a prvalue of type `std::nullptr_t` — NOT a pointer type itself. It's a "null pointer constant" that implicitly converts to any pointer type (and pointer-to-member type). That's why it's overload-safe where 0/NULL aren't.
- **0 / NULL / nullptr in overload resolution**: `print(0)` → `print(int)`; `print(NULL)` → impl-defined mess (may be int, may be ambiguous); `print(nullptr)` → `print(int*)` reliably. nullptr's type is `std::nullptr_t` — you can overload on it: `void print(std::nullptr_t)`. But a *pointer variable holding nullptr* still calls `print(int*)` — **overloading matches on types, not values**.
- Unifying view: references compile to pointers, pass-by-address copies an address — mechanically "C++ passes everything by value"; the semantics differ at the language level.

## const references & aliasing (gc "In one out the other", 02/09)
- `void bar(int& a, const int& b)` called as `bar(c, c)`: both alias `c`. `a = 1` writes c; printing `b` shows **1**. A const reference is a **read-only view, not a promise of immutability** — the object can still change through another name. (Same root as the SROA/aliasing note in memory_layout: the compiler can't cache a load through `const T&` across writes it can't prove independent.)
- Flip side: if `c` were `const int`, the call is a CE — `int&` can't bind to a const object (no mutable view of a constant).
- **std::max/std::min tie-breaking**: both return the FIRST argument when equal (`max(a,b)` = `b < a ? a : b` — equal → a... spelled as "if equivalent, returns a" on cppreference). So `const int& mx = std::max(x, x); x = 11;` → mx reads 11 (it aliases x).
- Adjacent trap (not in gc's Q): `const int& r = std::max(a, b + 1);` — the `b + 1` temporary materializes for the call, max returns a `const&` *into an argument*, and lifetime extension does NOT apply through a function return → dangling after the full expression.

## Return by reference / address (12.12)
- Rule: the returned object must outlive the function. Ref to a plain local = dangling (compilers catch only trivial cases).
- **Lifetime extension does not cross a function return** (the general rule behind the max trap above): direct binding extends, bounced-through-a-return binding doesn't.
- Safe returns: (a) a reference PARAMETER (`return (a < b) ? a : b;` — both live in the caller); (b) a static local — but non-const static + returned ref = shared mutable state across every caller (`getNextId()` aliasing surprise), avoid; (c) a member of an object outliving the call (the real-world case: `obj.getName()`).
- Rvalue-argument nuance: an rvalue bound to a `const&` param lives to the end of the FULL EXPRESSION containing the call — `std::cout << foo("temp")` fine; saving the returned ref past the statement dangles.
- Assigning a returned reference to a value variable COPIES (`const int id{ getNextId() };` — independent). Dangling only bites when you *keep it as a reference*.
- Non-const ref return makes the call an lvalue: `max(a, b) = 7;` assigns through — the mechanism behind `v[i] = x` (operator[] returns T&).
- Return by address: same lifetime rules + nullptr as "no object"; caller must null-check. Prefer reference unless no-object is real (today: std::optional/expected for values, → error_handling).

## Pointer arithmetic & array decay (gc, 02/09)
- `int x[5]` at address 0, `sizeof(int)==4`:
  - `&x + 1` → **20**. `&x` has type `int(*)[5]` — pointer to the WHOLE array; +1 steps one whole array (`sizeof(int[5])` = 20).
  - `x + 1` → **4**. `x` decays to `int*`; +1 steps one **pointee** (`sizeof(int)` = 4).
- Rule: `p + n` advances `n * sizeof(*p)` — size of the *pointed-to type*, never "size of the pointer" (gc's explanation misspoke here: pointer size is 8 on x86-64 and irrelevant to the stride).
- Same fact underlies `sizeof(x)` = 20 vs `sizeof(x+0)` = 8, and the `(&x)[1]` end-of-array idiom.

## argv is null-terminated (gc, 02/09)
- The standard guarantees **`argv[argc] == 0`** — not UB, explicitly specified ([basic.start.main]). argv acts like a null-terminated array, same shape as a C-string: walk `for (char** p = argv; *p; ++p)` with no count.
- Why it exists: lets argv pass directly to APIs expecting null-terminated arrays (`execv(path, argv)`); portability history (some old compilers didn't set it — one more reason it's now nailed down in the standard).
- Practice: use argc; keep the terminator fact in the back pocket.

## Compile errors vs UB vs impl-defined
- CE: `int* p{5}` (literal address); `int* p{&constInt}`; `int&*` (pointer to reference); `f(&5)`; calling through fp with missing "default" arg; overloaded-name decay without target type.
- UB: dereferencing wild/null/dangling; calling a null function pointer.
- Impl-defined: using (not dereferencing) a dangling pointer's value; what NULL expands to.

## Questions (getcracked) / Quiz log
- [x] &x + 1 vs x + 1 (array at 0, sizeof(int)=4) — 02/09 — ok (20, 4). Note gc's own explanation said "size of the pointer" for op two; correct reasoning is size of the POINTEE.
- [x] In one out the other (int& + const int& aliasing same var) — 02/09 — ok (prints 1).

## Syntax anchors
```cpp
int x{5};
int* ptr{ &x };     // & = address-of
*ptr = 6;           // * = dereference, yields lvalue → x == 6
int* p1, * p2;      // star per name; `int* p1, p2` makes p2 an int

int* pn{};          // value-init → nullptr
if (pn) { }         // null check via bool conversion

const int* a{};        // ptr-to-const: *a = 1 CE, a = &y ok
int* const b{ &x };    // const ptr: b = &y CE, *b = 1 ok; must init
const int* const c{ &x };

int foo(int);
int (*fp)(int){ foo };    // decay; &foo also fine
(*fp)(5);  fp(5);         // same call
using CmpFn = bool(*)(int,int);
void selectionSort(int* arr, int size, CmpFn cmp);
auto fp2{ &foo };

void f(int x = 0);
int (*fpd)(int){ f };  // fpd() CE — defaults don't travel through pointers

void nullify(int*& refptr) { refptr = nullptr; }  // reseats caller's ptr
// int&* — CE: no pointer to reference

void print(int) ; void print(int*);
print(0);        // int
print(NULL);     // impl-defined / possibly ambiguous
print(nullptr);  // int*
void print(std::nullptr_t);  // catches literal nullptr only —
int* pv{nullptr}; print(pv); // still int* (types, not values)

void safe(const int* ptr) { assert(ptr); if (!ptr) return; /* use *ptr */ }

int x[5]{0,1,2,3,4};       // at addr 0, sizeof(int)==4:
// &x + 1  → 20   (int(*)[5]: strides sizeof(int[5]))
// x  + 1  → 4    (decayed int*: strides sizeof(int))
// sizeof(x) == 20, sizeof(x + 0) == 8

void hello();
std::cout << hello;        // 1 — fp→bool (no void* conversion for fps)
std::cout << reinterpret_cast<void*>(&hello);  // the address (cond.-supported)

for (char** p = argv; *p; ++p)   // argv[argc] == 0, guaranteed
    std::cout << *p << '\n';

// references
int v1{5}, v2{6};
int& r{ v1 };
r = v2;              // v1 = 6; NO rebind — references never reseat
// int& bad;         // CE: must initialize
// int& bad2{ 5 };   // CE: non-const ref can't bind rvalue

short s{ 3 };
const int& cr{ s };  // conversion → binds a TEMPORARY int(3)
s = 42;              // cr still 3 — watching a snapshot, not s

const int& ext{ 5 };            // lifetime-extended: fine for ext's whole life
const int& bounce(const int& x) { return x; }
const int& dang{ bounce(5) };   // DANGLING: extension doesn't cross a return

int& maxRef(int& a, int& b) { return (a > b) ? a : b; }
maxRef(v1, v2) = 7;             // call is an lvalue: writes the bigger one

void getSinCos(double deg, double& sinOut, double& cosOut);  // out-param style: avoid
```

## Traps / interview one-liners
- "A pointer should hold a valid address or nullptr — the whole discipline in one sentence."
- "Dereferencing a dangling pointer is UB; even reading its value is only implementation-defined."
- "const left of star protects the pointee, right of star freezes the pointer."
- "Default args don't travel through function pointers — they're compile-time call-site sugar."
- "0 is an int, NULL is a mystery, nullptr is a pointer. Overload on nullptr_t if you must catch it."
- "Reseat a caller's pointer with int*&; int&* doesn't exist because references aren't objects."
- "Mechanically everything is pass-by-value — sometimes the value is an address."
- "&x + 1 jumps the array, x + 1 jumps an element — pointer arithmetic strides by pointee size."
- "cout << functionName prints 1: no void* conversion for function pointers, so bool wins."
- "argv[argc] is guaranteed null — argv is a null-terminated array by the standard."
- "A const reference is a read-only window, not a frozen object — another alias can still write."
- "std::max/min return the first argument on ties — and returning const& means feeding them a temporary can dangle."
- "Assigning to a reference writes the referent; references never reseat."
- "Cross-type const-ref binding copies into a temporary — you alias the snapshot, not the variable."
- "Lifetime extension is direct-binding only: it never survives a function return and never chains."
- "Cheap to copy = fits in two pointers and no ctor work; otherwise const&. Strings: string_view by value."
- "Out-params hide writes at the call site; return values are free (RVO). Reach for T& params last."
