# Bitflags and std::bitset

## Core model
- `std::bitset<N>` — N fixed at compile time. Mutators: `set(i)` (→1), `reset(i)` (→0), `flip(i)`, query `test(i)`. Whole-set: `set()`/`reset()`/`flip()` no args act on all bits.
- Queries: `size()` = N, `count()` = popcount, `all()` / `any()` / `none()`.
- Optimized for speed not space: storage rounds up to word multiples — `bitset<8>` is typically 8 bytes on 64-bit (4 on 32-bit). sizeof is implementation-defined (was a quiz Q).
- Construct from integer literal `0b0000'0101` or from a "01" string. `to_ulong()`/`to_ullong()` convert back.
- Bitwise ops on sub-int integrals promote to int/unsigned int first: `~c` on a uint8_t yields a 32-bit int with high bits set; `c << 6` doesn't lose bits into oblivion, it grows. Assigning back narrows (list-init → CE, assignment → warning).

## Compile errors vs UB vs exceptions
- CE: `std::uint8_t cneg{ ~c };` — narrowing from promoted int in list-init.
- UB: `bits[i]` with i >= N — operator[] does NOT bounds-check.
- Throws: `bits.test(i)` with i >= N → std::out_of_range (the checked twin of operator[]); `to_ulong()` when bits above position 31 are set → std::overflow_error.

## Traps / interview one-liners
- "operator[] is unchecked, test() throws — same split as vector [] vs at()."
- "count() is a popcount; for raw integers C++20 gives std::popcount/countl_zero/countr_zero in <bit>, which compile to POPCNT/LZCNT — the fast way to scan a bitmap of price levels."
- "~ on a uint8_t is a 32-bit answer: promotion happens before every bitwise op."
- "bitset<8> costs 8 bytes; vector<bool> packs but has its own proxy weirdness — neither is a memory win at small N."
