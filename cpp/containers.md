# std::array & std::vector: Fixed and Dynamic Arrays

## Containers and the three array types

A container stores a collection of unnamed elements behind one named object and gives back the number of elements, access to them, and ways to add and remove. C++ containers are homogeneous class templates: the element type is a template argument. The word "length" here means the number of elements, and "size" means bytes as `sizeof` reports them, though the standard library uses `size()` for the element count. An array is a container whose elements sit contiguously with no per-element overhead, which is what makes random access a pointer addition and makes arrays the default choice for a sequence. C++ has three: the C-style array inherited from C, in [arrays.md](arrays.md); `std::vector`, from C++03, the resizable one and the default; and `std::array`, from C++11, the fixed-size replacement for C-style arrays. Use `std::vector` unless the length is a compile-time constant and you want `constexpr`, in which case `std::array` is the only one of the three that fully supports it.

## std::array

`std::array<T, N>` from `<array>` is a struct wrapping one C-style array member, so it has the same layout, the same zero overhead, and sits on the stack when local, but it does not decay, copies as a value, and knows its own length. The length `N` is a `std::size_t` non-type template parameter and must be a constant expression: a literal, a `constexpr` variable, or an enumerator; a `const int` initialized from a runtime value does not work. A zero-length `std::array` is legal and is an empty class, unlike a zero-length C-style array.

It is an aggregate, so it has no constructors and is initialized with braces in element order. Without an initializer the elements are default-initialized, which leaves fundamental types indeterminate, so write `std::array<int, 5> a{};` to value-initialize. Too many initializers is an error, too few leaves the rest value-initialized. A `const std::array` makes every element const, and a `constexpr std::array` is the reason to use the type at all. Since C++17 class template argument deduction fills in both arguments from the initializers, `std::array a{1, 2, 3};`, and that is the preferred form; deduction cannot omit just one of the two arguments, so to fix the element type and deduce the length use C++20's `std::to_array<short>({1, 2, 3})`, which costs a temporary and a copy and is only for that case.

Because `std::array` is a struct holding a C-style array, an array of structs initialized without naming the element type needs double braces: `std::array<House, 3> h{{{13, 1, 7}, {14, 2, 5}, {15, 2, 4}}};`. With single braces the compiler treats `{13, 1, 7}` as the initializer for the inner C-style array member, not for element zero. Brace elision lets you drop the extra braces when the elements are scalars or when each initializer names its type, and there is no harm in always writing the double braces. When a `constexpr` array is initialized by deduction, a `static_assert(std::size(arr) == expected)` catches a missing initializer, which is the standard way to keep a name table in step with an enumeration; a `constexpr std::array` of enumerators is also how you iterate an enumeration with a range-based for, since the language cannot iterate an enum directly.

Length and indices have type `size_type`, which for `std::array` is always `std::size_t`. `size()`, `std::size()`, and C++20 `std::ssize()` return the length, and because `N` is a template argument they return a constant expression even on a non-constexpr array, so the length can size another array or feed a `static_assert`. `operator[]` does no bounds check; `at()` checks at runtime and throws `std::out_of_range`; `std::get<I>(arr)` checks at compile time through a `static_assert` in its implementation and therefore only accepts a constexpr index. A constexpr signed index converts to `std::size_t` without narrowing; a runtime signed index is a narrowing conversion and may warn.

Pass a `std::array` by const reference, and because the length is part of the type, a function taking `const std::array<int, 5>&` accepts only that length. To accept any element type or length, write `template <typename T, std::size_t N> void f(const std::array<T, N>&)`, or `template <auto N>` in C++20 to avoid naming the length's type; class template argument deduction does not apply to function parameters. Inside such a template `N` is a constant, so `static_assert(N > 3)` or `std::get<3>(arr)` turns an out-of-range access into a compile error rather than undefined behavior. `std::array` is not move-capable beyond moving its elements, so returning one by value copies the array; that is acceptable when the array is small, cheap to copy, and the function is not hot, otherwise fill an out-parameter by reference, or return a `std::vector`, which moves.

## std::vector: construction and access

`std::vector<T>` from `<vector>` owns a heap buffer and can change its length after construction. `std::vector<int> v{};` is empty. A braced list of values calls the list constructor, which sets the length to the number of values, allocates exactly that much, and copies them in; with C++17 deduction `std::vector primes{2, 3, 5, 7};` infers `int`. The elements of a braced list are evaluated left to right, in order, unlike function arguments, so `c({a(), b()})` prints `ab` before `c` runs and the order is guaranteed, not unspecified.

The other common constructor is `explicit std::vector<T>(std::size_t n)`, which makes `n` value-initialized elements. Because it is explicit, `std::vector<int> v = 10;` does not compile, and because a non-empty braced list prefers the list constructor, `std::vector<int> v{10};` is one element holding ten while `std::vector<int> v(10);` is ten zeros. Empty braces prefer the default constructor. The length constructor therefore needs parentheses and an explicit element type. A `const std::vector` cannot be modified and its elements behave as const, but the element type itself may not be const: `std::vector<const int>` is disallowed. `std::vector` cannot be `constexpr` in any useful way; for compile-time data use `std::array`.

`operator[]` returns a reference to the element with no bounds check, and an out-of-range index is undefined behavior; there is no element at index `size()`. `at()` checks the index at runtime and throws `std::out_of_range` on failure, and is the one behavioral difference between the two: both have const and non-const overloads and both return references. `at()` is slower and rarely the right tool, because the check belongs before the index is formed. The length and index type is `std::vector<T>::size_type`, normally `std::size_t`, so `size()` and `std::size()` return unsigned and `std::ssize()` returns signed `std::ptrdiff_t`. The unsigned choice dates from 1997 and is widely regarded as a mistake because it forces signed-to-unsigned conversions everywhere. A constexpr signed index converts without narrowing; a runtime signed `int` index is a narrowing conversion that compilers warn about, and the least intrusive fix is to keep the loop variable as `std::size_t` and use it only for indexing.

## std::vector: passing, returning, and moving

Pass a vector by const reference; by value copies the whole buffer. The element type is part of the type, so `const std::vector<int>&` rejects a `std::vector<double>`, and deduction does not help in a parameter, so a function for any element type is a template on `T`, or an abbreviated `auto` parameter in C++20, which then also accepts anything else that compiles. A function that assumes a minimum length can only assert on `size()` at runtime, because a vector's length is not a constant; better not to write such a function.

Returning a vector by value is fine, and the reason is move semantics. Copy semantics means the destination gets its own buffer with the same contents, which is right when both objects live on. When the source is a temporary about to die, copying and then destroying the original is waste, so C++11 lets the destination take over the buffer instead: a move is a pointer swap, and the dying temporary then has nothing to free. Move semantics is invoked when the type supports it, the initializer or right-hand side is an rvalue, and the copy was not elided; a return value is an rvalue, so returning a vector costs nothing beyond the pointer transfer even when elision does not apply. Of the four copies in pass-and-return, constructing the argument and constructing the return value are inherent; passing is best done by const reference, and returning by value is elided or moved. See [smart_pointers_move.md](smart_pointers_move.md) for the mechanics.

## std::vector: length, capacity, and stack use

`resize(n)` changes the length, keeping existing elements and value-initializing new ones, so `int` elements appear as zeros. Capacity is how many elements the vector has storage for, and length is how many are in use; `capacity()` reports the first, `size()` the second. Growing beyond the capacity forces a reallocation: allocate a new buffer, copy or move every element across, free the old one. That is proportional to the length and is the expensive operation to avoid. Keeping capacity separate from length lets a vector shrink and regrow without reallocating: after `resize(3)` on a five-element vector the capacity stays five, and `resize(5)` again costs nothing. Valid indices are bounded by the length, never the capacity, so storage that exists past `size()` is still out of bounds. Shrinking never releases memory; `shrink_to_fit()` asks for the capacity to match the length and the implementation may ignore or partially honour the request.

Used as a stack, a vector grows with `push_back` and `emplace_back` and shrinks with `pop_back`, with `back()` reading the top and `size()` the depth. A push past the capacity reallocates, and each such reallocation reserves extra room, doubling on GCC and Clang and growing by half on MSVC, so pushes are amortized constant. To avoid the early reallocations, `reserve(n)` raises the capacity without touching the length; `resize(n)` or the length constructor would also create `n` elements, which is wrong for a stack. `push_back(x)` copies or moves an existing object in; `emplace_back(args...)` forwards the arguments and constructs the element in place, which avoids a temporary when the element is built at the call site. `emplace_back` will use explicit constructors and, before C++20, cannot aggregate-initialize, so prefer `push_back` when the object already exists and `emplace_back` only for in-place construction. A vector of function pointers or lambdas behaves like any other: `functions.push_back(functions.front())` copies the first pointer, and iterating the vector calls each in turn, so a print, an increment, and the print again yields `01`.

## std::vector internals

A `std::vector` is three pointers of type `T*`: `first`, the start of the allocation, `last`, one past the last live element, and `end`, one past the end of the allocated storage. `size()` is `last - first`, `capacity()` is `end - first`, the region up to `last` holds constructed objects, and the region between `last` and `end` is raw storage with nothing constructed in it. The allocator is conceptually a fourth member, but the default allocator is an empty class stored in a compressed pair with one of the pointers, so it takes no space and `sizeof(std::vector<int>)` is 24 on a 64-bit system whatever the element type and whatever `reserve` was called with; the elements live on the heap, not in the object. libstdc++ names the members `_M_start`, `_M_finish`, and `_M_end_of_storage`; libc++ uses `__begin_`, `__end_`, and `__end_cap_`; MSVC uses `_Myfirst`, `_Mylast`, and `_Myend` inside `_Mypair._Myval2`. There is no small-vector optimization because the standard requires that moving a vector leaves iterators and references to its elements valid, which an inline buffer would break; `std::string` may use SSO because a string move is allowed to invalidate.

When `push_back` finds `last == end`, the vector allocates a larger block, moves or copies every element across, destroys the old ones, and frees the old block. libstdc++ and libc++ double the capacity; MSVC grows by one and a half times, which lets freed blocks be reused for a later growth because the sum of the earlier blocks exceeds the new one once the factor is below the golden ratio. Any factor above one gives amortized constant `push_back`. Elements are moved only if `T`'s move constructor is `noexcept`, through `std::move_if_noexcept`; otherwise they are copied to keep the strong exception guarantee, which is the practical reason to mark move constructors `noexcept`. Reallocation invalidates every iterator, pointer, and reference: `auto b = v.begin(); v.push_back(3); *b` on a two-element vector reads freed memory and is undefined behavior, while the same sequence after `v.reserve(3)` prints `1` because nothing moved. `std::vector<Bar> bar(5)` value-initializes five elements by calling the default constructor five times; since C++11 no prototype element is copied, so a `Bar` that prints `1` on default construction and `2` on copy prints `11111`. Pre-C++11 the same line printed `12222`.

`std::vector<bool>` is a mandated specialization that packs one bit per element and is therefore not a container of `bool`: `operator[]` returns a proxy `reference`, not `bool&`, `data()` does not exist, `auto x = v[i]` deduces the proxy, and writes to different elements from different threads race on the shared byte. Use `std::vector<char>` or `std::vector<std::uint8_t>` for a real element container, `std::bitset<N>` for a fixed size, and `std::deque<bool>` when an actual `bool` container of dynamic size is required.

```cpp
template <typename T> struct vector { T* first; T* last; T* end; };   // 24 bytes, allocator compressed away
std::vector<int> v{ 1, 2 };
auto b = v.begin();
v.push_back(3);           // capacity 2 exceeded: reallocate, b dangles, *b is UB
v.reserve(3); auto c = v.begin(); v.push_back(4); *c;   // still 1: no reallocation
```

## Errors and pitfalls

- **Undefined behavior: an iterator, pointer, or reference held across a `push_back` that exceeds capacity.** Reallocation moves everything; `reserve` first if the handle must survive.
- **Logical error: expecting `sizeof(v)` to change with `reserve` or elements.** The object is three pointers, 24 bytes; the buffer is on the heap.
- **Logical error: a throwing move constructor.** The vector copies on reallocation instead of moving; mark moves `noexcept`.
- **Logical error: treating `std::vector<bool>` as a container of `bool`.** Proxy references, no `data()`, no `bool&`.
- **Invalid: `std::vector<int> v = 10;`** The length constructor is explicit; write `v(10)`.
- **Invalid: `std::vector<const int>`.** Make the vector const instead.
- **Invalid: a `std::array` whose length is a runtime value**, or single braces on an array of structs without naming the element type.
- **Invalid: `std::get<i>(arr)` with a runtime `i`**, or with a constexpr index out of range, which is a compile error by design.
- **Undefined behavior: `operator[]` out of range on either container**, including indices between `size()` and `capacity()`.
- **Runtime error: `at()` out of range throws `std::out_of_range`.**
- **Logical error: `std::vector<int> v{10};` is one element.** `v(10)` is ten zeros.
- **Logical error: `resize` or the length constructor to pre-size a stack.** They add elements; `reserve` sets capacity only.
- **Logical error: expecting `shrink_to_fit` to free memory.** It is a non-binding request.
- **Logical error: returning a `std::array` by value from a hot function.** It copies; return a vector or fill an out-parameter.
- **Warning trap: indexing with a runtime `int`.** Narrowing to `size_type`; index with a `std::size_t` variable.

## Additional syntax examples

```cpp
std::array a{1, 2, 3};                         // C++17 CTAD: std::array<int, 3>
std::array<int, 5> z{};                        // value-initialized zeros
constexpr std::array names{"red"sv, "green"sv}; static_assert(std::size(names) == 2);
std::array<House, 2> h{{{13, 1, 7}, {14, 2, 5}}};   // double braces without element type
auto s = std::to_array<short>({1, 2, 3});      // C++20, deduce length only
std::get<1>(a);                                // compile-time bounds check

template <typename T, std::size_t N> void f(const std::array<T, N>& arr) { static_assert(N > 0); }
template <auto N> void g(const std::array<int, N>&);   // C++20

std::vector<int> v(10);        // ten zeros
std::vector<int> w{10};        // one element, 10
w.reserve(100);                // capacity 100, length 1
w.resize(4);                   // length 4, new elements zero
w.push_back(5); w.emplace_back(6); w.pop_back(); w.back();
w.at(50);                      // throws std::out_of_range
for (std::size_t i = 0; i < w.size(); ++i) w[i];
std::ssize(w);                 // C++20, signed
```

## Interview Q&A

### What is `sizeof(std::vector<int>)` after `reserve(3)` on a 64-bit system?

24. The object is three pointers, begin, end of elements, and end of storage, with the empty default allocator compressed to zero bytes. Capacity and elements live on the heap and never change the object's size.

### `std::vector<Bar> bar(5);` where `Bar` prints `1` on default construction and `2` on copy. Output?

`11111`. Since C++11 the count constructor value-initializes each element in place; no prototype is built and copied. Pre-C++11 the signature took a `const T&` default argument and printed `12222`.

### `auto b = v.begin(); v.push_back(3); std::cout << *b;` on `std::vector<int> v{ 1, 2 }`. And after `v.reserve(3)` first?

Junk and undefined behavior in the first case: capacity is 2, the push reallocates, and `b` points into freed memory. With the reserve the push stays inside capacity, nothing moves, and it prints `1`.

### Why does `std::vector` have no small-buffer optimization when `std::string` does?

Moving a vector must keep iterators and references to its elements valid, so the elements cannot live inside the object and move with it. A string move is permitted to invalidate, so SSO is allowed.

### Why should a move constructor be `noexcept` if the type goes into a vector?

Reallocation uses `std::move_if_noexcept`. A move that might throw would leave the old buffer half-moved with no way to restore it, so the vector copies instead to keep the strong guarantee, and the move constructor is never used.

### What is the one real difference between `v[i]` and `v.at(i)`?

Bounds checking. `at()` validates the index at runtime and throws `std::out_of_range`; `operator[]` does not check and an invalid index is undefined behavior. Both return references, both have const overloads, and `at()` is the slower one because of the check. In practice validate the index first and use `operator[]`.

### `std::vector<int> v{10};` versus `std::vector<int> v(10);`

A non-empty braced list prefers the list constructor, so the first is a one-element vector containing ten. The second calls the explicit length constructor and holds ten value-initialized zeros. The length constructor cannot be reached with braces, an `=`, or deduction.

### Why separate length from capacity?

Reallocation copies every element and is the expensive operation. With capacity tracked separately, shrinking and regrowing within the existing storage costs nothing, and pushing reserves extra room so a sequence of pushes reallocates a logarithmic number of times. `reserve` sets capacity without creating elements; `resize` sets both.

### Why is it fine to return a `std::vector` by value but not to pass one by value?

Passing by value copies a buffer the caller still needs, and moving from an lvalue argument would empty the caller's vector. Returning yields an rvalue, so the destination takes over the buffer by a pointer swap, or the copy is elided entirely. A `std::array` has no buffer to hand over, so returning it by value really does copy the elements.

### What is printed by `c({a(), b()})` where `a` and `b` print their names?

`ab`. The elements of a braced initializer list are evaluated left to right in order, which the standard guarantees, unlike the unspecified order of ordinary function arguments. The list is built first, then the vector, then `c` runs.

### Why does an array of structs in a `std::array` sometimes need double braces?

Because `std::array` is a struct with one member, the C-style array. Single braces make the compiler treat the first inner list as the initializer for that member rather than for element zero. Brace elision rescues the scalar case and the case where each element names its type; otherwise write the extra braces.

## Practice history

### Reading

- 13/09/2026 (later): Raymond Chen, Inside STL: the vector; the Medium vector guide returned 403 and was not read, growth factors and `vector<bool>` are from the standard and library sources. Implement vector problem not attempted.
- 13/09/2026: learncpp 17.1 (introduction to std::array), 17.2 (length and indexing), 17.3 (passing and returning), 17.4 (arrays of class types and brace elision), 17.6 (std::array and enumerations); Raymond Chen, Inside STL: the array. learncpp 16.1 (containers and arrays), 16.2 (std::vector and list constructors), 16.3 (unsigned length and subscript problem), 16.4 (passing std::vector), 16.5 (returning std::vector and move semantics), 16.10 (resizing and capacity), 16.11 (stack behavior). Bo Qian STL videos not watched.

### Questions (getcracked)

- Per platform record, rescraped 13/09/2026. std::vector: Don't @ me (`at()` bounds-checks, `[]` does not) ok. Containers for containers. (vector of function pointers, prints 01) ok. A, B, C, initializer_list (`c({a(), b()})` prints ab; braced-list elements evaluate left to right) wrong first attempt, retest in a week. Build a Histogram and Yeah, I know what a call stack is. problems not attempted. std::array: Array extensioooooons (a variable-length array is a compiler extension that adjusts the stack pointer at runtime, no malloc or new; filed in [arrays.md](arrays.md)) wrong first attempt, retest in a week.
- 13/09/2026 Internals node, per platform record: How does it allocate? (`vector<Bar>(5)` default-constructs five times, 11111) ok, Vector growth 2 (after `reserve(3)` the push does not reallocate, prints 1) ok; wrong first attempt (retest in a week): Vector growth 1 (push past capacity reallocates, the old iterator is UB), So, how big is vector? (`sizeof` is 24, three pointers, reserve does not change it).
- Anki: vector is three pointers, 24 bytes; push past capacity invalidates everything, reserve prevents it; count constructor default-constructs in place since C++11; moves happen only if noexcept; braced list evaluates in order, function arguments do not; `{10}` is one element, `(10)` is ten; `reserve` is capacity only; `at()` throws, `[]` is UB; `std::array` of structs needs double braces without element type; `std::get` is compile-time checked.

<!-- gc-questions:start -->

## Related getcracked questions

Pulled from the Beginner C++ progress tree. ✓ answered correctly, ✗ attempted and missed, ○ not attempted yet. Regenerate with `python3 cpp/tools/gc_links.py` after re-scraping.

### std::array
- ✗ [Array extensioooooons](https://getcracked.io/question/1279) — Medium

### std::vector
- ✓ [Don't @ me](https://getcracked.io/question/843) — Cooked
- ✗ [A, B, C, initializer_list](https://getcracked.io/question/820) — Easy
- ✓ [Containers for containers.](https://getcracked.io/question/1100) — Easy
- ○ [Build a Histogram](https://getcracked.io/problem/46/build-a-histogram) — problem
- ○ [Yeah, I know what a call stack is.](https://getcracked.io/problem/19/yeah-i-know-what-a-call-stack-is) — problem

### Internals
- ✓ [How does it allocate?](https://getcracked.io/question/849) — Cooked
- ✓ [Vector growth 2](https://getcracked.io/question/544) — Cooked
- ✗ [Vector growth 1](https://getcracked.io/question/543) — Easy
- ✗ [So, how big is vector?](https://getcracked.io/question/764) — Medium
- ○ [Implement vector](https://getcracked.io/problem/1/implement-vector) — problem

<!-- gc-questions:end -->
