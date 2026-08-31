# Object Sizes

## Core model
- Standard minimums: object >= 1 byte (distinct addresses); byte >= 8 bits; char/short/int/long/long long >= 8/16/16/32/64 bits. Typical x86-64 Linux (LP64): int 4, long 8, long long 8, float 4, double 8, long double 16, pointers 8, bool/char 1.
- Class object size = non-static members (statics live outside the object) + padding + base subobject(s) + vptr(s) if polymorphic + vbase pointer(s) if virtual inheritance.
- Layout rule: each member at the next offset that is a multiple of its alignof; total size rounded to a multiple of the largest member alignment (so arrays index correctly). Member order therefore changes size: order by decreasing alignment to minimize padding.
- vptr: 8 bytes on x86-64, one per hierarchy however many virtual functions; a derived class with its own virtuals adds nothing. Two polymorphic bases (MI) = two vptrs. Virtual inheritance adds a vbase pointer per virtual base path, shared in the final object.
- Empty class: sizeof = 1. Empty base contributes 0 (EBO); C++20 `[[no_unique_address]]` extends that to members.
- Beware 32-bit-era articles: they say vptr/long = 4 bytes.

## Questions (getcracked)
- (tbd)
- Claude quiz 30/08: sizeof {char,double,char} — MISSED: forgot tail padding (17 vs 24); struct rounds to multiple of max alignment

## Compile errors vs unspecified
Compile error:
- `sizeof` on an incomplete type: `struct S; sizeof(S);` (this is why forward declarations can't be members by value).

Unspecified / trap (not UB by itself):
- Padding byte contents are unspecified — memcmp on structs compares garbage: two equal-valued structs can memcmp unequal.
- Layout between access-specifier groups was implementation-defined pre-C++23; don't hardcode offsets — use offsetof (itself conditionally-supported on non-standard-layout types).

## Traps / interview one-liners
- "sizeof includes padding; the struct is rounded to its alignment so it can be arrayed."
- "Reorder members by decreasing alignment to kill holes; `pahole` shows them."
- "In HFT terms: padding decides how many structs fit a 64B cache line, and where false sharing lands."
- "static members and member functions add zero to sizeof; virtual functions add one vptr total."
