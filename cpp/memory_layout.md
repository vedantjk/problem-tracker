# Object Sizes, Alignment & Layout

## Core model
- Standard minimums: object >= 1 byte (distinct addresses); byte >= 8 bits; char/short/int/long/long long >= 8/16/16/32/64 bits. x86-64 Linux (LP64): int 4, long 8, long long 8, float 4, double 8, long double 16, pointers 8, bool/char 1. wchar_t 4, char16_t 2, char32_t 4.
- Class size = non-static members (statics live outside) + padding + base subobjects + vptr(s) + vbase pointer(s). Member functions add nothing.
- Layout: each member at next offset that's a multiple of its alignof; TOTAL rounded up to largest member alignment (arrays must index). Compute OFFSETS, sizeof falls out. Reorder by decreasing alignment to kill holes (`pahole` shows them).
- vptr: 8B on x86-64, one per hierarchy regardless of virtual-function count; derived's own virtuals add nothing; two polymorphic bases (MI) = two vptrs. Virtual inheritance: +1 vbase pointer per virtual path, base shared once in the most-derived object.
- Empty class sizeof = 1; empty BASE contributes 0 (EBO); C++20 `[[no_unique_address]]` for members.
- References: `sizeof(int&)` reports sizeof(int) (language: references aren't objects), but a reference MEMBER costs pointer storage: `sizeof(struct{int&})` == 8. Same for lambda by-ref captures.
- Beware 32-bit-era articles (vptr/long = 4).

## Memory segments: stack vs heap (learncpp 20.2 + OSTEP 14.1, read 01/09)
- Five segments of a running program: **code/text** (compiled instructions, read-only) · **data** (initialized globals/statics) · **BSS** (zero-initialized globals/statics — costs no space in the binary, just a size) · **heap** · **call stack**.
- data-vs-BSS is sorted by VALUE, not by presence of an initializer (verified 01/09, objdump): `int a;` → .bss, `int b = 0;` → **.bss too** (explicit zero!), `int c = 5;` → .data, `int d[1000];` → 4000B of .bss but ~0B in the binary.
- **Stack = automatic memory** (OSTEP's framing): allocation/deallocation managed *implicitly by the compiler*. `int x;` in a function → compiler makes room on call, frees on return. Corollary: anything that must outlive the call must NOT live there.
- **Heap = explicit memory**: you (`new`/`malloc`) allocate, you free. OSTEP's one-liner example packs both in a line: `int *x = (int*)malloc(sizeof(int));` — the *pointer* x is a stack allocation the compiler handles; the *pointee* is a heap allocation you handle.
- Stack frame contents: return address, args, locals, saved registers. **Stack pointer (SP)** register tracks the top; "popping" a frame = moving SP — no memory is cleaned, the bytes just get overwritten by the next push (why reading popped-frame garbage sometimes "works").
- Why stack is fast: allocation = one SP bump, sizes known at compile time, direct addressing, hot in cache. Why heap is slow(er): allocator search/bookkeeping, successive `new`s not necessarily contiguous, access via pointer indirection.
- Stack sizes: ~8MB g++/clang Linux, 1MB MSVC. Overflow triggers: big locals (`int arr[10'000'000]` ≈ 40MB) or deep recursion (learncpp measured crash at ~4,848 calls debug / ~128,679 release — frame size shrinks with -O). Result: OS kills you (segfault/access violation), not a C++ exception.
- Growth direction (up vs down in addresses) is architecture-specific — don't assume frames at lower addresses.
- Choose: stack for small, scope-bound; heap for large or outliving-the-scope. Heap costs: leak risk, slower alloc, indirection.
- OSTEP 14.2 side notes worth keeping: `malloc(size_t)` returns `void*` (NULL on failure); `sizeof` is a compile-time **operator**, not a function — `sizeof(x)` on `int* x = malloc(10*sizeof(int))` gives 8 (pointer!), not 40, but `int x[10]; sizeof(x)` = 40 (static array size known). String alloc idiom: `malloc(strlen(s) + 1)` for the NUL.

### OSTEP 14.2-14.4: malloc/free + the error catalog (read 01/09)
- **14.2 malloc**: in C, casting the result (`(int*)malloc(...)`) is pure reassurance, not needed for correctness (C++ differs: `void*` doesn't implicitly convert, cast required). Passing a variable to sizeof is legal but trap-prone (the pointer-vs-array thing above).
- **14.3 free**: takes only the pointer — **the allocator tracks the size itself** (in its own metadata, usually a header just below the returned pointer). That's why free needs exactly the pointer malloc returned.
- **14.4 the seven memory errors** (each maps into ub_catalog):
  1. Forgetting to allocate: `char* dst; strcpy(dst, src)` → segfault ("YOU DID SOMETHING WRONG WITH MEMORY YOU FOOLISH PROGRAMMER AND I AM ANGRY"). Fix: malloc or `strdup`.
  2. Not allocating enough (**buffer overflow**): `malloc(strlen(src))` missing the +1 for NUL — often *appears* to work (allocators over-allocate/round up), classic security-vuln source.
  3. Uninitialized read: malloc'd memory holds unknown bytes (calloc zeroes).
  4. Forgetting to free (**leak**): matters for long-running processes; GC languages don't save you — a live reference pins the chunk forever.
  5. Freeing too early (**dangling pointer**): a later malloc recycles the chunk while you still use it.
  6. **Double free**: undefined; allocator metadata corrupts, crashes common.
  7. **Invalid free**: anything that isn't exactly a malloc-returned pointer (middle of a block, stack address).
- The "it compiled / it ran ≠ it's correct" tip + tooling: valgrind (purify historically). Overflows that scribble past the end can be silently harmless for years.
- **Why exiting leaks nothing**: two levels of memory management — the malloc library manages the heap *within* the process's address space; the OS hands out pages and **reclaims all of them at process death** regardless of free. So short-lived-program leaks are "fine" (bad habit); leaks kill long-running servers... and the OS itself has nobody to clean up after it.
- **14.5 preview**: malloc/free are *library* calls layered on system calls — `brk`/`sbrk` (move the heap's end, never call directly) and `mmap` (anonymous regions). `calloc` = malloc + zero; `realloc` = grow by new-region + copy.

### Why `x->foo()` can be slower than `y.foo()` (gc question, 01/09)
Excluding the `new` itself, three layers (in increasing importance):
1. **Naive indirection**: `x->foo()` = `(*x).foo()` — load the pointer, then access the object: two memory touches vs one. BUT with optimization x sits in a register, so at the callsite the generated code is often *identical* to the stack case. This reason mostly exists at -O0. (gc's own caveat.)
2. **Locality — the one gc calls the real answer**: the top of the stack is essentially always hot in L1 (every call/return touches it); a heap object can be anywhere — cold miss ≈ 100-300 cycles, worse prefetch, allocator scatter. Dominates in memory-bound code.
3. **The optimizer reason gc doesn't mention**: a stack object whose address never escapes can be **SROA'd / promoted into registers** — the object stops existing in memory at all, fields fold into constants. A heap object behind a pointer usually can't: the compiler must prove nothing aliases `*x` before caching loads across writes, and pointer escape kills that. Same family as "the call is an optimization barrier" (→ functions_scope_lambdas). C++14+ *may* elide `new` entirely in simple cases, but it's permission, not a guarantee (nothing like JVM escape analysis you can rely on).
- If `foo()` is virtual, that's a separate, additional indirection (vptr load + fn-pointer load + no inlining) — orthogonal to stack vs heap.
- One-liner for interviews: "same assembly at the callsite once optimized; the differences that survive are cache locality and what the optimizer is *allowed* to assume about aliasing."

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
