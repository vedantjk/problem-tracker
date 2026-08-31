# Enumerations

## Core model
- Unscoped `enum`: enumerators leak into the enclosing scope; implicit conversion to int.
- Scoped `enum class`: own scope, no implicit conversion. To integral: `static_cast`, or C++23 `std::to_underlying` (<utility>). Int → enum: `static_cast` too.
- C++20 `using enum X;` imports enumerators into the current scope (nice inside switch).
- Out-of-enumerator values: legal for any enum with a fixed underlying type (enum class defaults to int) as long as the value fits it — `FeePriority(3)` with enumerators 0..2 prints 3. But an unscoped enum WITHOUT fixed underlying type is only valid in the smallest bit-field range covering its enumerators; casting outside that is UB.

## Questions (getcracked)
- [x] FeePriority(3) — 30/08 — ok

## Compile errors vs UB
Compile error:
- `int i = FeePriority::One;` — enum class doesn't implicitly convert.
- Comparing different enum class types: `FeePriority::One == OtherEnum::A`.

UB:
- Casting a value outside the bit-field range into an unscoped enum with NO fixed underlying type: `enum Color {R,G,B}; Color c = Color(7);` (range is 0-3). With `enum class` or `: int`, same cast is defined.

## Traps / interview one-liners
- "enum class = scoped + no implicit int conversion + fixed underlying type. Specify `: uint8_t` for wire formats."
- "Enum can legally hold non-enumerator values — switch defaults must handle them."
