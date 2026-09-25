# Associative Containers: Hashing, std::unordered_map / std::map, std::set / std::unordered_set

## Hash tables in two flavors

A hash table maps a key to a bucket index by hashing the key and reducing modulo the bucket count, then resolves collisions in one of two ways. Separate chaining keeps a linked list, or some other small container, of entries per bucket; a lookup hashes, walks one chain, and compares keys with the equality predicate. Open addressing keeps every entry inside the bucket array itself and, on collision, probes for another slot by a fixed rule: linear probing steps to the next slot, quadratic probing steps by growing gaps, and double hashing steps by a second hash. Open addressing needs tombstones for deletion, since clearing a slot would break the probe chains that passed through it, and it degrades sharply as the table fills, so it rehashes at a lower load factor, typically below 0.7. Chaining tolerates load factors around 1 and deletes cleanly, but every entry is a separate allocation and a chain walk chases pointers across cache lines. Open addressing with linear probing is what a latency-sensitive table usually wants: the probe sequence stays in one or two cache lines and there is one allocation for the whole table.

`std::unordered_map` and `std::unordered_set` are specified in a way that forces separate chaining: pointers and references to elements must survive rehashing, `erase` must not invalidate other elements, and the bucket interface exposes `bucket_count()`, `bucket(key)`, `load_factor()`, `max_load_factor()`, and per-bucket iteration. Every element is a heap node holding the value, a next pointer, and usually the cached hash. When `size()` exceeds `max_load_factor() * bucket_count()`, the table rehashes to a larger prime or power-of-two bucket count and every iterator is invalidated while every pointer to an element stays valid. `reserve(n)` sizes the bucket array for `n` elements up front; `rehash(n)` sets the bucket count directly. The hash is `std::hash<Key>` by default and equality is `std::equal_to<Key>`; a user-defined key needs both, either as a `std::hash` specialization plus `operator==`, or as functor types passed as template arguments. A hash that returns the object's address, as in `reinterpret_cast<std::uintptr_t>(&a)`, together with an `operator==` that compares addresses, makes every distinct object a distinct key, including copies of the same value.

## Ordered containers are red-black trees

`std::map`, `std::set`, `std::multimap`, and `std::multiset` are red-black trees with an explicit header node. Each node holds a parent pointer, a left and right child pointer, a color bit, and the payload, which is `std::pair<const Key, T>` for the maps and `Key` for the sets. The header's three pointers are repurposed: parent points at the root, left at the smallest node, right at the largest, and in an empty tree all three point at the header itself. The header is the `end()` position, so `begin()` is the header's left pointer and `--end()` reaches the maximum through its right pointer. Iterator `++` is an in-order step, right child then leftmost descendant or climb until arriving from a left child; a single step is not constant time but a full traversal crosses each edge twice, so it is amortized constant as the standard requires. On MSVC the header is a separate heap node, every null link points at the header instead, and each node carries an `_Isnil` flag; libstdc++ and libc++ embed the header in the container object, which saves an allocation and complicates moves because the root's parent pointer must be re-aimed. A node base is 32 bytes on 64-bit before payload, so `std::set<int>` costs about 40 bytes plus allocator overhead per element and the nodes are scattered, which is why a sorted `std::vector` with `std::lower_bound`, or C++23 `std::flat_map`, wins for read-heavy data. The comparator and allocator sit in compressed pairs and cost nothing when empty.

The member `lower_bound`, `upper_bound`, `find`, `count`, and `equal_range` walk the tree from the root in logarithmic time. The free `std::lower_bound(s.begin(), s.end(), x)` gives the same answer but does its binary search with `std::advance` and `std::distance` over bidirectional iterators, so it is logarithmic in comparisons and linear in steps: linear time on a `std::set`. Use the member whenever one exists. A transparent comparator, `std::set<std::string, std::less<>>`, lets `s.find("abc")` avoid constructing a `std::string`; see the heterogeneous lookup note in [strings.md](strings.md).

```cpp
std::set<int> s{ 9, 3, 5, 1, 7 };
auto a = s.lower_bound(6);                          // O(log n): tree walk from the root
auto b = std::lower_bound(s.begin(), s.end(), 6);   // O(n) steps: advance over a bidirectional iterator
```

## Iteration order and the value type

The unordered containers promise nothing about the order of elements, so `*counts.begin()` after inserting 1 and 2 into an `std::unordered_set<int>` is whichever the implementation's hash and bucket layout put first. The standard calls this unspecified: a valid element comes out, the program is well-formed, but which one is not defined and may change between library versions, so a test that depends on it is a bug waiting for an upgrade. It is not undefined behavior, and it is not implementation-defined either, because the implementation does not have to document its choice. Ordered containers iterate in comparator order, which is the one guarantee to rely on.

The value type of a map is `std::pair<const Key, T>`, with a const key so that nothing can change a key in place and corrupt the ordering or the hash. A range-based for written as `for (const std::pair<Item, int>& count : counts)` names a different type, `pair<Item, int>` without the const, so each element is converted to a temporary of that type by copying the key, and the reference binds to the temporary. With an `Item` whose copy constructor prints `2`, and two elements emplaced from `Item{}` temporaries, the program prints `1212` for the two constructions and the two copies into the nodes, then `22` for the two copies made by the loop: `121222`. `emplace(Item{}, 1)` still copies, because the argument is a named parameter by the time the node is built; only `emplace(std::piecewise_construct, ...)` or `try_emplace` constructs the key in place. Write `const auto&`, or `const std::pair<const Item, int>&`, or structured bindings `const auto& [item, n]`, and no copy happens.

```cpp
std::unordered_map<Item, int> counts;
counts.reserve(2);
counts.emplace(Item{}, 1);                            // prints 1 then 2: temporary, then copy into the node
for (const std::pair<Item, int>& c : counts) {}      // copies each key again: the type lacks const
for (const auto& [item, n] : counts) {}              // no copy
```

## Lookup that misses

`find` returns `end()` on a miss and dereferencing it is undefined behavior, so a lookup is two steps: find, then compare against `end()`. A key that looks right can still miss. `std::to_string` has no `char` overload, so `std::to_string(c)` for `char c = '2'` promotes to `int` and produces `"50"`, the character's code, which is not the key `"2"`; `iter->second` then reads through `end()`. Build the key with `std::string(1, c)` or `std::string{c}`. `operator[]` on a map default-constructs and inserts a value on a miss, which is convenient for counting and a silent insertion everywhere else; `at()` throws `std::out_of_range`; `contains` (C++20) answers without an iterator. `count` on a non-multi container is zero or one.

```cpp
std::unordered_map<std::string, std::string> map{ {"2", "abc"} };
char c = '2';
auto iter = map.find(std::to_string(c));              // to_string(int) gives "50": miss
std::cout << iter->second;                            // UB: dereferencing end()
```

## Errors and pitfalls

- **Undefined behavior: dereferencing the result of `find` without checking it against `end()`.**
- **Logical error: `std::to_string(char)`.** It formats the character's integer code; use `std::string(1, c)`.
- **Unspecified: the iteration order of an unordered container.** Do not test against it or depend on `*begin()`.
- **Logical error: `std::lower_bound` on a `std::set` or `std::map`.** Linear time; call the member.
- **Logical error: `for (const std::pair<K, V>& p : m)`.** The element type is `pair<const K, V>`; the mismatch copies every element. Use `const auto&`.
- **Logical error: `m[key]` to test membership.** It inserts a default-constructed value; use `find`, `contains`, or `count`.
- **Undefined behavior: mutating a key in place**, which is why the key is const and why `extract` exists for moving nodes.
- **Undefined behavior: using an unordered container iterator across a rehash.** Pointers to elements survive; iterators do not.
- **Invalid: an `unordered_map` keyed on a type with no `std::hash` specialization and no hasher argument.**
- **Logical error: a hash and equality that disagree.** Equal keys must hash equal; an address-based hash makes every copy a new key.

## Additional syntax examples

```cpp
template <> struct std::hash<Item> {
    std::size_t operator()(const Item& a) const noexcept { return std::hash<int>{}(a.id); }
};
std::unordered_map<Item, int> counts;
counts.reserve(1024); counts.max_load_factor(0.5f);
auto [it, inserted] = counts.try_emplace(item, 0);   // key constructed in place, nothing on a hit
if (auto f = counts.find(key); f != counts.end()) use(f->second);
if (counts.contains(key)) {}                          // C++20
std::size_t b = counts.bucket(key); counts.bucket_count(); counts.load_factor();

std::map<std::string, int, std::less<>> m;            // transparent comparator: m.find("abc") without a std::string
auto lo = m.lower_bound("k");                         // member, O(log n)
auto node = m.extract("k"); node.key() = "j"; m.insert(std::move(node));   // rekey without reallocation
for (const auto& [k, v] : m) {}
std::set<int> s; s.insert(3); s.emplace(4); s.erase(3); s.count(4); *s.rbegin();   // largest
```

## Interview Q&A

### Separate chaining versus open addressing: which does `std::unordered_map` use and why?

Chaining, because the standard requires that pointers and references to elements survive rehashing and that erasing one element does not invalidate others, and because it exposes a bucket interface. Each element is its own heap node, so lookups chase pointers. Open addressing keeps everything in one array, probes on collision, needs tombstones for deletion, and stays inside a cache line, which is why hand-written low-latency tables use it.

### `std::unordered_set<int> s; s.insert(1); s.insert(2); std::cout << *s.begin();`

Unspecified. The container is well-formed and prints a valid element, but which one depends on the hash, the bucket count, and the library, and none of that is documented or stable. It is neither undefined nor implementation-defined behavior.

### Why is `std::lower_bound(s.begin(), s.end(), 6)` on a `std::set` linear?

The free algorithm binary-searches by `std::advance` and `std::distance`, which on a bidirectional iterator step one node at a time. Comparisons stay logarithmic but iterator movement is linear. `s.lower_bound(6)` walks the tree from the root in logarithmic time.

### An `Item` prints `1` on construction and `2` on copy. Two `emplace(Item{}, n)` calls, then `for (const std::pair<Item, int>& c : counts)`. Output?

`121222`. Each emplace constructs a temporary and copies it into the node, `12` twice. The loop names `pair<Item, int>` while the element type is `pair<const Item, int>`, so each element converts to a temporary by copying the key, `2` twice. `const auto&` removes the last two.

### `map.find(std::to_string(c))` with `char c = '2'` and key `"2"`. What prints?

Undefined behavior. `to_string` has no `char` overload, the character promotes to `int`, the key becomes `"50"`, the lookup misses, and `iter->second` dereferences `end()`.

### What does a `std::map` node look like and why is iteration slow?

Parent, left, and right pointers, a color, and a `pair<const Key, T>` payload, one heap allocation per element, about 32 bytes of overhead before the payload and the allocator's own header. Nodes land wherever the allocator puts them, so an in-order walk is a pointer chase across cache lines. A sorted vector or `std::flat_map` keeps the same order in contiguous memory.

### When does an unordered container rehash, and what survives?

When `size()` would exceed `max_load_factor() * bucket_count()` after an insertion, or on an explicit `rehash` or `reserve`. All iterators are invalidated. Pointers and references to elements survive because the nodes are relinked, not moved.

## Practice history

### Reading

- 13/09/2026: Raymond Chen, Inside STL: the map, set, multimap, and multiset. William Fiset open addressing and separate chaining videos, Bo Qian associative containers, The Cherno unordered_map and map, Coding Jesus hashtable implementation, and Kenny Yip set videos not watched; the hashing section is from my own notes. Implement LRU Cache problem not attempted.

### Questions (getcracked)

- Per platform record, rescraped 13/09/2026. std::unordered_map & std::map: Fifty shades of '2' (`to_string(char)` gives "50", miss, deref of `end()` is UB) ok; Wrong map, bro. (`pair<Item,int>&` in the range-for copies the key because the element type is `pair<const Item,int>`; prints 121222) wrong first attempt, retest in a week. std::set & std::unordered_set: In the beginning... (unordered iteration order is unspecified) wrong first attempt, retest in a week; Bound to love lower_bound. (free `std::lower_bound` on a set is O(N) steps) wrong first attempt, retest in a week. Hashing: Where are we? is a name-lookup question filed in [inheritance.md](inheritance.md), wrong first attempt.
- Anki: unordered order is unspecified, not UB; free `lower_bound` on a set is linear, the member is logarithmic; map element type is `pair<const K, V>`, a mismatched reference type copies; `to_string(char)` formats the code; `find` then compare with `end()`; `[]` inserts; rehash kills iterators, not pointers; `std::unordered_map` is chaining by specification.

<!-- gc-questions:start -->

## Related getcracked questions

Pulled from the Beginner C++ progress tree. ✓ answered correctly, ✗ attempted and missed, ○ not attempted yet. Regenerate with `python3 cpp/tools/gc_links.py` after re-scraping.

### Hashing
- ✗ [Where are we?](https://getcracked.io/question/913) — Medium

### std::unordered_map & std::map
- ✓ [Fifty shades of '2'](https://getcracked.io/question/1843) — Medium
- ✗ [Wrong map, bro.](https://getcracked.io/question/1003) — Hard
- ○ [Implement LRU Cache](https://getcracked.io/problem/70/implement-lru-cache) — problem

### std::set & std::unordered_set
- ✗ [In the beginning...](https://getcracked.io/question/1004) — Easy
- ✗ [Bound to love lower_bound.](https://getcracked.io/question/1097) — Medium

<!-- gc-questions:end -->
