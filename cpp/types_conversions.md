# Integral Types, Promotions & Conversions

## Signed and unsigned arithmetic

Signed arithmetic overflow has undefined behavior. Examples include `INT_MAX + 1`, negating `INT_MIN`, and dividing `INT_MIN` by `-1`. The language does not require these expressions to wrap, even on a machine using two's complement. Optimizers can assume that a well-defined execution does not overflow.

Unsigned arithmetic is performed modulo 2 raised to the number of value bits. For an eight-bit unsigned type, converting 280 produces 24. Subtracting one from unsigned zero produces that type's maximum value. This is useful for bit patterns, but it can hide mistakes such as subtracting one from an empty container's size.

An integral conversion is a different operation from arithmetic overflow. Since C++20, conversion to an integer type of width N, other than `bool`, produces the destination value that differs from the source by a multiple of 2^N. For example, converting 255 to an eight-bit signed integer produces -1. Before C++20, an out-of-range conversion to a signed integer type was implementation-defined. List-initialization still rejects narrowing conversions, and an out-of-range floating-point-to-integer conversion still has undefined behavior.

Plain `char` may be signed or unsigned. A result involving `char` therefore needs that assumption stated; do not silently assume an eight-bit signed character type.

## Promotions and the usual arithmetic conversions

Before many arithmetic and bitwise operations, types such as `bool`, `char`, and `short` undergo integral promotion. They promote to `int` if it can represent every value of the source type, or to `unsigned int` otherwise. On common machines with 32-bit `int` and 16-bit `short`, even `unsigned short` promotes to signed `int`. Other platforms can differ.

After promotion, binary arithmetic finds a common type. For mixed signed and unsigned integers:

1. If the unsigned type's rank is at least the signed type's rank, the signed operand converts to the unsigned type.
2. Otherwise, if the signed type can represent all values of the unsigned type, the unsigned operand converts to the signed type.
3. Otherwise, both convert to the unsigned counterpart of the signed type.

```cpp
unsigned short a = 0, b = 1;
bool first = a - b > 0;       // False when both promote to int.
unsigned int c = 0, d = 1;
bool second = c - d > 0;      // True: subtraction wraps in unsigned int.
```

The first subtraction produces signed `-1` on the stated platform. The second produces the maximum `unsigned int`. Start with the operand types before trying to calculate the result.

Bitwise operations also apply promotions. On a typical 32-bit-int target, `~std::uint8_t{0x0F}` has type `int`, with more than eight bits in its result. Assignment back to an eight-bit type converts the result; the expression itself was not eight-bit arithmetic.

Character arithmetic usually produces `int`. On ASCII-compatible systems, `'A' + 1` produces the integer 66; converting that result to `char` produces `'B'`. The familiar values `'A' == 65`, `'a' == 97`, and `'0' == 48` are encoding assumptions.

A `float` promotes to `double` in contexts requiring floating promotion, including default argument promotions for C-style variadic arguments. A `bool` promotes to zero or one.

## Shifts

For a built-in shift, both operands must have integral or unscoped enumeration types. Promotions happen first. The shift count must be nonnegative and smaller than the width of the promoted left operand. With 32-bit `unsigned int`, `1u << 32` has undefined behavior; `1ull << 32` uses the wider type.

In C++20 and later, left shift has the specified modulo result, and signed right shift rounds toward negative infinity. On a 32-bit `int` target, `1 << 31` therefore yields `INT_MIN` and `-1 >> 1` yields `-1`. Older language versions have different signed-shift rules. These value rules never excuse an invalid shift count. See the [draft shift rules](https://eel.is/c++draft/expr.shift).

Some x86 instructions mask a shift count. That hardware behavior does not define an out-of-range C++ shift. Use a sufficiently wide unsigned literal and validate the count. Literal suffixes include `u`, `l`, and `ll`; C++23 adds the size-related `z` suffix, so `0uz` has type `std::size_t`.

## Overload resolution

For simple standard conversion sequences, an exact match ranks above a promotion, which ranks above a conversion. A `short` therefore prefers `f(int)` over `f(long)`, and a `float` prefers `f(double)` over `f(long)`.

If `foo(int)` and `foo(unsigned)` are the candidates, `foo(-1.5)` is ambiguous: both require a conversion of the same rank. Signedness does not break that tie. Real overload resolution has additional rules, so this ranking is a starting point rather than the entire algorithm.

## Fixed-width types and sizes

The exact-width aliases in `<cstdint>`, such as `std::uint32_t`, exist only when the implementation supports the required representation. The least-width and fast-width families provide alternatives with minimum widths. Exact-width aliases are useful for wire formats and files, but byte order and serialization still need handling.

On common implementations, `std::int8_t` and `std::uint8_t` alias character types, so stream insertion treats them as characters. Cast to `int` when you want a number.

`std::size_t` is the unsigned result type of `sizeof`. `std::ptrdiff_t` is the signed type used for pointer differences; it is not necessarily the signed counterpart of `size_t`. Prefer ordinary signed arithmetic when negative intermediate values are meaningful, and handle conversions to container sizes deliberately.

## Bools and enumerations

Without `std::boolalpha`, formatted boolean input accepts zero and one normally. Another numeric value sets the result to true and sets the failure state. With `boolalpha`, input and output use textual boolean names. Check the stream state before using parsed input. Arbitrarily overwriting a bool's bytes is unsafe because not every representation need represent a valid bool.

An unscoped enum introduces its enumerators into the enclosing scope and permits integral conversions. An `enum class` keeps them scoped and requires an explicit conversion to an integer. Use `static_cast`, or `std::to_underlying` in C++23. C++20's `using enum` can introduce selected enumerator names into the current scope.

An enum with a fixed underlying type can hold values not named by any enumerator. For an unscoped enum without a fixed underlying type, the valid range follows the language's bit-field range rule; casting outside it has undefined behavior. A switch over an enum must account for the values its input can actually contain.

## Errors and pitfalls

A narrowing braced initializer and ambiguous overload require diagnostics. Signed arithmetic overflow and invalid shift counts have undefined behavior. Unsigned wrap is defined but can still be a logical bug. In particular, `unsigned i >= 0` is always true. Enable useful warnings such as `-Wsign-compare` and `-Wconversion`, and inspect the type of intermediate expressions.

## Additional syntax examples

These are independent syntax sketches, including deliberately invalid examples marked `CE` (compile error). They are not one compilable program.

```cpp
unsigned short x = 0;
unsigned short y = x - 1;   // Converts to 65535 when unsigned short is 16 bits.

unsigned short a = 0, b = 1;
if (a - b > 0)   // False when int represents every unsigned short value: 0-1 = -1.
// == (static_cast<int>(a) - static_cast<int>(b)) > 0  [compiler explorer]
// unsigned int a,b -> true (0u-1u = 4294967295)

void foo(int);      // 1
void foo(unsigned); // 2
foo(-1.5);          // CE: ambiguous, same conversion rank

uint64_t val = 0;
for (int i = 0; i < 64; i++)
    val |= (1u << i);    // With 32-bit unsigned int, counts >= 32 are invalid. Use 1ull << i.

enum class FeePriority { One = 0, Two, Three };
FeePriority p = FeePriority(3);   // legal: fits underlying int
std::cout << (int)p;              // 3 (no implicit conversion)
auto v = std::to_underlying(p);   // C++23 <utility>
using enum FeePriority;           // C++20

bool b{};
std::cin >> std::boolalpha >> b;             // accepts "true"/"false"
std::cout << std::boolalpha << b;            // prints true/false
```

## Interview Q&A

### Why can unsigned short subtraction produce a negative result?

The operands are promoted before subtraction. On a typical machine, int can represent every unsigned short value, so both operands become int. Subtracting one from zero then gives signed minus one. I would state that platform assumption because promotion depends on the available ranges.

### Is signed overflow the same as converting to a smaller signed type?

No. Signed arithmetic overflow has undefined behavior. Integer conversion follows a separate wraparound rule since C++20: for example, converting 255 to an eight-bit signed integer produces minus one. Braced initialization can reject that conversion as narrowing before the program runs.

### Why is 1u shifted by 32 invalid on a typical desktop?

The left operand is normally a 32-bit unsigned int, and the shift count must be smaller than its width. The fact that a processor masks the count does not make the C++ expression valid. I would use a wider type if that matches the intended calculation.

### How do you approach a mixed signed and unsigned expression?

I first apply integral promotions, then find the common type using rank and representable range. Only then do I calculate the value. Assuming that any unsigned operand makes the result unsigned can be wrong when a wider signed type can represent its whole range.

### Why use enum class?

It keeps enumerator names scoped and prevents implicit conversion to integers, which avoids accidental mixing. I still need to validate external values because a fixed underlying type can represent values that have no named enumerator.

## Practice history

The entries below preserve the original practice record. Use the explanations above for the current rules and qualifications.

### Questions (getcracked)

- [x] FeePriority(3) — 30/08 — ok
- [ ] Down shift — 30/08 — MISSED: said UINT32_MAX assuming 1u<<32 → 0. Shift >= width is UB; x86 masks count (often yields 1). Fix: 1ull << i.

### Quiz log (Claude)

- 30/08: 300→44 u8 wrap chain — ok. `char x = 128` → -128 defined conversion (not UB) — half (said UB). 'A'+1 mechanism ok, ASCII value off.
- 31/08: uint8+uint8 promotion → 300 — ok. Shift ladder: (b)-(e) ok, (a) `1 << 31` said 2^31, it's INT_MIN (int can't hold +2^31).
