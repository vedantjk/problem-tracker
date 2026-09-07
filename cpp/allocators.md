# Allocators

## What "bump allocator" actually means

A bump allocator, also called an arena or linear allocator, owns one fixed buffer and a single cursor. Allocating means checking that the request fits in the space after the cursor, handing back the address at the cursor, and moving the cursor forward by the requested size plus any alignment padding. That is the whole design, and it is why bump allocation is the fastest allocation there is: a compare and an add, with no locks, no bookkeeping, and no per-allocation metadata.

The defining property is that there is no per-pointer free. The allocator writes nothing down about individual allocations, so it could not find them again even if it wanted to. The only release operation is a reset, which moves the cursor back to zero and invalidates everything at once. This works when every allocation shares one lifetime: everything created during one frame, one request, one compiler pass, or one parse of a message. When the unit of work ends, the arena is reset. If the program needs to free objects individually, a bump allocator is the wrong tool.

If an interviewer asks for a bump allocator, the answer has a buffer, a cursor, an allocate that aligns and bumps, a reset, and possibly a remaining-bytes query. It has no headers and no deallocate that takes a pointer. Reaching for headers and magic numbers in that situation is answering a different question.

## The three designs, by what "free" means

The clean way to place any allocator problem is to ask what freeing means in it.

A **bump or arena allocator** has no per-pointer free. Reset is the only release. It needs no metadata beyond the cursor.

A **stack allocator** adds one rule: a pointer can be freed only if it is the most recent allocation still live. Freeing the top pops the cursor back to where that allocation began. Freeing anything else either is an error or marks the block dead without reclaiming it. This still needs no metadata beyond the cursor if the caller supplies the size, or a small header if it does not.

A **general-purpose allocator**, whether first-fit, best-fit, or a segregated free list, allows freeing any block at any time. That requires per-block metadata so freed holes can be found and reused later, and it pays for that in header bytes, fragmentation, and search time. This is what `malloc` and `new` are.

The getcracked "Bump Memory Allocator" problem is a mislabeled member of the second family with the scaffolding of the third. It calls itself bump, but it hands you a `Deallocate(std::byte*)` to implement and a 16-byte `ChunkHeader` with a size and a magic tag. Headers only pay for themselves when the allocator intends to find and reuse holes, which is a first-fit design. In a true bump allocator the header would be pure waste, 16 bytes on a 3-byte request. The problem is still worth doing because it exercises placement new, alignment arithmetic, ownership inside a size budget, and pointer validation, but the label is wrong and it is worth saying so out loud before writing anything.

## Alignment: align the returned address, not the size

Alignment is a property of the address the caller receives. A request for 32-byte alignment means the returned pointer must be a multiple of 32. Rounding the *size* up to a multiple of 32 does not achieve that; it only makes chunk lengths multiples of 32, which is a different and mostly useless property. The reference solution to the getcracked problem makes exactly this mistake and hands back an address at offset 16 for a 64-byte-aligned request.

When each allocation carries a header before the payload, decide the payload address first and derive the header from it. Compute the earliest address that leaves room for a header after the cursor, round that address up to the alignment, and place the header immediately before it. If the alignment used is never smaller than the header's own alignment, the header lands correctly aligned for free, because any multiple of 8, 16, 32, or 64 is a multiple of 8, and subtracting 16 from a multiple of 8 keeps it a multiple of 8.

The rounding itself has a sentence worth memorizing instead of a formula: to round up to a multiple of `a`, add `a - 1` and then round down. Rounding down is integer division followed by multiplication, so the readable form is `((x + a - 1) / a) * a`. For a power of two, rounding down is clearing the low bits, which gives the bit form `(x + a - 1) & ~(a - 1)`. Rounding 19 up to a multiple of 8 gives 24, and rounding 24 gives 24, which is the property adding `a - 1` rather than `a` provides.

The standard library also provides this as `std::align` in `<memory>`. It takes the alignment, the size, a `void*` reference, and a space reference. It moves the pointer forward to the next aligned address if the size still fits, shrinks `space` by the padding it skipped, and returns the aligned pointer, or `nullptr` if the request cannot fit. It does not subtract the size; that remains the caller's job. Using `std::align` removes both the rounding formula and the fit check from the code.

When the buffer is a member array, give the array itself an alignment, for example `alignas(std::max_align_t) std::byte buf_[Capacity]`. A plain `std::byte` array has alignment one, so wherever the allocator object lands, its first byte may sit at an odd address and even the first allocation would need padding. Aligning the array makes offset zero a valid start for any default-aligned request. Note also that `std::align` subtracts only the padding from the space it is given, never the size, so after the call the cursor becomes the aligned offset plus the size, which can be written as `Capacity - remaining + size` when `remaining` is the space variable that was passed in.

Padding lost to alignment is internal fragmentation. It is bounded by `align - 1` bytes per allocation and is the accepted price of constant-time allocation with no bookkeeping. A bump allocator never looks back at the gap, because looking back would require the metadata it deliberately does not keep.

## Constructing objects in raw storage

Storage for an allocator is best typed as `std::byte`, the C++17 type from `<cstddef>` that means "raw memory, not a number and not a character." It is one byte in size, supports only bitwise operators and explicit conversion through `std::to_integer`, and shares the aliasing exemption of `char` and `unsigned char`, so a `std::byte*` may inspect the bytes of any object. Pointer arithmetic on `std::byte*` moves one byte per step, which makes it the natural cursor type.

Placing an object into raw storage is a job for placement new: `new (address) T{ args }` constructs a `T` at the given address without allocating anything. Ordinary `new` does two jobs, acquire storage and construct; placement new does only the second, because the storage already exists. It lives in `<new>`. Nothing is deleted afterwards, because nothing was allocated; if the type had a non-trivial destructor it would be invoked by hand as `p->~T()`. This is exactly what `std::vector` does when it constructs an element inside its reserved block.

Finding the object again later is a job for a cast. `reinterpret_cast<T*>(address)` says "read the bytes here as a `T`," which is legitimate precisely because placement new put a `T` there. The cast creates nothing and touches no memory. The two operations divide the work: placement new on the way in, `reinterpret_cast` on the way out. A C-style cast would compile but hides which conversion is happening, and `static_cast` refuses because `std::byte*` and `T*` are unrelated types. Going through `void*` with `static_cast` is the other standards-blessed spelling. Copying the header out with `std::memcpy` into a local, inspecting it, and copying it back avoids forming a typed pointer into the buffer at all, which sidesteps any aliasing question at the cost of more ceremony; for a trivially copyable header either approach is fine, and most allocator code uses the cast.

## Ownership inside a size budget

An allocator that owns its buffer needs exactly three words of state: the base pointer, the capacity, and the cursor. That is 24 bytes on a 64-bit target. The clean spelling of ownership is `std::unique_ptr<std::byte[]>`, which is the size of a raw pointer and calls `delete[]` automatically, so there is no hand-written destructor to forget. A constructor that receives already-allocated memory simply adopts the pointer into the same `unique_ptr`.

The trap in a 24-byte budget is an ownership flag. A `bool owns_memory` pads the class to 32 bytes. When the specification says the class is the sole owner in every construction path, the flag is unnecessary and the destructor can always release. A `static_assert(sizeof(Allocator) == 24)` under the class turns the budget into something the compiler enforces.

## Validating a pointer on free

When a free function must reject pointers it does not manage, the cheap tier of checks is a null check, a range check, an alignment check, and a magic tag in the header. Converting both pointers to `std::uintptr_t` before comparing makes the range check plain integer arithmetic; comparing raw pointers from different arrays with `<` is unspecified. Check `address < begin` before computing `address - begin` so the unsigned subtraction cannot wrap.

The magic value is a constant shared by every header. It is not a per-chunk identity; it is a tag meaning "written by the allocator and currently live," the same idea as a stack canary or the magic bytes at the front of an ELF file. Zeroing it on free makes a second free fail the check, so one constant serves as a double-free detector. A pointer into the middle of a live chunk whose user data happens to contain the magic value is the gap this tier cannot close. Adding a sanity check that the header's recorded size does not extend past the cursor tightens it further at no cost.

Exact validation requires metadata. A bitmap of chunk starts carved from the top of the buffer, one bit per 8-byte granule, makes the check exact and O(1) while keeping the class at 24 bytes, for about 1.5 percent of capacity. Making the magic depend on the address, for example `HeaderMagicId ^ uintptr_t(address)`, makes accidental matches essentially impossible with zero extra memory; glibc's safe-linking and tcache key use this idea. Walking the chunk chain from the base is exact but linear and needs the padded size stored somewhere. The interview framing is that exact validation needs a side table or a chain walk, a bump allocator's whole value is having neither, so a canary plus range and alignment checks is the right trade, strengthened with an address-dependent tag if needed.

Production allocators mostly trust the caller, because freeing a wrong pointer is already undefined behavior. glibc checks alignment and size sanity and catches double frees, but does not prove the pointer is a chunk start. Those checks are defense in depth, not a contract.

A free function should accept `nullptr` as a no-op. That is the contract of `delete` and of `free`, and it exists so cleanup code does not need a branch on every pointer.

## Errors and pitfalls

The reference solution to the getcracked problem is a useful catalogue of mistakes, each of which passes the hidden tests.

Its capacity check compares the padded request against the space left but forgets the 16-byte header, which is added to the used count only afterwards. A 100-byte buffer accepts an 80-byte request that rounds to 96 and writes bytes 0 through 111. The fix is to include header and padding in the check before writing anything, which `std::align` does naturally when the space handed to it already excludes the header.

Its free decrements the used count for any chunk, and the used count doubles as the bump cursor. Freeing a chunk in the middle moves the cursor back over live data, and the next allocation overwrites a live chunk. Only the most recent allocation can be popped safely, which is the stack-allocator rule.

Its alignment rounds the size, not the address, so requests above 16 bytes of alignment are silently misaligned. It also over-rounds a size that is already a multiple of the alignment, because it adds a full `align` instead of `align - 1`.

It placement-news a 24-byte `Chunk` rather than the 16-byte `ChunkHeader`, so the `Memory` pointer field is written into the first 8 bytes of the payload it is about to hand out. Nothing reads it back, so it is harmless, but only the header belongs in the buffer.

## Additional syntax examples

These are independent sketches, not one program.

```cpp
// Storage and ownership in 24 bytes.
std::unique_ptr<std::byte[]> base_;   // 8: owns the buffer, delete[] automatic
size_t cap_;                          // 8
size_t cur_{ 0 };                     // 8: offset of the first unused byte
static_assert(sizeof(Allocator) == 24);

// Round up to a multiple of a. Say it: add a - 1, then round down.
size_t roundUp(size_t x, size_t a) { return ((x + a - 1) / a) * a; }
// Power-of-two form: (x + a - 1) & ~(a - 1)

// std::align: moves p to the next aligned address if size fits, shrinks space by the padding.
void*  p     = base_.get() + cur_ + sizeof(ChunkHeader);
size_t space = cap_ - cur_ - sizeof(ChunkHeader);
if (!std::align(a, size, p, space)) throw std::bad_alloc{};

// In: placement new creates the header in raw bytes.
new (bytes - sizeof(ChunkHeader)) ChunkHeader{ size, ChunkHeader::HeaderMagicId };

// Out: reinterpret_cast re-finds it.
auto* h = reinterpret_cast<ChunkHeader*>(bytes - sizeof(ChunkHeader));

// Range check with integers, not pointer comparison.
const auto addr  = reinterpret_cast<std::uintptr_t>(bytes);
const auto begin = reinterpret_cast<std::uintptr_t>(base_.get());
if (addr < begin) throw std::bad_alloc{};        // before subtracting
const size_t off = addr - begin;

// Stack-style pop: only if this chunk ends exactly at the cursor.
if (off + h->Size == cur_) cur_ = off - sizeof(ChunkHeader);
```

## Interview Q&A

### Write me a bump allocator.

A bump allocator owns a fixed buffer and a cursor. Allocate rounds the cursor up to the requested alignment, checks that the size fits in what remains, returns the aligned address, and advances the cursor past the allocation. Reset moves the cursor back to zero. There is no per-pointer free, because the allocator keeps no record of individual allocations; every allocation in the arena shares one lifetime and is released together. That is what makes it two instructions per allocation and also what limits it to workloads with a common lifetime, like a frame or a request.

### How is a stack allocator different?

A stack allocator adds a free that works only for the most recent live allocation, popping the cursor back to where that allocation began. Freeing anything else cannot reclaim space, because the cursor is the only state and moving it back over live data would corrupt it. Allocations push, frees pop, and pops only come from the top.

### Why does the header-and-magic version not count as a bump allocator?

Because a bump allocator's defining property is having no per-allocation metadata. A header is metadata. It only pays for itself if the allocator intends to find and reuse freed holes later, which is a first-fit or free-list design. In a header-based design freeing means marking the block, and allocating means possibly walking for a hole; that is a general-purpose allocator, not a bump allocator.

### How do you guarantee alignment when each allocation has a header?

I decide the payload address first: the earliest address after the cursor that leaves room for a header, rounded up to the requested alignment. The header goes immediately before it. As long as I never round to less than the header's own alignment, the header is aligned automatically, because a multiple of any larger power of two is still a multiple of 8, and so is that minus 16. One rounding, both guarantees. `std::align` does the rounding and the fit check in one call.

### How do you keep the allocator at 24 bytes?

Base pointer, capacity, cursor. The base pointer is a `unique_ptr<std::byte[]>`, which is one word and handles `delete[]`. The trap is an ownership flag, which pads the class to 32; if the class is the sole owner on every path, the flag is unnecessary.

### What does placement new do and why do you need it?

Ordinary `new` acquires storage and then constructs; placement new skips the first step and constructs at an address I supply. I need it because the storage for the header already exists inside my buffer as raw bytes, and placement new is the operation that turns those bytes into an object. Later I find that object again with `reinterpret_cast`, which is legitimate because the object is really there.

### How do you validate a pointer in free without a table?

Null returns as a no-op. Then range and alignment checks using integer addresses, then a magic tag in the header. The tag is a constant meaning "live chunk written by this allocator," and zeroing it on free makes a double free fail the same check. Exact validation would need a side table or a chain walk, which is the metadata a bump allocator exists to avoid; if I want the canary stronger I make it address-dependent.

## Practice history

### getcracked problems

- [x] Bump Memory Allocator — 07/09 — solved with heavy guidance; first submission failed one hidden test because `Deallocate(nullptr)` threw instead of returning. Lessons: null free is a no-op by contract; the problem is a mislabeled stack allocator with first-fit scaffolding; align the address, not the size; `std::align` replaces the round-up formula; `unique_ptr<std::byte[]>` is the ownership spelling. Final solution verified under ASan and UBSan. **Rule to remember: if asked for a bump allocator, no headers, no per-pointer free, just cursor and reset.**
- [x] Stack Allocator (template `Capacity`, buffer on the stack) — 07/09 — solved; first version used `unique_ptr` (heap, violates the no-`new` rule) and had `&`/`!=` precedence wrong in the power-of-two check, both caught before submit. Final: `alignas(std::max_align_t) std::byte buf_[Capacity]`, `std::align`, cursor update `Capacity - remaining + size`, reset is `offset_ = 0`. Lessons: `std::align` subtracts the padding from space, not the size; align the buffer itself so the first allocation never pads; this one is the genuine bump allocator, the previous problem was not.
