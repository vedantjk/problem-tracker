# Object Sizes, Alignment & Layout

## Sizes and platform assumptions

`sizeof` measures an object's representation in C++ bytes, including padding. A byte has at least eight bits, and `sizeof(char)` is always one. The minimum widths of char, short, int, long, and long long are 8, 16, 16, 32, and 64 bits respectively. Complete objects have nonzero size, although empty base and potentially overlapping member subobjects have special rules.

On a typical x86-64 Linux target using LP64, int is four bytes, long and long long are eight, and ordinary object pointers are eight. LP64 names a data model in which long integers and pointers are 64 bits, while int remains 32 bits. Float is commonly four bytes, double eight, and long double sixteen bytes of storage. Bool and char commonly occupy one byte; wchar_t is commonly four, char16_t two, and char32_t four. These are target observations. For example, 64-bit Windows normally uses a four-byte long.

## Alignment and padding

Alignment constrains the addresses where an object of a type can begin. In a typical ordinary struct layout, each member starts at an offset satisfying its alignment. The compiler can insert padding between members and at the end. Tail padding ensures that successive array elements also satisfy the struct's alignment.

```cpp
struct S { char a; double b; char c; };
// Assuming alignof(double) == 8 and sizeof(double) == 8:
// a starts at 0, b at 8, and c at 16. A typical sizeof(S) is 24.
struct R { double b; char a; char c; };
// Under the same platform layout rules, this struct commonly occupies 16 bytes.
```

Calculate offsets in declaration order and then round the total to the object's required alignment. Do not just add member sizes and guess the padding. The application binary interface (ABI) is the platform's set of rules for binary layout and function calls. Explicit alignment, inheritance, and ABI rules can change the calculation.

`sizeof(S)` gives the total storage size, and `alignof(S)` gives the alignment required for an object of type `S`. The declaration keyword `alignas` requests alignment, for example `alignas(64) char buffer[64];`. It cannot weaken the type's existing alignment requirement.

For a standard-layout type such as the simple struct `S` above, `offsetof(S, b)` from `<cstddef>` gives member `b`'s byte offset from the start. Standard-layout is a language category with restrictions on members and inheritance that make certain layout operations well-defined; do not assume every class qualifies. Tools such as `pahole` can also inspect the layout produced by a particular build.

Reordering members can reduce holes and improve how many objects fit into a cache line. It can also change an ABI or serialized representation. Cache-line size is target-dependent; 64 bytes is common. False sharing depends on where independently written data lands, not just the total struct size.

Padding bytes are not meaningful fields. Two objects with equal member values need not have identical byte representations, so `memcmp` is not a general replacement for semantic equality. Do not treat padding as a stable serialized value.

## Classes, virtual dispatch, and empty objects

Non-static data members and base subobjects contribute to object representation. Static members have separate storage, and member function code is not stored inside each object. Virtual dispatch commonly introduces hidden pointers, but neither a vptr nor a particular number of such pointers is specified by C++.

On common ABIs, a derived class can share its primary base's virtual-table pointer, and multiple polymorphic bases can require multiple pointers. Adding more virtual functions does not normally add a pointer per function. Virtual inheritance shares the virtual base within the most-derived object, but the metadata arrangement depends on the ABI. Do not assume “one vbase pointer per virtual path.” The [Itanium C++ ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#vtable-components) describes one widely used scheme involving virtual-table offsets.

An empty complete class commonly has size one. Empty Base Optimization can remove the additional storage for an eligible empty base. C++20's `[[no_unique_address]]` allows similar overlap opportunities for members, but does not promise that every annotated member costs zero bytes.

`sizeof(int&)` yields the size of int because references are not objects with their own sizeof result. A reference member or reference capture often requires pointer-like storage, but its representation is implementation-dependent. Local references can also be optimized away.

## Process memory: code, data, BSS, stack, and heap

A useful operating-system model separates executable code, initialized static data, zero-initialized static data (BSS), stack storage, and dynamically allocated regions. Actual processes have other mappings too, and C++ does not require these sections.

BSS commonly records the size of zero-initialized storage without storing every zero in the executable. Both `int a;` and `int b = 0;` at namespace scope can reside there; `int c = 5;` commonly resides in initialized data. The value and toolchain placement matter, not merely whether an initializer was written.

Automatic locals commonly use stack storage or registers. A frame can contain saved registers, spilled arguments, a return address, and local storage, depending on the calling convention and optimization. Releasing a frame often only adjusts a stack pointer; it need not erase the old bytes. Their physical presence does not keep destroyed local objects alive.

Dynamic storage obtained with new or an allocator can outlive the allocating call. The pointer variable and its pointee have separate lifetimes: a local `std::unique_ptr<T>` can occupy automatic storage while owning a dynamically allocated T.

## Stack capacity and allocation cost

Stack capacity is set by the environment. Rough defaults such as eight megabytes for some Linux main threads and one megabyte for some Windows executables are context-dependent. Large local arrays and deep recursion can exhaust it; C++ does not promise a catchable exception for stack overflow. Stack growth direction is also platform-specific.

Stack allocation is often cheap because storage can be reserved by adjusting a register. Dynamic allocation may require allocator bookkeeping, synchronization, or obtaining more pages. Prefer scope-bound values when suitable, and use owning containers or smart pointers when dynamic storage is needed.

Access speed is a separate question from allocation speed. A heap object can be hot in cache, and a stack object can be cold. Contiguity, access pattern, working-set size, and aliasing matter more than the label “stack” or “heap.”

## malloc, free, calloc, and realloc

`malloc` allocates raw storage and returns a void pointer, or null on failure. C permits implicit conversion from void pointer to an object pointer; C++ generally requires a cast. In C++ code, an owning container or other RAII type usually expresses the intended lifetime more clearly. Pair allocation and deallocation families correctly: malloc with free, new with delete, and new[] with delete[].

The allocator retains enough information to free an allocation, so `free` does not take a size. Its metadata layout is allocator-specific. `free(nullptr)` is valid; an interior pointer, an automatic object's address, or a pointer already freed is not a valid allocated block to free.

`calloc` zeroes the allocated bytes; this is not the same as constructing arbitrary C++ objects. `realloc` may resize in place or move and copy the storage. On failure, it leaves the original allocation intact, so do not overwrite the only pointer to that allocation before checking the result. Do not use raw relocation for arbitrary non-trivially-copyable C++ objects.

On some Unix-like systems, allocators use facilities such as brk or mmap underneath. Allocation-library calls are not necessarily system calls on each invocation. When a process terminates, the OS normally reclaims its address space, but that does not replace destructors or other application cleanup.

`sizeof` is an operator. For ordinary C++ types, `sizeof(pointer)` describes the pointer, not the allocation size. A C string buffer needs space for its terminating null character, so its byte count includes `strlen(text) + 1`.

## Seven common memory mistakes

1. Using a destination before allocating valid storage can cause an invalid write.
2. Allocating too little storage causes a buffer overflow, including when the terminator byte was forgotten.
3. Reading uninitialized storage does not produce a dependable value.
4. Losing an owning pointer without releasing its allocation leaks memory. Retaining unused objects can also waste memory in garbage-collected programs.
5. Releasing storage too early leaves dangling pointers and risks use-after-free.
6. Freeing the same allocation twice violates the allocator contract.
7. Freeing an invalid pointer, such as an interior or stack pointer, also violates that contract.

An incorrect program may appear to work because an invalid access happens to hit mapped memory. Use warnings, sanitizers, and tools such as Valgrind to catch exercised mistakes, while still reasoning about ownership and bounds.

## Pointer indirection and optimization

`x->foo()` uses a pointer to reach an object; `y.foo()` names an object directly. After optimization, their call-site instructions may be identical. A pointer may already be in a register, and either object may be in cache.

A local object whose address does not escape can sometimes be replaced with registers or constants through scalar replacement of aggregates (SROA). A pointer whose aliases are unknown can make that proof harder. Compilers can also optimize some dynamic allocations, so the distinction is about what can be proved, not an absolute stack-versus-heap rule.

Virtual dispatch is a separate consideration. It commonly loads a function address indirectly, but devirtualization can sometimes turn it into a direct call and enable inlining. Measure the complete workload before attributing a slowdown to one source-level spelling.

## Errors and pitfalls

`sizeof` requires a complete object type where applicable, so a forward declaration alone cannot support a by-value data member or an ordinary sizeof calculation. Layout numbers, virtual inheritance metadata, padding reuse, and captured-reference storage should be labeled with their ABI assumptions. A measurement proves a layout for that build, not for all C++ implementations.

## Additional syntax examples

These are independent syntax sketches, including deliberately invalid examples marked `CE` (compile error). They are not one compilable program.

```cpp
class A { float m1; const int m2; static int m3; char m4; };
// sizeof(A) = float+int+char+padding; statics not in the object

class C1 { char c; int i1, i2, i3; long l; short s; };   // holes after c and i3
class C2 { int i1, i2, i3; long l; short s; char c; };   // repacked
// (32-bit article numbers; recompute LP64: long=8, vptr=8)

class Base    { virtual void f(); int a; };                // A common x86-64 ABI layout is 16 bytes.
class Derived : public Base { virtual void g(); int b; };  // Some ABIs reuse tail padding; inspect this target.

class ABase { int m; };
class BBase : public virtual ABase { int m; };  // Virtual-base metadata is ABI-specific.
class CBase : public virtual ABase { int m; };  // Virtual-base metadata is ABI-specific.
class ABCD  : public BBase, public CBase { int m; };  // ONE shared ABase

struct S { char a; double b; char c; };  // Typical 8-byte double alignment: offsets 0, 8, 16; total 24.
struct R { double b; char a; char c; };  // Typically 16 under those same assumptions.
```

## Interview Q&A

### Why can a struct be larger than the sum of its members?

Each member must satisfy its alignment, so the compiler may insert gaps. The struct can also need tail padding so every element of an array starts at a suitably aligned address. I calculate member offsets first and then account for the final alignment.

### Does adding a virtual function add eight bytes?

Not necessarily. A class becoming polymorphic may gain virtual-dispatch metadata under a particular ABI, but an already polymorphic class usually does not gain a pointer for each new virtual function. Inheritance and the ABI determine the layout, so I would state the target before giving a size.

### Are stack objects always faster than heap objects?

Stack allocation is often cheaper, but access speed depends on locality and the generated code. A heap object can be hot and contiguous with related data. I separate allocation cost from access cost and look at cache behavior and what the optimizer can prove.

### Why does free not need the allocation size?

The allocator keeps metadata that lets it identify and release the allocation. That is also why I must pass a valid allocation pointer, rather than an address somewhere in the middle. The metadata's exact location depends on the allocator.

### Can I compare structs with memcmp?

Not as a general equality test. Padding bytes can differ even when all the members compare equal, and member representations can have their own subtleties. I compare meaningful fields or use a suitable equality operator.

### Why can a pointer-based access limit optimization?

The compiler may need to consider whether another pointer aliases the same object. If it cannot prove independence, it may have to reload values after writes or calls. A non-escaping local can be easier to promote into registers, but this is a proof issue rather than a universal rule about allocation location.

## Practice history

The entries below preserve the original practice record. Use the explanations above for the current rules and qualifications.

### Quiz log (Claude)

- 30/08 MISSED: {char,double,char} — computed 17, forgot TAIL padding → 24. Rule: total rounds to max alignment.
- 30/08: {short,char,int*,float} — offsets right, forgot tail pad again mid-answer (20 → 24); reorder to 16 — ok. Tail-pad reflex landed by rep 3.
- 31/08: {char,int,char,long} = 24 — total right, internal map wrong (pad-7 before long, zero tail). Compute offsets, not a padding shopping list.

<!-- gc-questions:start -->

## Related getcracked questions

Pulled from the Beginner C++ progress tree. ✓ answered correctly, ✗ attempted and missed, ○ not attempted yet. Regenerate with `python3 cpp/tools/gc_links.py` after re-scraping.

### Object Sizes
- ✓ [Satisfy me!](https://getcracked.io/question/1470) — Easy
- ✗ [Understand lambdas, understand C++.](https://getcracked.io/question/1070) — Easy

### Heap
- ✓ [Can you treat me as an equal?](https://getcracked.io/question/1082) — Easy
- ✗ [They're stacked.](https://getcracked.io/question/1277) — Easy

### char, const char*, and string
- ✓ [0.0_7](https://getcracked.io/question/975) — Easy
- ✓ [Char + Char](https://getcracked.io/question/674) — Easy
- ✓ [String placement](https://getcracked.io/question/1216) — Easy
- ✓ [String them together.](https://getcracked.io/question/996) — Easy
- ✓ [What's a character?](https://getcracked.io/question/847) — Easy
- ✗ [Where did it go?](https://getcracked.io/question/757) — Easy
- ✗ [You don't understand strings.](https://getcracked.io/question/699) — Easy
- ✗ [Another string question?](https://getcracked.io/question/1423) — Medium
- ✗ [Change it for me.](https://getcracked.io/question/870) — Medium
- ✗ [GG](https://getcracked.io/question/687) — Medium
- ✗ [More chars more problems.](https://getcracked.io/question/858) — Medium
- ✓ [Pointers to Pointers to Pointers](https://getcracked.io/question/767) — Medium
- ✗ [Signed Char == Unsigned Char?](https://getcracked.io/question/381) — Medium
- ✗ [What even is a string?](https://getcracked.io/question/881) — Medium
- ✗ [What's zero?](https://getcracked.io/question/818) — Medium
- ○ [Implement std::string](https://getcracked.io/problem/90/implement-std-string) — problem

### Small String Optimization
- ✓ [SOO, about that object.](https://getcracked.io/question/1206) — Easy
- ○ [Implement std::string](https://getcracked.io/problem/90/implement-std-string) — problem

<!-- gc-questions:end -->
