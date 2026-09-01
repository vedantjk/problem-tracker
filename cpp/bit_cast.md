# std::bit_cast (C++20, <bit>)

## Core model
- `auto i = std::bit_cast<int>(f);` — copies the bit pattern into a NEW object of the target type. No aliasing violation by construction (it's semantically a memcpy, but constexpr-able and returns by value).
- Requirements (else CE): source and destination exactly the same size, both trivially copyable.
- Works on structs: pack `struct Color{uint8_t r,g,b,a;}` ↔ `uint32_t`; `std::array<uint8_t,12>` ↔ `struct Point{float x,y,z;}` — byte buffers to typed data without reinterpret_cast or unions.
- vs alternatives: reinterpret_cast (UB at access), union pun (UB in C++, legal in C), memcpy (defined but not constexpr, two statements). bit_cast is the modern default.

## Compile errors vs unspecified
- CE: size mismatch (`bit_cast<double>(int{1})`), non-trivially-copyable participant (std::string either side).
- Unspecified: padding bits in the result when the destination has padding; bits corresponding to source padding.
- Aliasing note: result depends on byte order — packing Color→uint32_t gives different numbers on little vs big endian; C++20 std::endian to check.

## Syntax anchors
```cpp
auto i = std::bit_cast<int>(23.45f);          // float bits as int

struct Color { uint8_t r, g, b, a; };
auto packed = std::bit_cast<uint32_t>(Color{255,128,64,255}); // endian-dependent!

struct Point { float x, y, z; };
std::array<uint8_t, 12> bytes = { /* ... */ };
auto pt = std::bit_cast<Point>(bytes);        // bytes -> struct, no UB
```

## Traps / interview one-liners
- "bit_cast = constexpr memcpy that returns a value. Same asm as the UB reinterpret_cast version, none of the UB."
- "Aliasing legality is type identity, not size: long via long long* is UB despite identical 64-bit representation; int64_t* is fine on Linux only because int64_t IS long there."
