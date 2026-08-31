# reinterpret_cast and std::memcpy

## Core model
- `reinterpret_cast<T*>(p)` reinterprets the pointer's bits as another pointer type (also pointer↔integer via uintptr_t). Zero runtime cost, zero checks — and the cast itself is fine; **the UB happens at the ACCESS**, governed by:
- **Strict aliasing rule**: an object may only be accessed through (a) its own type / cv-variants, (b) a signed/unsigned sibling of its type, or (c) `char*`, `unsigned char*`, `std::byte*`. Anything else — `*reinterpret_cast<int*>(&some_float)`, A* → B* between unrelated classes — is UB, and the optimizer exploits it (it assumes an int write can't change a float, reorders accordingly).
- Alignment is a second, independent hazard: casting a misaligned `char*` to `uint32_t*` and dereferencing is UB even where aliasing would allow it. `alignas`/`alignof` to control it.
- The blessed type pun: `std::memcpy(&i, &f, sizeof f);` — compiles to the same single register move, no UB. C++20: `std::bit_cast<int>(f)` — constexpr-able, sizes must match exactly. These are THE answers to "how do I look at a float's bits".
- Casting away const-ness of a truly-const object and writing → UB regardless of which cast did it.

## Compile errors vs UB
- CE: `std::bit_cast` between different-sized types; reinterpret_cast between unrelated non-pointer types (e.g. float → int directly — that's static_cast's job, a value conversion, different thing entirely).
- UB: dereference after aliasing-violating cast; misaligned dereference; writing through a const-stripped pointer to a const object.
- Legal: round-trip T* → void*/uintptr_t → T*; T* → char* for byte inspection; pointer to first member ↔ standard-layout struct.

## Traps / interview one-liners
- "reinterpret_cast is free at runtime; what it buys you is UB at the access, per strict aliasing. char/unsigned char/std::byte are the only universal aliases."
- "Parsing a network buffer as `reinterpret_cast<const Header*>(buf)` is the idiom everyone writes and it's technically UB (aliasing + lifetime); memcpy into a struct optimizes to the identical code and is defined. C++23 adds std::start_lifetime_as to bless the direct read." (my ITCH parser: this exact question)
- "float↔int bits: memcpy or bit_cast, never *reinterpret_cast<int*>(&f). Same asm, one is UB."
- "-fno-strict-aliasing exists (Linux kernel uses it) — it's an admission, not a fix."
