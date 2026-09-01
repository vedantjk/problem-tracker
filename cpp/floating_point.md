# Floating Point Types

## Core model
- float (4B, IEEE single), double (8B, IEEE double), long double (8/12/16B; x87 80-bit on Linux). Literals are double by default; `f` suffix for float.
- IEEE single layout: 1 sign + 8 exponent (bias 127) + 23 significand bits with an implicit leading 1 (normals only). Worked 123.456: fraction .456 → 0111010010111100011..., normalize 1.f × 2^6, exponent 133 = 10000101, round significand to 23 bits.
- Default rounding: round-to-nearest-EVEN (ties go to the even bit, not always up).
- Reserved exponents: all-0 → ±0 and subnormals (no hidden 1, gradual underflow); all-1 → ±Inf (frac 0) / NaN (frac ≠ 0).
- Precision: float ~7 sig decimal digits (24-bit significand), double ~16 (53-bit). float can't represent all int32; double can.
- cout defaults: precision 6, drops ".0"; std::setprecision to change.
- Range: float ~±3.4e38, double ~±1.8e308.

## Questions (getcracked)
- [ ] A very small value — 30/08 — MISSED: answered denorm_min; condition "x + 1.0 > 1.0" defines epsilon(). Smallest-positive (denorm_min 4.9e-324) vs smallest-that-moves-1.0 (epsilon 2.2e-16) — read the condition, not the headline. (Platform's own explanation conflates them too; epsilon is the gap at 1.0, denorm_min is the smallest positive double.)

## UB vs implementation-defined vs defined-but-surprising
UB:
- Out-of-range float→integral conversion at runtime: `double d=1e20; int x = d;` — NOT a wrap like integral→integral; genuinely UB.

Implementation-defined:
- `sizeof(long double)` (8/12/16); whether `char` in the exponent examples is signed.

Defined but surprising:
- `0.1 + 0.2 != 0.3`; `nan != nan` (true); `+0.0 == -0.0` (true) yet `1/+0.0 != 1/-0.0`; float loses integers above 2^24.
- `-ffast-math` trades all the IEEE guarantees away — NaN checks may be deleted.

## Syntax anchors
```cpp
// IEEE-754 single: 1 sign | 8 exp (bias 127) | 23 frac (+hidden 1)
// 123.456f:
//   123      = 1111011b
//   .456     = 0111010010111100011...b
//   normalize 1.1110110111010010111100011 x 2^6
//   exponent 127+6 = 133 = 10000101b
//   frac: drop hidden 1, keep 23, round-to-nearest-even

std::numeric_limits<double>::min();        // 2.2e-308  smallest NORMAL
std::numeric_limits<double>::denorm_min(); // 4.9e-324  smallest positive
std::numeric_limits<double>::epsilon();    // 2.2e-16   gap at 1.0 (x+1.0 > 1.0)
std::numeric_limits<double>::lowest();     // -1.8e308  most negative
```

## Traps / interview one-liners
- "0.1 is infinite in binary → 0.1+0.2 != 0.3; compare with epsilon relative to magnitude, never ==."
- "min() = smallest normal (2.2e-308), denorm_min() = smallest positive (4.9e-324), epsilon() = gap at 1.0 (2.2e-16), lowest() = most negative. Integer min() is most-negative — the inconsistency lowest() fixes."
- "NaN != NaN — the only self-unequal value; use std::isnan."
- "Float loses integers above 2^24 — why finance uses fixed-point ints, not float, for prices (my Slipstream/lob use ×10^4 ticks)."
- "Signed zero exists: +0.0 == -0.0 but 1/+0.0 = +Inf, 1/-0.0 = -Inf."
