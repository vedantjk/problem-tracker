# Bits, bitset & Type Punning

## std::bitset
- `bitset<N>`: `set(i)/reset(i)/flip(i)/test(i)`; no-arg set/reset/flip act on all. `size() count() all() any() none()`. Construct from `0b0000'0101` or "01" string; `to_ulong()/to_ullong()` back.
- Speed not space: storage rounds to word multiples — `bitset<8>` = 8B on 64-bit (4B on 32-bit); sizeof implementation-defined (quiz Q).
- `bits[i]` UNCHECKED (UB out of range) vs `test(i)` throws out_of_range — the vector []/at() split. `to_ulong()` throws overflow_error if high bits set.
- C++20 <bit>: `std::popcount, countl_zero, countr_zero` → POPCNT/LZCNT (scan a bitmap of price levels).

## Bitwise + promotion
- Sub-int operands promote to int first: `~uint8_t` → 32-bit answer with high bits; `c << 6` grows. Assign back: list-init CE, assignment warns.

## Strict aliasing & reinterpret_cast
- `reinterpret_cast<T*>(p)`: free at runtime, zero checks; UB happens at the ACCESS. Legal access types for an object: own type/cv, signed/unsigned sibling, `char*`/`unsigned char*`/`std::byte*`. Everything else UB — optimizer assumes int writes can't touch floats.
- Type IDENTITY, not size: `long` via `long long*` UB despite identical 64 bits; `int64_t*` fine on Linux only because int64_t IS long there (Windows: long long — portability trap).
- Alignment is an independent hazard: misaligned `uint32_t*` deref UB even where aliasing is fine. `alignas/alignof`.
- Legal patterns: cast-and-cast-back (T*→void*/uintptr_t→T*, access via original); byte reads via char*; standard-layout struct ↔ first member.
- Audit method: UB is a contract property, not a runtime testable one. "Works" proves nothing; UBSan does NOT catch aliasing (only -fsanitize=alignment); -Wstrict-aliasing=2 catches blatant cases; TySan is new/slow. Heuristic: if memcpy could express it, write memcpy — same asm.
- Network buffers: `reinterpret_cast<const Header*>(buf)` = the idiom everyone writes, technically UB (aliasing+lifetime); memcpy per struct optimizes identically; C++23 `std::start_lifetime_as` blesses it. (My ITCH parser: expect this question.)
- Writing through const-stripped pointer to truly-const object: UB whatever cast produced it.

## std::bit_cast (C++20, <bit>)
- Copies bits into a NEW object: constexpr memcpy returning by value. No aliasing issue by construction.
- Requirements (else CE): exact same size, both trivially copyable.
- Struct-capable: Color{4×uint8_t} ↔ uint32_t (endian-dependent number! std::endian to check); std::array<uint8_t,12> ↔ Point{3×float}.
- vs union pun (UB in C++, legal C), memcpy (defined, not constexpr), reinterpret (UB).
- Unspecified: padding bits in the result.

## Compile errors vs UB vs throws
- CE: `bit_cast` size mismatch or non-trivially-copyable; `uint8_t cneg{~c}` narrowing; reinterpret_cast between non-pointer unrelated types (float→int value conversion = static_cast's job).
- UB: `bits[N]`; aliasing-violating deref; misaligned deref; const-stripped write.
- Throws: `test(N)` out_of_range; `to_ulong()` overflow_error.

## Syntax anchors
```cpp
std::bitset<8> bits{ 0b0000'0101 };
bits.set(3);    // 0000 1101
bits.flip(4);   // 0001 1101
bits.reset(4);  // 0000 1101
bits.test(3);   // 1 (throws if idx >= N; bits[i] doesn't check -> UB)
bits.size(); bits.count(); bits.all(); bits.any(); bits.none();

std::uint8_t c{ 0b00001111 };
std::bitset<32>(~c);      // 1111...11110000 (promoted first)
std::bitset<32>(c << 6);  // grew into the int, nothing lost
std::uint8_t cneg{ ~c };  // CE: narrowing
c = ~c;                   // warning only

B* b = reinterpret_cast<B*>(&a);          // unrelated cast: UB at b->y
int* p = reinterpret_cast<int*>(&f); *p;  // float pun: aliasing UB

float f = 3.14f; int i;
std::memcpy(&i, &f, sizeof f);            // blessed pun, same asm

auto j  = std::bit_cast<int>(23.45f);     // float bits as int
struct Color { uint8_t r, g, b, a; };
auto packed = std::bit_cast<uint32_t>(Color{255,128,64,255}); // endian!
struct Point { float x, y, z; };
std::array<uint8_t, 12> bytes = { /* ... */ };
auto pt = std::bit_cast<Point>(bytes);    // bytes -> struct, no UB
```

## Traps / interview one-liners
- "reinterpret_cast is free; what it buys is UB at the access. char/uchar/std::byte are the only universal aliases."
- "float↔int bits: memcpy or bit_cast, never *reinterpret_cast<int*>(&f)."
- "-fno-strict-aliasing (Linux kernel) is an admission, not a fix."
- "operator[] unchecked, test() throws."
- "~ on uint8_t is a 32-bit answer."
