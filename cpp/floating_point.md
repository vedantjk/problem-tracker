# Floating Point Types

## Representation and precision

Floating point represents a number using a sign, a significand, and an exponent, much like scientific notation. For example, `6.5` in decimal is `110.1` in binary, which can be written as `1.101 × 2²`. Here the significand is the binary number `1.101`, which carries the significant digits, and the exponent is 2, which sets the power of two that multiplies it. The exponent provides a large range, while the finite number of significand bits limits precision. Many decimal fractions, including 0.1, have an infinite binary expansion and must be rounded.

On common IEEE-754 systems, `float` is binary32 and occupies four bytes, while `double` is binary64 and occupies eight. Binary32 has one sign bit, eight exponent bits, and 23 stored fraction bits. Its exponent uses a bias of 127: the stored exponent is the actual exponent plus 127. For `6.5`, the actual exponent is 2, so the stored exponent is 129. This offset allows the exponent field to represent both negative and positive exponents, with special field values reserved for the cases discussed below.

A normal value uses a binary significand written with one nonzero digit before the point, as in `1.101`. That first digit must be one, so the format does not store it. This implicit leading one plus the 23 stored fraction bits gives 24 bits of significand precision. Binary64 has 53 bits of precision. These correspond roughly to seven and sixteen significant decimal digits.

C++ does not require these exact formats. `long double` is particularly platform-dependent: it may match `double`, use an 80-bit value stored in a larger slot, or use another format. Check `std::numeric_limits<T>` and the target's documentation before relying on a layout.

Floating literals such as `1.0` have type `double`; `1.0f` has type `float`. On an IEEE binary32 target, all integers through 2^24 are exactly representable, but not every larger integer is. Binary64 can exactly represent every 32-bit integer.

## Encoding a value

For a normal IEEE binary32 value, first express the magnitude in binary, then normalize it as `1.fraction * 2^exponent`. Store the exponent with its bias, omit the implicit leading one, and round the remaining fraction to the available bits. For 123.456, the normalized exponent is six, so the stored exponent is 133.

The usual default rounding mode is round to nearest, with ties going to the representable result whose least significant significand bit is even. Rounding can occur after each operation, so algebraically equivalent expressions can produce different floating-point results.

## Zeros, subnormals, infinity, and NaN

In IEEE formats, an all-zero exponent encodes zero or a subnormal value. Subnormals do not have the implicit leading one and provide gradual underflow with decreasing precision near zero. An all-one exponent encodes infinity when the fraction is zero, or a NaN when it is nonzero.

Positive and negative zero compare equal, but their signs can affect later operations. Under IEEE division semantics, dividing positive one by them produces positive or negative infinity. A NaN compares unequal to every value, including itself; use `std::isnan` to test for it.

Compiler options such as `-ffast-math` permit assumptions that can change behavior involving NaNs, infinities, signed zero, and reassociation. Treat those options as changes to the numerical contract, rather than a universally safe speed improvement.

## numeric_limits: range is different from spacing

For a typical IEEE `double`, the following functions answer different questions:

| Function | Meaning | Approximate value |
|---|---|---|
| `min()` | This is the smallest positive normal value. | 2.2 × 10^-308 |
| `denorm_min()` | This is the smallest positive subnormal when subnormals are supported. | 4.9 × 10^-324 |
| `epsilon()` | This is the gap from one to the next representable value above one. | 2.2 × 10^-16 |
| `lowest()` | This is the most negative finite value. | -1.8 × 10^308 |

For integer types, `min()` instead gives the most negative representable value. `lowest()` provides a consistent name for the lower finite bound.

Do not define epsilon as the smallest representable `x` for which rounded `1.0 + x > 1.0`. Under round-to-nearest, values just above half an epsilon can already round the sum upward. Epsilon describes representable spacing at one, not that addition threshold.

## Comparisons and practical choices

Exact equality is appropriate when exact equality is the intended condition, such as comparing values assigned from the same representable constant. For approximate numerical results, choose a tolerance based on the problem's error budget. A common approach combines an absolute tolerance near zero with a relative tolerance at larger magnitudes. Machine epsilon alone is not a universal application tolerance.

```cpp
// For finite inputs, with tolerances chosen for the application:
bool close(double a, double b, double abs_tol, double rel_tol)
{
    return std::abs(a - b) <=
           std::max(abs_tol, rel_tol * std::max(std::abs(a), std::abs(b)));
}
```

For prices that must follow a specified decimal scale, fixed-point integers can preserve that representation exactly. The Slipstream/lob notes use a scale of 10^4; the correct scale depends on the venue or format. Representation scale and permitted tick size are separate concepts. Fixed point still needs overflow and rounding rules.

Stream output normally starts with precision six and can hide stored precision. Use `std::setprecision` deliberately; `max_digits10` is useful when a decimal representation must round-trip to the same floating value.

## Errors and pitfalls

Converting a floating value to an integer truncates its fractional part. If the truncated result cannot be represented by the destination type, the conversion has undefined behavior. It does not use the wrap rule for integer-to-integer conversions. Validate range before converting values from external or numerical input.

## Additional syntax examples

These are independent syntax sketches, including deliberately invalid examples marked `CE` (compile error). They are not one compilable program.

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
std::numeric_limits<double>::epsilon();    // 2.2e-16   gap from 1.0 to the next representable value
std::numeric_limits<double>::lowest();     // -1.8e308  most negative
```

## Interview Q&A

### Why does 0.1 plus 0.2 often differ from 0.3?

Those decimal fractions cannot all be represented exactly in binary floating point. Their stored values and the addition result are rounded, so the result can differ from the stored representation of 0.3. For approximate calculations I choose a tolerance based on the required numerical accuracy.

### What is machine epsilon?

It is the gap between one and the next representable value above one. It describes precision near one, not the smallest positive floating-point value. The spacing changes with magnitude, which is why using epsilon as a fixed tolerance everywhere is usually inappropriate.

### How are min, denorm_min, and lowest different?

For a floating type, min gives the smallest positive normal value. Denorm_min reaches further toward zero when subnormals are supported. Lowest gives the most negative finite value. They describe range, while epsilon describes spacing near one.

### Would you always avoid equality for floating-point values?

No. Equality is useful when exact equality is what the program needs. When I compare independently calculated approximations, I use an error tolerance appropriate to the calculation, usually accounting for both magnitude and behavior near zero.

### Why might you store prices as integers?

If the format specifies a decimal scale, I can store the scaled integer exactly and avoid binary rounding of the price representation. I still need to choose the scale from the format, check overflow, and define how calculations round.

## Practice history

The entries below preserve the original practice record. Correction to the old quiz shorthand: epsilon is the spacing above one, not the smallest representable x that makes rounded 1.0 + x exceed one. Under round-to-nearest, values just above half epsilon can do that. Numerical constants here assume IEEE binary64.

### Questions (getcracked)

- [ ] A very small value — 30/08 — MISSED: answered denorm_min; condition "x + 1.0 > 1.0" defines epsilon(). Smallest-positive (denorm_min 4.9e-324) vs smallest-that-moves-1.0 (epsilon 2.2e-16) — read the condition, not the headline. (Platform's own explanation conflates them too; epsilon is the gap at 1.0, denorm_min is the smallest positive double.)

### Quiz log (Claude)

- 30/08: exchange price representation (×10^4 ITCH, venue-dependent scales, tick size ≠ representation) — ok.
- 31/08: numeric_limits quartet — 4/4, prior miss reversed.
