# C-Style Arrays: Declaration, Decay & Pointer Arithmetic

## Declaring and initializing

A C-style array is declared with the element type, a name, and a length in square brackets: `int testScore[30]{};` is thirty value-initialized ints laid out contiguously with no header, so `sizeof` on the array is exactly the elements' bytes. The length must be an integral constant expression of at least one: a `const int` initialized from a literal or a `constexpr` works, a runtime variable does not, and zero, negative, and non-integral lengths are errors. Some compilers accept a runtime length as a C99 extension; that is a variable-length array, not C++, and should be disabled with the compiler's pedantic flags. `int i[0];` is ill-formed, not undefined behavior: the program is rejected, though GCC and Clang accept it as an extension unless told to be strict.

Elements are accessed with `operator[]`, which accepts any integral or unscoped enumeration index, signed or unsigned, and performs no bounds check. Indexing outside `[0, length)` is undefined behavior. Initialization is aggregate initialization from a braced list, with `int prime[5]{2, 3, 5, 7, 11};` preferred over the `=` form. Too many initializers is an error; too few leaves the rest value-initialized, so `int b[4]{1, 2};` has zeros in the last two. Empty braces value-initialize everything, which is why `int arr[5]{};` is preferred to `int arr[5];`, whose elements are indeterminate. When every element is listed, omit the length and let the compiler count: `const int prime[]{2, 3, 5, 7, 11};` cannot drift out of sync with its initializer. `int bad[]{};` is an error because the deduced length would be zero. `auto` cannot deduce an array type from a braced list, so `auto squares[5]{...}` does not compile. A `const` or `constexpr` array must be initialized and its elements cannot be assigned afterwards; `constexpr` arrays of program data belong in a namespace at global scope, which is the one place C-style arrays are still the right default.

Because an array has no length field, the length comes from the type. `sizeof(prime)` is the whole array in bytes, and the old `sizeof(arr) / sizeof(arr[0])` idiom divides that by one element. Since C++17 `std::size(arr)` from `<iterator>` returns the length as `std::size_t`, and since C++20 `std::ssize(arr)` returns it signed; both refuse to compile on a pointer, which the `sizeof` idiom does not. Before C++17 the same guarantee comes from a template that deduces the length from a reference-to-array parameter: `template <typename T, std::size_t N> constexpr std::size_t length(const T(&)[N]) { return N; }`.

## Array decay

In most expressions an array is implicitly converted to a pointer to its first element: `int[5]` becomes `int*` holding `&arr[0]`, and the length is gone. This is decay. It does not happen in four places: as the operand of `sizeof` or `typeid`, as the operand of unary `&`, when the array is a member of a class type, and when the array is bound to a reference. `&arr` is a pointer to the whole array, of type `int(*)[5]`, which is why `&arr + 1` advances by the whole array and `arr + 1` by one element; that comparison is worked through in [pointers_references.md](pointers_references.md).

Decay is why arrays are passed "by address even when it looks like by value". A parameter written `int arr[]` or `int arr[10]` is adjusted to `int*`; the bracketed length is ignored, and two arrays of the same element type but different lengths decay to the same pointer type, so one function accepts both. The array syntax in the parameter is still preferred because it documents intent, and it should be `const` unless the function means to modify the caller's elements, which it can since it has the original storage, not a copy. A `const int[5]` decays to `const int*`. The design goal was C's: avoid copying large arrays into functions and let one function handle any length.

The cost is that the callee cannot know the length. `sizeof(arr)` inside `void f(int arr[])` is the size of a pointer, so the division idiom silently returns the wrong count, and `std::size(arr)` refuses to compile, which is the better failure. A function that indexes `arr[2]` compiles for a two-element array and for `&c` where `c` is a single `int`, and both are undefined behavior at runtime. The workarounds are passing the length as a separate parameter, ideally asserted, or a sentinel value at the end as C strings do with the null terminator. The modern answer is not to use C-style arrays at the call boundary: `std::string_view` for read-only strings, `std::string` for mutable ones, `std::array` for fixed-size non-global data, `std::vector` for everything sized at runtime, and `std::span` when a function must accept any contiguous range with its length.

Decay also interacts with `auto` and `typeid`. `auto y = arr1;` copy-initializes from a decayed value, so `y` is `int*`. `auto& x = arr1;` binds a reference, so `x` is `int(&)[2]`. `typeid` ignores top-level references and cv-qualifiers, so `typeid(arr1) == typeid(x)` is true and `typeid(arr1) == typeid(y)` is false. An array member `int b[2]` keeps its array type, a reference member `int (&a)[2]` reports the array type through `typeid`, and two arrays with different lengths are different types, so `int[2]` and `int[3]` compare unequal while two `int*` deduced from arrays of different lengths compare equal.

## Pointer arithmetic and subscripting

Adding an integer to a pointer produces the address of that many objects further on, scaled by the pointed-to type: for `int* p`, `p + 1` is four bytes ahead on a system with four-byte ints, `p - 1` four bytes back, and `++p` and `--p` move `p` itself. Subtracting two pointers into the same array gives the element distance as a `std::ptrdiff_t`. The arithmetic is only defined while the pointer and the result stay within one array or at its one-past-the-end position; the one-past pointer may be formed and compared but not dereferenced. Arithmetic on a pointer to a single object is allowed only for the object itself and one past it, so anything further is undefined even if nothing crashes.

Subscripting is pointer arithmetic with a dereference: `ptr[n]` is defined as `*((ptr) + (n))`. Since `arr` decays to `&arr[0]`, `arr[n]` and `*(arr + n)` are the same expression, `&arr[n]` equals `arr + n`, and `arr[0]` is `*arr`. That definition has two consequences people find surprising. Addition commutes, so `n[ptr]` is legal and means `*(n + ptr)`; the `2["123"]` puzzle indexes the string literal, which decays to `const char*`, and prints `3`. Indices are relative to whatever the pointer currently points at, not to the start of any array, so if `ptr = &arr[3]` then `ptr[0]` is element three, `ptr[1]` is element four, and `ptr[-1]` is element two. Zero-based indexing exists because element `n` is at offset `n` without a subtraction. Prefer subscripting when indexing from the start of an array, and pointer arithmetic when moving relative to a given element.

Traversal with a pair of pointers is the model behind every iterator loop: `const int* begin = arr; const int* end = arr + std::size(arr); for (; begin != end; ++begin)`. Passing `begin` and `end` to a function sidesteps decay entirely, because the length travels as the difference between the two pointers. A range-based for over a C-style array expands to exactly that loop, with `__begin = arr` and `__end = arr + std::size(arr)`, which is also why range-for cannot work on a decayed pointer parameter.

Multidimensional arrays are one contiguous block in row-major order, and pointer arithmetic on a pointer to a sub-array steps by the whole sub-array. For `int array[2][5][2]`, `int (*p)[5][2] = array;` points at the first `[5][2]` block of ten ints, `p + 1` is the second block, and casting that to `int*` and adding `(1 * 2) + i` reaches flat elements ten plus two plus `i`. With the initializer filled in order, flat elements twelve and thirteen are `3` and `4`, so the loop prints `34`. Work these by flattening the index rather than by visualizing the nesting.

## Heap arrays and stack limits

`new int[10]` allocates on the free store and must be released with `delete[]` on the pointer the allocation returned. Incrementing that pointer and then calling `delete[]` is undefined behavior, since the deallocation function receives an address it never handed out; `arr` "still being inside the array" is irrelevant. The same holds for arrays of class type: `auto t = new std::shared_ptr<char>[15];` is an array of fifteen shared pointers, released with `delete[] t;`, which runs each element's destructor and then frees the block. Plain `delete t;` on an array is undefined behavior, and neither form is needed if the array is held by `std::unique_ptr<T[]>` or `std::vector` in the first place; see [smart_pointers_move.md](smart_pointers_move.md).

A local array lives on the stack, and the stack is small: typically eight megabytes on Linux and one on Windows. `int hugeArray[10000000];` is forty megabytes of automatic storage, so the program overflows the stack on entry to `main` and typically dies with a segmentation fault, even though the declaration compiles without complaint and the elements it touches are the first two. Nothing moves it to the heap for you. Large or runtime-sized data belongs in a `std::vector`, or in `static` or namespace-scope storage if its size is fixed. The stack-versus-heap layout is in [memory_layout.md](memory_layout.md).

## Errors and pitfalls

- **Invalid: non-constant length.** `int n = 5; int arr[n];` is not C++; compilers that accept it are applying a C99 extension.
- **Invalid: zero length.** `int i[0];` and `int bad[]{};` are ill-formed.
- **Invalid: too many initializers.** `int a[4]{1, 2, 3, 4, 5};` is rejected.
- **Invalid: `auto` with an array declarator.** `auto squares[5]{1, 4, 9, 16, 25};` does not compile.
- **Invalid: `std::size` on a decayed parameter.** The compile error is the point; the `sizeof` division idiom compiles and is wrong.
- **Undefined behavior: out-of-bounds subscript**, including the one-past position, and pointer arithmetic that leaves the array.
- **Undefined behavior: `delete[]` on anything but the pointer `new[]` returned**, and `delete` without brackets on an array.
- **Undefined behavior in practice: a multi-megabyte local array.** Stack overflow is not diagnosed by the compiler.
- **Logical error: `(*arr + 1)`** is element zero plus one, not element one. `*(arr + 1)`, `arr[1]`, and `1[arr]` are the second element.
- **Logical error: `auto y = arr;` is a pointer.** Use `auto& y = arr;` to keep the array type.

## Additional syntax examples

```cpp
constexpr int squares[]{0, 1, 4, 9};            // length deduced, namespace-scope constexpr is fine
int zeros[8]{};                                 // all zero
int partial[4]{1, 2};                           // {1, 2, 0, 0}

std::size(squares);                             // 4, C++17, <iterator>
std::ssize(squares);                            // 4 as a signed value, C++20
sizeof(squares) / sizeof(squares[0]);           // 4, but silently wrong on a pointer

void print(const int arr[], int n);             // arr is const int*; n carries the length
void print(const int* begin, const int* end);   // length is end - begin
void print(std::span<const int> s);             // C++20: any contiguous range, with size()

int (*pa)[4] = &squares_mutable;                // pointer to the whole array
const char* s = "123"; s[2]; 2[s]; *(s + 2);   // all '3'
```

## Interview Q&A

### Why does passing an array to a function lose its length?

Because the array decays to a pointer to its first element at the call, and a pointer carries no length. The parameter `int arr[]` is really `int*`, `sizeof(arr)` inside the function is the pointer's size, and `std::size(arr)` refuses to compile. Either pass the length or an end pointer alongside, or pass a reference to the array with its length as a template parameter, or use `std::span`, `std::array`, or `std::vector` and let the type carry it.

### Is `2["123"]` valid, and what does it print?

Valid, prints `3`. Subscripting is defined as `*((a) + (b))`, addition commutes, and the string literal decays to `const char*`, so `2["123"]` is `*("123" + 2)`, the character `'3'`. It is a party trick, not a style.

### What is wrong with `int* arr = new int[10]; arr++; delete[] arr;`?

`delete[]` must receive exactly the pointer `new[]` returned. After the increment it receives the address of element one, which the allocator never handed out, so the deallocation is undefined behavior regardless of the pointer still being inside the block. Keep the original pointer, or hold the array in a `std::unique_ptr<int[]>` and never touch the raw pointer.

### Why does `int hugeArray[10000000];` crash even though the program only writes two elements?

The array is automatic storage, so its full forty megabytes are reserved on the stack when `main`'s frame is set up, and the default stack is a few megabytes. The overflow happens at frame entry, before any element is touched. Nothing in the language moves a large local to the heap; that is the programmer's job, with `std::vector` or static storage.

### Given `int arr[2]` and `auto& x = arr; auto y = arr;`, what are the types of `x` and `y`, and what does `typeid` say?

`x` is `int(&)[2]` because binding a reference does not decay the array. `y` is `int*` because copy-initialization uses the decayed value. `typeid` strips references, so `typeid(x) == typeid(arr)` is true and `typeid(y) == typeid(arr)` is false. Arrays of different lengths are different types, so `int[2]` and `int[3]` differ, while two pointers deduced from them are both `int*` and compare equal.

## Practice history

### Reading

- 13/09/2026: learncpp 17.7 (introduction to C-style arrays), 17.8 (C-style array decay), 17.9 (pointer arithmetic and subscripting). Multidimensional arrays (17.12) and the std::array chapter not yet read.

### Questions (getcracked)

- 13/09/2026 C-Style Arrays node, per platform record: #square (`2["123"]` prints 3) ok. The headers you never knew (`arr++; delete[] arr;` is not safe, wrong pointer to the deallocator) ok. 3D Arrays (`int(*p)[5][2]`, `(int*)(p + 1) + 2 + i` reaches flat elements 12 and 13, prints 34) ok. Allocation decisions (ten-million-int local array overflows the stack) ok. To delete or not to delete (`new std::shared_ptr<char>[15]` needs `delete[] t;`) ok. Array, Array, go away, come again another day. (typeid on array vs reference vs decayed pointer, prints 1011011) ok. Wrong first attempt (retest in a week): Indexing arrays (`(*arr + 1)` is element zero plus one, the one option that is not the second element). [0] (`int i[0];` is ill-formed, not UB or implementation-defined). 3D Space coding problem not attempted.
- Anki: `int i[0]` is ill-formed; `(*arr + 1)` is not `arr[1]`; `delete[]` needs the original pointer; `auto` from an array is a pointer, `auto&` keeps the array; `typeid` strips references.

<!-- gc-questions:start -->

## Related getcracked questions

Pulled from the Beginner C++ progress tree. ✓ answered correctly, ✗ attempted and missed, ○ not attempted yet. Regenerate with `python3 cpp/tools/gc_links.py` after re-scraping.

### C-Style Arrays
- ✓ [#square](https://getcracked.io/question/517) — Cooked
- ✗ [Indexing arrays](https://getcracked.io/question/725) — Cooked
- ✓ [The headers you never knew](https://getcracked.io/question/423) — Cooked
- ✓ [3D Arrays](https://getcracked.io/question/768) — Easy
- ✓ [Allocation decisions](https://getcracked.io/question/787) — Easy
- ✓ [To delete or not to delete](https://getcracked.io/question/1024) — Easy
- ✗ [[0]](https://getcracked.io/question/783) — Medium
- ✓ [Array, Array, go away, come again another day.](https://getcracked.io/question/860) — Medium
- ○ [3D Space](https://getcracked.io/problem/8/3d-space) — problem

<!-- gc-questions:end -->
