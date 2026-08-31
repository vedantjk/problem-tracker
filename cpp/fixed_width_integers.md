# Fixed Width Integers

## Core model
- `<cstdint>`, C++11: `int8_t`...`uint64_t`, exact size + two's complement guaranteed. Not guaranteed to exist on exotic hardware (compile error there); everywhere real, they exist.
- `int8_t`/`uint8_t` are typically aliases for signed/unsigned char (spec oversight) → `cout << int8_t{65}` prints 'A'. Cast to int for numeric output.
- May be slower than the native width on some CPUs; but memory footprint often dominates ("measure, don't assume").
- `int_fast#_t` = fastest type with >= # bits; `int_least#_t` = smallest with >= # bits. Guaranteed to exist. Rarely used in practice.
- `std::size_t`: implementation-defined unsigned type, result of sizeof, 8 bytes on x86-64. No type's object representation may exceed size_t's max. Signed sibling: `ptrdiff_t`.

## Questions (getcracked)
- (tbd)

## Compile errors vs surprises
Compile error:
- Using `std::int32_t` on a platform without an exact-width 32-bit type — the alias simply doesn't exist there (exotic hardware only).

Surprises (defined):
- `std::uint8_t x = 65; std::cout << x;` prints 'A' — it's a char alias.
- `size_t` arithmetic never goes negative — loop-underflow infinite loops.
(For overflow rules see signed_unsigned.md — same rules apply, these are just aliases.)

## Traps / interview one-liners
- "Fixed-width for wire formats, files, and hardware registers — my ITCH parser is uint16_t/uint32_t because the spec says so. Local arithmetic: int. Indexing/sizes: size_t."
- "`uint8_t` streams as a char, not a number."
- "size_t is unsigned: `for (size_t i = n-1; i >= 0; --i)` loops forever."
