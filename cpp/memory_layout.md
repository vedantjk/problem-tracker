# Object Sizes, Alignment & Layout

## Core model
- Standard minimums: object >= 1 byte (distinct addresses); byte >= 8 bits; char/short/int/long/long long >= 8/16/16/32/64 bits. x86-64 Linux (LP64): int 4, long 8, long long 8, float 4, double 8, long double 16, pointers 8, bool/char 1. wchar_t 4, char16_t 2, char32_t 4.
- Class size = non-static members (statics live outside) + padding + base subobjects + vptr(s) + vbase pointer(s). Member functions add nothing.
- Layout: each member at next offset that's a multiple of its alignof; TOTAL rounded up to largest member alignment (arrays must index). Compute OFFSETS, sizeof falls out. Reorder by decreasing alignment to kill holes (`pahole` shows them).
- vptr: 8B on x86-64, one per hierarchy regardless of virtual-function count; derived's own virtuals add nothing; two polymorphic bases (MI) = two vptrs. Virtual inheritance: +1 vbase pointer per virtual path, base shared once in the most-derived object.
- Empty class sizeof = 1; empty BASE contributes 0 (EBO); C++20 `[[no_unique_address]]` for members.
- References: `sizeof(int&)` reports sizeof(int) (language: references aren't objects), but a reference MEMBER costs pointer storage: `sizeof(struct{int&})` == 8. Same for lambda by-ref captures.
- Beware 32-bit-era articles (vptr/long = 4).

## Compile errors vs unspecified
- CE: `sizeof` on incomplete type (`struct S; sizeof(S);`) — why forward-declared types can't be by-value members.
- Unspecified: padding byte contents (memcmp on structs compares garbage); pre-C++23 layout between access-specifier groups; use offsetof.

## Quiz log (Claude)
- 30/08 MISSED: {char,double,char} — computed 17, forgot TAIL padding → 24. Rule: total rounds to max alignment.
- 30/08: {short,char,int*,float} — offsets right, forgot tail pad again mid-answer (20 → 24); reorder to 16 — ok. Tail-pad reflex landed by rep 3.
- 31/08: {char,int,char,long} = 24 — total right, internal map wrong (pad-7 before long, zero tail). Compute offsets, not a padding shopping list.

## Syntax anchors
```cpp
class A { float m1; const int m2; static int m3; char m4; };
// sizeof(A) = float+int+char+padding; statics not in the object

class C1 { char c; int i1, i2, i3; long l; short s; };   // holes after c and i3
class C2 { int i1, i2, i3; long l; short s; char c; };   // repacked
// (32-bit article numbers; recompute LP64: long=8, vptr=8)

class Base    { virtual void f(); int a; };                // vptr(8)+int(4)+pad(4) = 16
class Derived : public Base { virtual void g(); int b; };  // 16: b fills pad, no 2nd vptr

class ABase { int m; };
class BBase : public virtual ABase { int m; };  // + vbase ptr
class CBase : public virtual ABase { int m; };  // + vbase ptr
class ABCD  : public BBase, public CBase { int m; };  // ONE shared ABase

struct S { char a; double b; char c; };  // 0,pad7,8,16,pad7 -> 24
struct R { double b; char a; char c; };  // 16
```

## Traps / interview one-liners
- "sizeof includes padding; the struct rounds to its alignment so arrays work."
- "Padding decides how many structs fit a 64B cache line and where false sharing lands."
- "Equal structs can memcmp unequal — padding is garbage."
- "References have no sizeof of their own but cost pointer storage as members/captures."
