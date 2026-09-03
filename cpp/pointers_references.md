# Pointers & References

(learncpp 12.7-12.8, 12.9-12.11, 20.1 — read 02/09)

## Core model
- A pointer is an OBJECT holding an address; a reference is a NAME for an object (not an object itself — though a reference *member* costs pointer storage, → memory_layout). Consequences: pointers reseat/null/uninitialized-exist, references must bind at birth and never reseat.
- `&` is three operators by context: type suffix = lvalue reference, unary = address-of, binary = bitwise AND. `*` likewise: type suffix = pointer, unary = dereference, binary = multiply.
- `*(&x)` round-trips; dereference yields an **lvalue** (assignable through it).
- Pointer size = address width (8B on x86-64), independent of pointee type. Multiple declarations need per-name stars: `int* p1, p2;` — p2 is an `int` (the reason "east const" people write `int *p`).
- **Invariant to maintain**: a pointer holds the address of a valid object OR nullptr. Value-init (`int* p{};`) gives null; uninitialized = wild (garbage address).
- Pointer → bool: null → false, everything else → true (`if (ptr)`).
- **Dangling pointer nuance**: *dereferencing* a dangling pointer is UB, but merely *using its value* (copying it, `p == q`) after the pointee dies is **implementation-defined**, not UB — the standard only guarantees assigning a new value (e.g. `p = nullptr;`) is safe. So even `if (dangling)` is off the well-defined map.
- Destruction does NOT null your pointers — dangling detection is entirely on you; there's no way to distinguish a valid pointer from a dangling one at runtime.

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
- Ergonomics ladder: raw fp → `using ValidateFn = bool(*)(int,int);` → `std::function<bool(int,int)>` (type-erased, costs — → functions_scope_lambdas) → `auto fp{&foo};`.
- Callback anchor: `void selectionSort(int* arr, int size, bool (*cmp)(int,int));`.

## Pass by address (12.10-12.11)
- Ladder: pass-by-value copies the object; pass-by-reference binds; pass-by-address copies an 8-byte pointer. "Pass by reference when you can, pass by address when you must."
- Address-taking needs an lvalue: `f(&5)` CE. const-ref beats const-ptr partly *because* it also takes rvalues/temporaries.
- Param const style: `const int* ptr` yes; `int* const ptr` in a signature = noise (top-level const on params isn't part of the signature anyway, → initialization_deduction).
- Null-handling pattern: `assert(ptr);` (document + debug-trap) AND `if (!ptr) return;` (production) — assert is not a substitute for the check.
- Optional out/in-param via `const int* id = nullptr` works but **overloading is better** (no null-deref risk, literals work); today: `std::optional` for optional *values* (→ error_handling), pointer only when you need to *mutate* an optional target.
- **Reseating the caller's pointer needs `int*& refptr`** (reference to pointer). `int&*` is CE — "no pointers to references" (references aren't objects). Plain `int* ptr2` param: `ptr2 = nullptr;` changes only the copy.
- **0 / NULL / nullptr in overload resolution**: `print(0)` → `print(int)`; `print(NULL)` → impl-defined mess (may be int, may be ambiguous); `print(nullptr)` → `print(int*)` reliably. nullptr's type is `std::nullptr_t` — you can overload on it: `void print(std::nullptr_t)`. But a *pointer variable holding nullptr* still calls `print(int*)` — **overloading matches on types, not values**.
- Unifying view: references compile to pointers, pass-by-address copies an address — mechanically "C++ passes everything by value"; the semantics differ at the language level.

## Compile errors vs UB vs impl-defined
- CE: `int* p{5}` (literal address); `int* p{&constInt}`; `int&*` (pointer to reference); `f(&5)`; calling through fp with missing "default" arg; overloaded-name decay without target type.
- UB: dereferencing wild/null/dangling; calling a null function pointer.
- Impl-defined: using (not dereferencing) a dangling pointer's value; what NULL expands to.

## Questions (getcracked) / Quiz log
- (none yet)

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
```

## Traps / interview one-liners
- "A pointer should hold a valid address or nullptr — the whole discipline in one sentence."
- "Dereferencing a dangling pointer is UB; even reading its value is only implementation-defined."
- "const left of star protects the pointee, right of star freezes the pointer."
- "Default args don't travel through function pointers — they're compile-time call-site sugar."
- "0 is an int, NULL is a mystery, nullptr is a pointer. Overload on nullptr_t if you must catch it."
- "Reseat a caller's pointer with int*&; int&* doesn't exist because references aren't objects."
- "Mechanically everything is pass-by-value — sometimes the value is an address."
