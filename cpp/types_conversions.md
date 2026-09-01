# Integral Types, Promotions & Conversions

## Signed vs unsigned
- Signed ARITHMETIC overflow: UB (`INT_MAX+1`, `-INT_MIN`, `INT_MIN/-1`). Optimizer assumes it can't happen (that's why loops vectorize).
- Unsigned arithmetic: defined modular wrap, value mod 2^N. 280 in u8 → 24; `0u - 1` → max.
- CONVERSION (stuffing too-big value into narrower type): unsigned always wrapped; signed was implementation-defined pre-C++20, defined wrap since (two's complement mandated). `char x = 300` → wrap; `char x{300}` → CE (narrowing). Float→integral out of range: still UB.
- C++26 direction: uninitialized reads become "erroneous behavior"; UB stays where optimizers profit (signed overflow, shifts, bounds).

## Promotion, then conversion (the two-step rule)
1. **Integral promotion**: anything narrower than int (bool, char, short — signed AND unsigned) → **signed int** (unsigned int only if int can't hold the range: never on real platforms). float → double is the floating promotion (varargs!). bool → int (0/1). Promotions are value-preserving, exist for register width.
2. **Usual arithmetic conversions**: one side unsigned with rank >= int → signed side converts to unsigned.
- Consequence: `unsigned short a=0,b=1; a-b > 0` **false** (int math, -1); with `unsigned int`: **true** (4294967295). Width relative to int flips it.
- Bitwise ops promote too: `~uint8_t{0x0F}` is a 32-bit int answer; `c << 6` grows, doesn't truncate.
- `char` +: `'A'+1` is int 66 → `cout` prints number; assign back to char → prints 'B'. Anchors: 'A'=65, 'a'=97 (bit 0x20 apart), '0'=48.

## Shifts (the full contract)
- Count must be in [0, width of promoted left operand) — else UB, signedness irrelevant: `1u << 32` UB, `1ull << 32` fine, `i << -1` UB.
- Value rules (C++20, two's complement): `1 << 31` = INT_MIN (was UB pre-C++14); `-1 << 1` defined wrap (UB pre-C++20); `-1 >> 1` = -1 arithmetic shift (impl-defined pre-C++20).
- `i << 0.2` — CE: integral operands only.
- x86 `shl` masks count to 5 bits → `1u<<32` often EXECUTES as 1, not 0. UB ≠ polite zero.

## Overload resolution ranks
- exact > promotion > conversion; tie at same rank across candidates = CE.
- `foo(int)` vs `foo(unsigned)` with `foo(-1.5)`: ambiguous CE (double→int and double→unsigned same rank; signedness never breaks ties).
- Promotion beats conversion: short arg picks `f(int)` over `f(long)`; float arg picks `f(double)` over `f(long)`.

## Fixed-width integers (<cstdint>)
- `int8_t..uint64_t`: exact width + two's complement; may not exist on exotic hardware (CE there).
- `int8_t/uint8_t` alias char types → `cout << uint8_t{65}` prints 'A'. Cast to int to print.
- `int_fast#_t` / `int_least#_t`: guaranteed to exist; rarely used.
- `size_t`: unsigned, result of sizeof, 8B on x86-64; signed sibling `ptrdiff_t`. No object bigger than size_t max.
- Use: fixed-width for wire/file/registers (ITCH parser: uint16_t/uint32_t per spec); int for arithmetic; size_t for sizes.

## Bools
- `std::boolalpha`: print/parse true/false (case-sensitive). Default cin: 0/1 only; other numeric → true + failure state; non-numeric → false + failure state (cin.clear() to recover).
- UB: reading a bool whose byte holds 2 (memcpy'd) — compiler assumes 0/1.

## Enumerations
- Unscoped enum: leaks enumerators, implicit → int. Scoped `enum class`: own scope, no implicit conversions; `static_cast` or C++23 `std::to_underlying` (<utility>); C++20 `using enum X;` imports.
- Out-of-enumerator values: fine when underlying type is fixed (enum class defaults int) and value fits — `FeePriority(3)` on 0..2 prints 3. Unscoped WITHOUT fixed type: valid range = smallest bit-field covering enumerators; outside → UB (`enum Color{R,G,B}; Color(7)`).
- Specify `: uint8_t` for wire formats. Switch defaults must handle non-enumerator values.

## Questions (getcracked)
- [x] FeePriority(3) — 30/08 — ok
- [ ] Down shift — 30/08 — MISSED: said UINT32_MAX assuming 1u<<32 → 0. Shift >= width is UB; x86 masks count (often yields 1). Fix: 1ull << i.

## Quiz log (Claude)
- 30/08: 300→44 u8 wrap chain — ok. `char x = 128` → -128 defined conversion (not UB) — half (said UB). 'A'+1 mechanism ok, ASCII value off.
- 31/08: uint8+uint8 promotion → 300 — ok. Shift ladder: (b)-(e) ok, (a) `1 << 31` said 2^31, it's INT_MIN (int can't hold +2^31).

## Syntax anchors
```cpp
unsigned short x = 0;
unsigned short y = x - 1;   // wraps on ASSIGNMENT back: 65535

unsigned short a = 0, b = 1;
if (a - b > 0)   // false! promoted to int: 0-1 = -1
// == (static_cast<int>(a) - static_cast<int>(b)) > 0  [compiler explorer]
// unsigned int a,b -> true (0u-1u = 4294967295)

void foo(int);      // 1
void foo(unsigned); // 2
foo(-1.5);          // CE: ambiguous, same conversion rank

uint64_t val = 0;
for (int i = 0; i < 64; i++)
    val |= (1u << i);    // UB at i=32. Fix: 1ull << i

enum class FeePriority { One = 0, Two, Three };
FeePriority p = FeePriority(3);   // legal: fits underlying int
std::cout << (int)p;              // 3 (no implicit conversion)
auto v = std::to_underlying(p);   // C++23 <utility>
using enum FeePriority;           // C++20

bool b{};
std::cin >> std::boolalpha >> b;             // accepts "true"/"false"
std::cout << std::boolalpha << b;            // prints true/false
```

## Traps / interview one-liners
- "Signed overflow UB / unsigned wrap defined — but unsigned is more dangerous by default: `v.size()-1` on empty = 2^64-1, silently."
- "Sub-int unsigned types promote to SIGNED int before arithmetic."
- "`for (unsigned i = n; i >= 0; --i)` never terminates."
- "Arithmetic overflow vs conversion: `INT_MAX+1` UB forever; `char x = 300` defined wrap since C++20."
- "Shift checklist: (1) count < width or UB, no exceptions; (2) value rules all defined since C++20."
- "`uint8_t` streams as a char, not a number."
- "1u = unsigned int literal; suffixes u/l/ll combine (1ull); no short/char literals; C++23 uz = size_t."
- "-Wsign-compare/-Wconversion; prefer signed for arithmetic, unsigned for bit patterns."
