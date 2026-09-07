# Bits, bitset & Type Punning

## bitset and bit operations

`std::bitset<N>` represents N bits with a fixed compile-time size. Use set, reset, and flip to modify bits; their no-argument forms operate on the whole set. Test inspects one bit, count reports the number of set bits, and all, any, and none describe the set as a whole.

Construct a bitset from an integer or a suitable string representation. `to_ulong()` and `to_ullong()` convert back to integer types and throw `std::overflow_error` if the value does not fit. Size returns the logical bit count, not the storage size in bytes.

The representation is implementation-dependent and commonly rounds to machine-word storage. A bitset<8> may occupy eight bytes on one 64-bit library implementation; neither that size nor a compact single-byte layout is guaranteed.

```cpp
std::bitset<8> flags{0b0000'0101};
flags.set(3);                  // Bits 0, 2, and 3 are now set.
bool present = flags.test(3);  // A checked access.
```

Through C++23, operator[] requires an in-range index and violating the precondition has undefined behavior. Test performs a check and throws `std::out_of_range`. Later library hardening can change how a violated precondition is diagnosed on a hardened implementation; use the checked interface when the index is not established as valid.

C++20's `<bit>` provides functions such as `std::popcount`, `std::countl_zero`, and `std::countr_zero` for suitable unsigned integer types. A compiler can map them to instructions such as POPCNT or LZCNT when supported, or use another implementation. A bitmap of price levels is one application, but instruction selection is not a language guarantee.

## Promotions happen before bitwise arithmetic

Small integral operands undergo promotion before many bitwise operations. On a typical platform with 32-bit int, `~std::uint8_t{0x0F}` produces an int result, not an eight-bit result. A shift likewise operates on the promoted left type. Assigning back performs a separate conversion; list-initialization may reject it as narrowing.

The width of the promoted left operand also bounds a valid shift count. Use [types and conversions](types_conversions.md) to determine the type before interpreting a bit pattern.

## reinterpret_cast does not validate access

A reinterpret_cast can express a low-level conversion, but it does not check bounds, alignment, lifetime, or whether the resulting pointer can access the stored object as that type. Forming a cast and accessing through it are separate operations. Many common object-pointer casts need no runtime instruction, but “always free” is not a portable guarantee for every form of reinterpret_cast.

Type-based aliasing rules let the optimizer assume certain typed accesses do not refer to the same object. Permitted access includes the object's type or a similar type, its corresponding signed or unsigned type, and char, unsigned char, or std::byte for representation access. Accesses involving aggregate members, unions, and base subobjects require the corresponding object-model reasoning; this is not a license to reinterpret every equal-sized type. See [type accessibility](https://timsong-cpp.github.io/cppwp/n4950/basic.lval).

Type identity matters more than size. Long and long long remain different types even where both occupy eight bytes. An int64_t alias is compatible with whichever underlying type it actually names on the target.

## Alignment, lifetime, and byte buffers

Alignment is independent of aliasing. Even if a type is otherwise appropriate, accessing it through an insufficiently aligned address can violate the language rules. Use alignof and suitable storage, rather than relying on hardware that happens to tolerate an unaligned load.

A byte buffer is not automatically a live Header object merely because a pointer is cast to Header*. Some operations can implicitly create objects of implicit-lifetime types, but the applicability depends on the storage and operation. C++23's `std::start_lifetime_as` provides explicit facilities for suitable implicit-lifetime objects; it still has requirements and does not validate an arbitrary network message.

For an ITCH-style parser, check bounds, layout, byte order, alignment, lifetime, and valid field representations. Copying bytes into a suitable existing trivially copyable object can avoid typed aliasing and alignment hazards at the source. Decoding fields individually is often clearer when the wire layout differs from the host layout.

Writing through a const-stripped pointer to an originally const object has undefined behavior. Casting does not change the underlying object's constness.

## memcpy and bit_cast

Memcpy copies object representation bytes. For a suitable trivially copyable destination, it is a standard tool for moving representations without accessing the source through an unrelated typed lvalue. The copied representation must still be valid for how it will be used, and the byte count and object lifetime must be correct.

C++20's `std::bit_cast<To>(from)` produces a new value from a source representation. The types must have equal size and both be trivially copyable. Constant evaluation has further restrictions, so not every valid runtime bit_cast is a constant expression.

```cpp
static_assert(sizeof(float) == sizeof(std::uint32_t));
float f = 3.14f;
auto bits = std::bit_cast<std::uint32_t>(f);
```

This reads the float representation into an unsigned integer without making an integer lvalue alias the float. It does not numerically convert 3.14 to three. Bit_cast is not a blanket guarantee that every arbitrary input bit pattern is a valid destination value. Padding and indeterminate bits have additional rules; see the [bit_cast specification](https://timsong-cpp.github.io/cppwp/n4950/bit.cast).

A Color with four byte fields can be bit-cast to a 32-bit integer if the requirements hold, but the integer's numeric value depends on byte order. `std::endian` describes native endianness. A three-float Point and twelve-byte array also need actual size, trivial-copyability, and representation checks rather than an assumption based solely on member count.

Reading an inactive union member for type punning is not a general portable C++ technique, although specific union rules and compiler extensions exist. Prefer an appropriate memcpy or bit_cast for representation transfer. For pointer round trips, use only the guarantees of the specific conversion; a sufficiently wide integer type such as uintptr_t, when available, can support converting an object pointer to integer and back. Pointer-interconvertible standard-layout objects provide other specific cases, such as an eligible object and its first member.

## Diagnosing problems

A successful run does not prove that a cast is valid. AddressSanitizer and UndefinedBehaviorSanitizer detect useful exercised errors, but ordinary UBSan is not a complete strict-aliasing checker. Alignment sanitization and strict-aliasing warnings cover particular cases, and tool-specific type sanitizers have their own availability and limits.

Use a checklist: identify the real object and its lifetime, verify the address and alignment, establish that the access type is permitted, and check the representation and bounds. Compiler flags such as `-fno-strict-aliasing` change implementation assumptions; they do not repair independent alignment, lifetime, or bounds errors.

## Errors and pitfalls

Size mismatch or non-trivially-copyable types make bit_cast invalid. An out-of-range test throws, while an unchecked out-of-range access violates a precondition. Reinterpret_cast is neither automatically undefined behavior nor automatically permission to dereference its result. Identify the actual operation that violates a rule.

## Additional syntax examples

These are independent syntax sketches, including deliberately invalid examples marked `CE` (compile error). They are not one compilable program.

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

B* b = reinterpret_cast<B*>(&a);          // Access requires a valid B object and all other access conditions.
int* p = reinterpret_cast<int*>(&f); int value = *p; // Reading a float through int violates typed access.

float f = 3.14f; std::uint32_t i;
static_assert(sizeof(i) == sizeof(f));
std::memcpy(&i, &f, sizeof f);            // Copies the representation into an unsigned integer.

auto j = std::bit_cast<std::uint32_t>(23.45f); // Requires equal size; these are representation bits.
struct Color { uint8_t r, g, b, a; };
auto packed = std::bit_cast<uint32_t>(Color{255,128,64,255}); // endian!
struct Point { float x, y, z; };
std::array<uint8_t, 12> bytes = { /* ... */ };
auto pt = std::bit_cast<Point>(bytes);    // Requires equal size, trivial copyability, and valid representations.
```

## Interview Q&A

### Why can reinterpret_cast compile and still lead to undefined behavior?

The cast does not validate the access I perform afterward. The resulting pointer still needs a correctly aligned, live object that may be accessed through that type, with valid bounds. I check those conditions before dereferencing it.

### How is bit_cast different from reinterpret_cast?

Bit_cast produces a new value by transferring a representation between equal-sized trivially copyable types. A pointer reinterpret_cast changes the pointer type without copying an object. Bit_cast avoids the unrelated typed-alias access, but valid representation and padding rules still matter.

### Why does inverting an eight-bit integer produce more than eight bits?

The operand is promoted before the bitwise operation. On a typical machine it becomes a 32-bit int, so the inversion acts on that type. Converting back to an eight-bit type is a separate step.

### Can I cast network bytes directly to a header pointer?

Only if I can establish all the object-model and format requirements, which a cast alone does not do. I need sufficient bytes, alignment, a valid object lifetime, a permitted access type, and correct layout and endianness. Copying or decoding fields is often easier to justify.

### Why use test instead of bitset's subscript operator?

Test checks the index and throws out_of_range if it is invalid. Subscript requires the index to be valid already. I use the interface that matches whether the caller or the access operation is responsible for establishing the bound.
