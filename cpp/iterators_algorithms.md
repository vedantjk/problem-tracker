# Iterators and Standard Library Algorithms

## What an iterator is

An iterator is an object that walks a container and gives access to each element on the way through a uniform interface: `++` advances, `*` reads or writes the current element, and `!=` compares against an end position. A raw pointer is the simplest iterator over contiguous storage, and `end` is always one past the last element, never the last element itself. Taking `&arr[std::size(arr)]` to get that position is undefined behavior because it indexes out of range even though nothing is read; write `arr.data() + std::size(arr)` instead. Containers expose `begin()` and `end()` members, and `std::begin` and `std::end` do the same for C-style arrays, which is why a range-based for works on them and not on a `new[]` array, where no length exists to compute an end. Loop with `p != end` rather than `p < end`, because every iterator category supports `!=` and only random-access ones support `<`.

```cpp
std::array arr{ 0, 1, 2, 3, 4, 5, 6 };
auto begin{ arr.data() };
auto end{ begin + std::size(arr) };            // one past the last element
for (auto p{ begin }; p != end; ++p) std::cout << *p << ' ';
```

## The six iterator categories

Each category includes everything above it. An input iterator can be read and advanced in a single pass; an output iterator can be written and advanced in a single pass and cannot be compared; a forward iterator is multi-pass and default constructible; a bidirectional iterator adds `--`; a random-access iterator adds `it + n`, `it - it`, `it[n]`, and the relational operators; and a contiguous iterator, a tag since C++17 and a concept since C++20, promises that the elements are adjacent in memory, so `&*(it + n) == &*it + n`. The category is what an algorithm dispatches on through `std::iterator_traits<It>::iterator_category`, or the C++20 concepts `std::input_iterator` through `std::contiguous_iterator`: `std::distance` and `std::advance` are constant time on random access and linear otherwise, and `std::sort` refuses anything below random access, which is why `std::list` and `std::forward_list` carry their own `sort` member.

| category | adds | standard sources |
|---|---|---|
| input | read `*it`, `++`, `==`, single pass | `istream_iterator`, `istreambuf_iterator` |
| output | write `*it = x`, `++`, single pass, no comparison | `ostream_iterator`, `back_inserter`, `inserter`, `front_inserter` |
| forward | multi-pass, default constructible | `forward_list`, `unordered_map`, `unordered_set` and their multi variants |
| bidirectional | `--` | `list`, `map`, `set`, `multimap`, `multiset` |
| random access | `+ n`, `- it`, `[n]`, `<` | `deque` |
| contiguous | adjacent storage | `vector` except `vector<bool>`, `array`, `string`, `string_view`, `span`, `valarray`, raw pointers |

Of the twelve headers the platform lists, only `<vector>`, `<array>`, and `<string>` give contiguous iterators. `deque` is random access but stored in blocks, so it is not contiguous. `queue`, `stack`, and `priority_queue` are adapters and expose no iterators at all. The unordered containers are forward only, so `--it` does not compile on them. C++20 ranges also let the end be a sentinel of a different type from the iterator, such as `std::unreachable_sentinel` or `std::default_sentinel`, which is what makes `std::ranges::for_each(arr, f)` and counted or null-terminated ranges work.

## Iterator invalidation

Any operation that moves elements to new addresses or destroys them leaves iterators, pointers, and references dangling, and using one is undefined behavior. For `std::vector`, any insertion that would push `size()` past `capacity()` reallocates and invalidates everything; below capacity, only iterators at or after the insertion point die. `erase` invalidates from the erased element to `end()`, and returns the iterator to the element after, which is the revalidation idiom: `it = v.erase(it)`. A `reserve` followed by at most that many `push_back` calls keeps iterators valid, which is the difference between `v.push_back(3)` after `auto b = v.begin()` on a two-element vector printing junk, and the same after `v.reserve(3)` printing `1`. For `deque`, pushing at either end invalidates iterators but not pointers or references to elements, and inserting in the middle invalidates everything. For `list`, `forward_list`, `map`, and `set`, only the erased element's iterator is invalidated and insertion invalidates nothing. For the unordered containers, an insertion that triggers a rehash invalidates every iterator but no pointer or reference to an element. Mutating a container inside a range-based for over it is the same bug with the iterators hidden.

```cpp
for (auto it = v.begin(); it != v.end(); ) {
    if (pred(*it)) it = v.erase(it);           // erase returns the next element
    else ++it;
}
std::erase_if(v, pred);                        // C++20, the same in one call
for (auto num : v) if (num % 2 == 0) v.push_back(num + 1);   // UB: loop iterators invalidated
```

## Algorithms and callables

The algorithms in `<algorithm>` operate on iterator pairs and split informally into inspectors such as `find`, `find_if`, and `count`, mutators such as `sort` and `shuffle`, and facilitators such as comparators and `transform`. `std::find(begin, end, value)` returns the first match or `end`, so always compare against `end()` before dereferencing. `std::find_if` takes any callable that accepts one element and returns bool. `std::sort(begin, end, comp)` takes a comparator that returns true when the first argument must come before the second; `std::greater{}` with C++17 deduction gives a descending sort. `std::for_each(begin, end, fn)` calls `fn` on every element, by reference if the function takes one, ignores the return value, and states intent better than a hand loop; partial ranges come from `std::next(arr.begin())`, and the ranges form takes the container directly. Most algorithms make no promise about left-to-right processing order; only `for_each`, `copy`, `copy_backward`, `move`, and `move_backward` do, so a stateful callable that depends on order needs one of those.

A callable is anything that can be invoked with the element: a function name, which decays to a function pointer, an explicit function pointer `&func`, a function object such as `FuncObj()`, or a lambda. Taking the address of a temporary, `&FuncObj()`, is not one of them: a prvalue has no address and the call does not compile. A non-static member function is a different shape again; `&Getcracked::memfunc` needs an object as its first argument, and the C++17 utility that calls every callable uniformly, including pointers to members with the object supplied separately, is `std::invoke(op, args...)`. `std::apply` unpacks a tuple into a call, `std::visit` dispatches on a variant, and `std::is_invocable` only asks whether a call would compile. See [classes.md](classes.md) for the pointer-to-member syntax.

`std::transform` has a unary form, one input range and one output, and a binary form, two input ranges and one output, that takes only the beginning of the second range and assumes it is at least as long as the first. With `values` of three elements and `otherValues` of two, the third step reads one past the end of `otherValues`, which is undefined behavior regardless of what `back_inserter` on the result reports. `std::back_inserter(resultValues)` is an output iterator whose assignment calls `push_back`, so the destination needs no pre-sizing.

```cpp
std::vector<int> values{ 1, 2, 3 }, other{ 1, 2 }, result;
std::transform(values.begin(), values.end(), other.begin(), std::back_inserter(result),
               [](int a, int b) { return a + b; });   // UB: other has only two elements
```

## Complexity versus runtime on small data

`std::find` is linear and `std::lower_bound` is logarithmic, but on a six-element vector the linear scan is the faster one. The binary search pays for a division, a data-dependent branch per step, and a comparison the branch predictor cannot learn, while the scan is a predictable loop over one cache line that stops at the third element. Asymptotic complexity describes growth, not the constant, and for small n the constant wins; the crossover is typically in the tens of elements. The same reasoning is why `std::sort` falls back to insertion sort on short ranges. `std::lower_bound` also requires the range to be partitioned with respect to the key, which a sorted range is, and it does a binary search by `std::advance` and `std::distance`, so on a non-random-access container it is logarithmic in comparisons but linear in steps. That is why `std::set` has its own `lower_bound` member; see [associative_containers.md](associative_containers.md).

## Errors and pitfalls

- **Undefined behavior: dereferencing `end()`**, or the result of `find` without checking it against `end()`.
- **Undefined behavior: `&arr[std::size(arr)]`.** Use `data() + size()` for the past-the-end pointer.
- **Undefined behavior: using an iterator after the container reallocated or erased.** `push_back` past capacity on a vector, `erase` anywhere, insertion into a `deque`, a rehash in an unordered container.
- **Undefined behavior: inserting into a container inside a range-based for over it.**
- **Undefined behavior: the binary `std::transform` with a shorter second range.** It only takes the second range's beginning.
- **Invalid: `&FuncObj()` as a callable.** A temporary has no address; pass `FuncObj()` by value.
- **Invalid: `std::sort` on a `std::list` or a forward-only container.** It needs random access; use the member `sort`.
- **Invalid: `--it` on an unordered container's iterator.** Forward iterators only.
- **Logical error: `p < end` in a generic loop.** Only random-access iterators are relationally comparable.
- **Logical error: `std::lower_bound` on a `std::set`.** Correct answer, linear time; use `s.lower_bound(x)`.
- **Logical error: relying on processing order in an algorithm other than `for_each`, `copy`, or `move`.**
- **Logical error: assuming `lower_bound` beats `find` on a handful of elements.** The constant factor wins at small n.

## Additional syntax examples

```cpp
auto found{ std::find(arr.begin(), arr.end(), 5) };
if (found != arr.end()) *found = 0;
auto it{ std::find_if(names.begin(), names.end(), [](std::string_view s) { return s.contains("nut"); }) };
std::count_if(v.begin(), v.end(), [](int x) { return x % 2 == 0; });
std::sort(v.begin(), v.end(), std::greater{});
std::for_each(std::next(v.begin()), v.end(), [](int& x) { x *= 2; });
std::ranges::for_each(v, print);
std::transform(a.begin(), a.end(), std::back_inserter(out), [](int x) { return x * x; });
std::invoke(&Getcracked::memfunc, obj, 42);   // member function through a uniform call
std::iterator_traits<decltype(it)>::iterator_category{};
static_assert(std::contiguous_iterator<std::vector<int>::iterator>);
```

## Interview Q&A

### Which standard containers give contiguous iterators?

`vector` (not `vector<bool>`), `array`, `string`, plus `string_view`, `span`, `valarray`, and raw pointers. `deque` is random access but block-allocated. The adapters `queue`, `stack`, and `priority_queue` have no iterators. Node-based and hashed containers are bidirectional or forward.

### A custom `for_each(begin, end, pred)` is called with `func`, `&func`, `&FuncObj()`, and `FuncObj()`. Which fails?

`&FuncObj()`. A function name decays to a pointer, so the first two are the same thing, and a function object by value is callable. A temporary is a prvalue with no address, so taking it is a compile error.

### Which C++17 utility lets a generic `foreach` accept a pointer to a non-static member function plus an object?

`std::invoke`. It calls functions, function objects, lambdas, and pointers to members uniformly, supplying the object as the first argument for members. `std::apply` unpacks a tuple, `std::visit` dispatches on a variant, and `std::is_invocable` is a trait, not a call.

### Binary `std::transform` over a three-element and a two-element vector into a `back_inserter`. Result?

Undefined behavior. The binary form takes only the beginning of the second range and reads three elements from it. The output size is not the question; the third read is past the end.

### `std::find` versus `std::lower_bound` on a six-element vector: which is faster?

`std::find`. Logarithmic beats linear only when n is large enough for the extra work per step of the binary search, the division and the unpredictable branch, to be repaid. On a few elements the predictable scan over one cache line wins.

### What does `v.push_back(3)` do to an iterator taken before it, and how does `reserve` change the answer?

If the push exceeds capacity, the vector reallocates and every iterator, pointer, and reference dangles, so dereferencing prints junk and is UB. After `v.reserve(3)` the same push stays inside capacity, nothing moves, and the iterator still points at the first element.

### Why do `std::list` and `std::forward_list` have their own `sort`?

`std::sort` requires random-access iterators for its partitioning and introsort fallbacks. A linked list is bidirectional or forward only, so the algorithm cannot be instantiated; the member is a merge sort that relinks nodes.

## Practice history

### Reading

- 13/09/2026: learncpp 18.2 (introduction to iterators), 18.3 (introduction to standard library algorithms). The Medium guides on iterators and vectors returned 403 and were not read; the category table and invalidation rules above are from the standard. Bo Qian iterator and algorithm videos and the CppCon 105 algorithms talk not watched.

### Questions (getcracked)

- Per platform record, rescraped 13/09/2026. STL Algorithms: Call it. (`&FuncObj()` takes the address of a temporary) ok, Call it, improved. (`std::invoke`) ok, Removing the polymorphic (filed in [inheritance.md](inheritance.md)) ok, Zip it 3 (binary `transform` reads past the shorter range, UB) ok; Get it for me quick! (`find` beats `lower_bound` on six elements) wrong first attempt, retest in a week. Iterator Categories: Side-by-side (contiguous: vector, array, string, answer `1, 4, 6`) wrong first attempt, retest in a week.
- Anki: contiguous = vector, array, string, span, string_view; deque is random access not contiguous; adapters have no iterators; unordered containers are forward only; binary `transform` trusts the second range's length; `&Temp()` is not a callable; `std::invoke` handles pointers to members; `find` beats `lower_bound` on tiny ranges; `it = v.erase(it)`.

<!-- gc-questions:start -->

## Related getcracked questions

Pulled from the Beginner C++ progress tree. ✓ answered correctly, ✗ attempted and missed, ○ not attempted yet. Regenerate with `python3 cpp/tools/gc_links.py` after re-scraping.

### Iterator Categories
- ✗ [Side-by-side](https://getcracked.io/question/1103) — Hard

### STL Algorithms
- ✓ [Call it, improved.](https://getcracked.io/question/950) — Cooked
- ✓ [Call it.](https://getcracked.io/question/949) — Easy
- ✗ [Get it for me quick!](https://getcracked.io/question/1437) — Easy
- ✓ [Removing the polymorphic](https://getcracked.io/question/1213) — Medium
- ✓ [Zip it 3](https://getcracked.io/question/1069) — Medium

<!-- gc-questions:end -->
