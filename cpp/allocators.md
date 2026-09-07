# Allocators

## What a bump allocator does

A bump allocator hands out memory by advancing a cursor through a buffer. The cursor records where the next allocation can begin. Each request skips any alignment padding, checks that enough space remains, and moves the cursor past the returned block. It is fast because it does not search previously freed blocks for a suitable hole.

A simple fixed-buffer implementation needs a base address, a capacity, and a cursor. Individual deallocation does not reclaim space in this design. A reset makes the whole buffer available again, so the caller must finish using its objects before resetting. This works well for allocations used during one frame, one request, or one parsing operation. Objects can have different lifetimes even though their storage is reclaimed together; any required object destruction is a separate responsibility.

An allocator can still expose a deallocation function that does nothing or records that a block is no longer live. For example, the standard library's `std::pmr::monotonic_buffer_resource` has a deallocation operation with no effect. The presence of that function does not make it a stack allocator. See the [standard's monotonic resource contract](https://eel.is/c++draft/mem.res.monotonic.buffer).

## The three designs, by how space is reclaimed

A **bump allocator** advances through unused storage and normally reclaims it in bulk. A minimal implementation needs no header for each allocation, but a particular interface may add headers for validation or diagnostics.

A **stack allocator** can reclaim the most recent live allocation first. This is last-in, first-out order, often shortened to LIFO. It restores the cursor to its position before that allocation, including any padding. A header can record the previous cursor, or the caller can supply a saved position. Moving the cursor backward over another live allocation would allow later requests to overwrite it.

A **general-purpose allocator** can reclaim blocks in arbitrary order and reuse the resulting gaps. It needs bookkeeping to locate available space. First-fit searches for the first suitable gap, best-fit chooses a suitable gap with minimal excess space, and segregated free lists group available blocks by size. The bookkeeping need not live in a header directly before every block. General-purpose allocation functions such as `malloc` typically use designs from this family.

The getcracked exercise adds a `ChunkHeader` with a size and magic tag to bump allocation. Its stated `Deallocate` requirement is to zero those fields; that does not require reclaiming the block or rewinding the cursor. Headers help implement that validation contract. If a solution also reclaims space, it must specify and correctly implement an additional policy, such as popping only the latest allocation or tracking reusable gaps.

## Alignment: align the returned address

Alignment describes where an object may begin. On the ordinary address model used in this exercise, an 8-byte-aligned address is divisible by eight. `alignof(T)` gives the alignment required by type `T`, in bytes; `sizeof(T)` gives its storage size. A header can therefore have a size of 16 bytes and an alignment of eight bytes.

The cursor does not have to be aligned after an allocation. Suppose the buffer begins at an 8-byte-aligned address. A 16-byte header followed by a 3-byte payload ends at offset 19. The next allocation can skip five bytes, put its header at offset 24, and put its payload at offset 40. The unused bytes are padding.

```text
Offsets within an initially 8-byte-aligned buffer:
0             16   19      24             40   43
| header      |data| pad   | header       |data|
```

For a header immediately before the payload, first find the earliest possible payload address: the current cursor plus the header size. Align that address, then place the header immediately before it. Use an alignment at least as strict as both the requested alignment and the header's alignment. For power-of-two alignments, taking the larger value does this. The header also ends up aligned because its size is a multiple of its own alignment.

Rounding only the requested size is insufficient unless the starting address is already suitably aligned. For example, an offset of 16 from a 64-byte-aligned base is still misaligned for a 64-byte request, regardless of the block's length.

To round a numeric address `x` up to a multiple of positive `a`, one formula is `((x + a - 1) / a) * a`. For a power of two, the equivalent bit formula is `(x + a - 1) & ~(a - 1)`. Both require guarding against overflow in the addition. Rounding 19 up to a multiple of eight gives 24; rounding 24 leaves it unchanged. The library function below avoids writing this arithmetic yourself.

## What std::align changes

`std::align`, from `<memory>`, finds an aligned start within a supplied region. It does not allocate memory. It receives an alignment, a requested size, a pointer variable, and a variable containing the available byte count. On success, it moves the pointer past the padding and subtracts only that padding from the byte count. The requested payload size is still included in the remaining count. If there is no fit, it returns `nullptr` and leaves both variables unchanged. See the [std::align contract](https://eel.is/c++draft/ptr.align).

The pointer variable has type `void*`, which holds an address without naming an object type. This lets the function work with raw storage for any type. The pointer and byte count are passed by reference so the function can update the caller's variables.

This sketch assumes a valid buffer, `used <= capacity`, and a nonzero power-of-two alignment. It leaves space for a header before asking the library to find the payload:

```cpp
const size_t headerSize = sizeof(ChunkHeader);
size_t available = capacity - used;
if (available < headerSize) throw std::bad_alloc{};

void* candidate = memory + used + headerSize;
size_t space = available - headerSize;
size_t effectiveAlignment = std::max(alignment, alignof(ChunkHeader));
if (!std::align(effectiveAlignment, requestedSize, candidate, space))
    throw std::bad_alloc{};

auto* payload = static_cast<std::byte*>(candidate);
size_t padding = (available - headerSize) - space;
// Construct the header here; update used only after allocation succeeds.
used += padding + headerSize + requestedSize;
```

The first check ensures that subtracting the header size cannot underflow. `std::align` then checks whether padding and payload fit in the remaining region. Conceptually, the consumed space is still just `padding + header size + requested size`. `std::bad_alloc{}` constructs an exception object using braces; `std::bad_alloc()` would also work here.

For a member buffer, `alignas(std::max_align_t) std::byte buffer[Capacity];` requests suitable alignment for types with fundamental alignment. `alignas` applies an alignment requirement to a declaration. This can avoid initial padding for those requests, but a header or a stricter requested alignment can still require padding. The unused gap before an allocation is called internal fragmentation; aligning one address skips at most `alignment - 1` bytes.

## Constructing objects in raw storage

`std::byte`, from `<cstddef>` since C++17, represents a byte of raw storage. It supports bitwise operations rather than ordinary integer arithmetic; `std::to_integer<int>(b)` explicitly obtains an integer from a byte value. A `std::byte*` advances one byte per pointer step and may inspect an object's underlying bytes, which makes it useful for allocator buffers.

Placement new constructs an object at an address whose storage already exists. The spelling `::new (address) T{arguments}` uses the global placement form from `<new>`. Here is a complete local example:

```cpp
#include <cstddef>
#include <new>

struct Header { std::size_t size; };
alignas(Header) std::byte storage[sizeof(Header)];
auto* header = ::new (static_cast<void*>(storage)) Header{3};
// header points to the Header just constructed inside storage.
std::size_t requested = header->size;  // 3
```

The placement expression returns a typed pointer, so keeping that pointer avoids an extra cast. It does not allocate the backing storage: do not call ordinary `delete` on `header`. If the constructed object needs destruction, destroy it before reusing or releasing its storage. For a class type, an explicit destructor call can be written `header->~Header()`. This simple header has a trivial destructor and needs no cleanup. The owner of a dynamically allocated backing buffer still releases that buffer later; the local array above ends with its scope.

If only a byte address is available later, `reinterpret_cast<ChunkHeader*>(headerAddress)` can recover a pointer to a live, suitably aligned header at that address. The cast creates a pointer; it neither reads memory nor constructs an object. Accessing `pointer->Size` is the separate read. Casting an arbitrary address does not prove that a header is there.

For a trivially copyable header, copying its bytes into a local header with `std::memcpy` is another useful approach. It avoids accessing the source through a typed header pointer, but still requires an in-bounds, readable byte region and valid representations for the fields. Checking a random candidate header needs those safeguards before inspecting its magic tag.

## Ownership inside a size budget

A simple owning implementation stores the buffer pointer, capacity, and cursor. On the exercise's usual 64-bit target, an eight-byte pointer and two eight-byte `size_t` fields total 24 bytes. This is a target layout assumption, not a guarantee for every C++ platform.

`std::unique_ptr<std::byte[]>` can own a buffer created by `new std::byte[capacity]` and automatically call `delete[]` when destroyed. With its default deleter it is commonly pointer-sized, but verify the actual allocator size with `static_assert(sizeof(Allocator) <= 24)`. See the [unique_ptr ownership and deleter rules](https://eel.is/c++draft/unique.ptr).

If both constructors transfer sole ownership to the allocator, an ownership flag is unnecessary. Adding a `bool` would commonly increase this layout to 32 bytes because of padding. Adopting an external pointer into the same `unique_ptr` is valid only if that memory can be released with the matching `delete[]`. Ownership alone does not tell us whether the buffer originally came from `new[]`, `malloc`, or some other source.

## Validating a pointer on free

A custom deallocation function must follow its own contract. `delete` and `std::free` accept null as a no-op, and doing the same is a useful convention for this exercise. Other pointers need validation before the function reads or writes the supposed header.

`std::uintptr_t`, from `<cstdint>` on platforms that provide it, is an unsigned integer type that can hold a converted pointer value. It lets this exercise work with addresses as numbers. That conversion does not read the pointed-to object. Numeric ordering and arithmetic here assume the ordinary address representation of the target platform.

```cpp
const auto address = reinterpret_cast<std::uintptr_t>(bytes);
const auto begin = reinterpret_cast<std::uintptr_t>(memory);
if (address < begin) throw std::bad_alloc{};
const auto offset = address - begin;
```

If the buffer starts at address 1000 and `bytes` represents address 1024, the offset is 24. Check the lower bound before subtracting so unsigned arithmetic cannot wrap. Then check that a complete header fits before that offset, that the offset does not exceed the used region, and that the header address has the required alignment. These checks avoid relying on ordered comparisons between pointers to unrelated arrays.

The magic field is a known marker stored in each live allocation's header. It is shared by all headers, rather than uniquely identifying one block. Zeroing it on deallocation lets a later check reject a repeated free in a design that does not reuse that storage. Also check that the recorded size fits before the current cursor.

These checks catch common mistakes but do not prove that a pointer is an allocation start. Payload bytes might happen to look like a valid header. Making the marker depend on the address can reduce accidental matches, but it still is not exact validation and may conflict with a required fixed magic value.

Exact validation needs trustworthy records of live allocation starts. One option is a bitmap: a bit for each possible aligned start, set when allocated and cleared when freed. At one bit per eight bytes of buffer, the bitmap alone costs about 1.6 percent of capacity, plus rounding. Another option is walking recorded allocations, which takes time proportional to the number visited and must account for padding. These are additional designs, not guarantees supplied by the magic check.

## Errors and pitfalls

Check the total space consumed before writing a header or payload. On the exercise's 64-bit layout, a request rounded to 96 bytes plus a 16-byte header cannot fit in a 100-byte buffer. Avoid unchecked additions and unsigned subtraction; subtract each component only after checking that it fits.

Zeroing a header does not make its storage reusable. Decreasing a bump cursor when freeing a middle block can make the next allocation overwrite a later live block. Reclaiming a top block must restore the cursor from before its padding, so storing only its requested size may be insufficient.

Validate that alignment is nonzero and a power of two before calling `std::align`. Rounding a request of three up to four does not preserve divisibility by three, so silently choosing the next power of two is not a general fix for an invalid request.

Construct only the header in the reserved header area. Constructing a 24-byte `Chunk` where only 16 bytes were reserved for `ChunkHeader` writes into the payload and can exceed the buffer for a small request. The extra pointer field is not needed there.

## Additional syntax examples

These are independent sketches, not one program. The size comments describe the exercise's usual 64-bit target.

```cpp
// Three members for ownership and cursor bookkeeping.
std::unique_ptr<std::byte[]> base_;  // Commonly 8 bytes with the default deleter.
size_t capacity_;                  // 8 bytes on this target.
size_t used_{0};                    // 8 bytes on this target.
// Place this check after the complete Allocator class definition.
static_assert(sizeof(Allocator) <= 24);

// Check the requested alignment before calling std::align.
if (alignment == 0 || (alignment & (alignment - 1)) != 0)
    throw std::bad_alloc{};

// After finding a valid aligned payload with room for the header:
auto* header = ::new (static_cast<void*>(payload - sizeof(ChunkHeader)))
    ChunkHeader{requestedSize, ChunkHeader::HeaderMagicId};
```

## Interview Q&A

### Write me a bump allocator.

I keep a buffer, its capacity, and a cursor. Each allocation finds an aligned address after the cursor, checks that the request fits, and advances past the returned block. I reclaim storage together with a reset or when the allocator is destroyed. Individual deallocation normally does not recover space, which keeps allocation simple and avoids searching for holes.

### How is a stack allocator different?

It can recover the most recent allocation's space immediately. Allocations push the cursor forward, and frees pop it back in reverse order. I need to recover the previous cursor, including any alignment padding, and ensure I am not moving backward over a live allocation.

### Can a bump allocator have headers and a deallocation function?

Yes. Headers can record sizes or validate deallocation without making freed space reusable. I classify the allocator by how it allocates and reclaims storage. A function that just zeros a header still leaves the bump cursor where it was.

### How do you guarantee alignment when each allocation has a header?

I leave room for the header, then align the payload address. The header goes immediately before the payload. I use an alignment that satisfies both types and include the padding, header, and requested bytes in the capacity check. `std::align` can find the aligned payload and check whether it fits in the space after reserving the header.

### How do you keep the allocator at 24 bytes?

I store only the buffer owner, capacity, and cursor, and check the class size on the target compiler. With a pointer-sized owner and eight-byte size fields, that fits in 24 bytes. Sole ownership on both construction paths means I do not need an ownership flag; I still need to use the correct way to release the supplied buffer.

### What does placement new do and why do you need it?

It constructs an object inside storage I already have. I use it to create the header in the allocator's buffer, and it returns a pointer to that header. It does not allocate another buffer, and the buffer's owner remains responsible for releasing the storage.

### How do you validate a pointer in free without a table?

I handle null according to the contract, then check the range and header alignment before inspecting the size and magic marker. That catches common invalid pointers and repeated frees, but payload data could imitate a header. If exact validation is required, I need a reliable record of allocation starts, such as a bitmap or a traversable allocation list.

### How would you support individual free calls in LIFO order on a stack allocator?

I record the cursor position from before each allocation and enough information to verify that the block being freed is the current top. Freeing it restores that saved cursor. Checking the block's end alone does not recover padding before it. A related interface offers a saved mark and rewind; rewinding invalidates everything allocated since that mark, so the caller must respect those lifetimes.

### What happens if align is not a power of two?

I reject it before calling `std::align`, since a nonzero power of two is a precondition. In this throwing interface I can report the failure with an exception. I check zero explicitly as well as using the power-of-two bit test. I do not silently round arbitrary alignment requests because that may change their meaning.

### How does a stack allocator compare to alloca?

`alloca` obtains storage from the current function's stack frame, and that storage lasts until the function returns. It is a compiler extension, and repeated calls in a loop keep consuming stack space. A stack allocator describes a last-in, first-out reclamation policy; its backing buffer could be local or dynamically allocated. An allocator object can expose explicit capacity checks and reclamation operations. A buffer stored on the call stack does not, by itself, imply a LIFO allocator policy.

### What is the purpose of std::max_align_t as the default alignment?

Its alignment covers types with fundamental alignment requirements, making it a useful default for a general raw-storage buffer. Types with extended alignment can require more, so callers must request that stronger alignment. The numeric value is platform-dependent. `__STDCPP_DEFAULT_NEW_ALIGNMENT__` describes the alignment guaranteed by ordinary allocation with `operator new`; it is a related guarantee, not a universal synonym for `alignof(std::max_align_t)`.

## Practice history

Editorial clarification: the entries below preserve the original session observations. The presence of headers or a deallocation function does not establish the allocator category. Use the reclamation rules explained above; the earlier “mislabeled” conclusion is superseded. The recorded hidden-test result is an observation about that exercise, not a universal contract for custom allocators.

### getcracked problems

- [x] Bump Memory Allocator — 07/09 — solved with heavy guidance; first submission failed one hidden test because `Deallocate(nullptr)` threw instead of returning. Lessons: null free is a no-op by contract; align the address, not the size; `std::align` replaces the round-up formula; `unique_ptr<std::byte[]>` is the ownership spelling. Final solution verified under ASan and UBSan. Original session conclusion, since refined: the exercise looked like a mislabeled stack allocator because it had headers and a `Deallocate`; the taxonomy section above explains why those do not change the category. **Rule to remember: if asked for a bump allocator, the core is a cursor and a reset. Do not add per-allocation headers or reclamation logic unless the interface requires them; if a deallocate function is required, make it a no-op or validation-only, and say so.**
- [x] Stack Allocator (template `Capacity`, buffer on the stack) — 07/09 — solved; first version used `unique_ptr` (heap, violates the no-`new` rule) and had `&`/`!=` precedence wrong in the power-of-two check, both caught before submit. Final: `alignas(std::max_align_t) std::byte buf_[Capacity]`, `std::align`, cursor update `Capacity - remaining + size`, reset is `offset_ = 0`. Lessons: `std::align` subtracts the padding from space, not the size; align the buffer itself so the first allocation never pads; this one is the minimal bump allocator with no headers and reset-only reclamation, the previous problem was the same allocation model with a validation header added.
