# Signed versus Unsigned Integers

## Core model
- Signed overflow: UB, full stop ("result not representable → behavior undefined"). Optimizer assumes it can't happen.
- Unsigned overflow: well-defined modular arithmetic, value mod 2^N ("divide by one-past-max, keep remainder"). 280 in a u8 → 24; `0u - 1` wraps to max.
- Mixed signed/unsigned arithmetic, two-step rule:
  1. Integral promotion first: anything narrower than `int` (char, short, unsigned short) becomes `int`.
  2. Then usual arithmetic conversions: if one side is unsigned with rank >= int, the signed side converts to unsigned.
- Consequence: `unsigned short a=0,b=1; a-b > 0` is **false** (promoted to int, -1). Same code with `unsigned int` is **true** (0u-1u = 4294967295). Width relative to int flips the answer.

## Overload-resolution corollary
- `foo(int)` vs `foo(unsigned)` called with `foo(-1.5)`: compile error, ambiguous. double→int and double→unsigned are both "floating-integral conversions" with identical rank; resolution never prefers signed over unsigned (or vice versa) within the same rank. Fix: cast at the call site or add a `foo(double)` overload.
- Same-rank ambiguity is the general rule: overload resolution compares conversion *ranks* (exact > promotion > conversion), and ties across candidates are ill-formed.

## Questions (getcracked)
- (tbd)

## Compile errors vs UB vs defined-but-treacherous
Compile error:
- `foo(-1.5)` with foo(int)/foo(unsigned) overloads — ambiguous, same conversion rank (see above).

UB:
- Signed arithmetic overflow: `INT_MAX + 1`, `-INT_MIN`, `INT_MIN / -1`.
- Shifts: `x << 32` on 32-bit int (shift >= width); `-1 << 1` was UB pre-C++20.

Defined but treacherous:
- `0u - 1` → 4294967295; `v.size() - 1` on empty vector; `unsigned short a=0,b=1; a-b > 0` false but true for unsigned int (promotion flip).

## Traps / interview one-liners
- "Signed overflow UB / unsigned wrap defined — but unsigned is the more dangerous default because wrap is silent: `v.size() - 1` on an empty vector is 2^64-1."
- "Sub-int unsigned types don't behave unsigned in arithmetic: they promote to int first."
- "`for (unsigned i = n; i >= 0; --i)` never terminates."
- "-Wsign-compare / -Wconversion catch most of this; prefer signed (`int`/`ssize`) for arithmetic, unsigned for bit patterns."
