# Tuple

## Core model
- Heterogeneous fixed-size value pack. Create: `std::tuple<int,float,bool> t{...}`, CTAD `std::tuple t{42, 3.14f, true}`, or `std::make_tuple(...)` (decays types).
- Access: `std::get<0>(t)` by index (returns reference, assignable), `std::get<float>(t)` by type (only if that type appears exactly once). Index must be a compile-time constant.
- Unpack: structured bindings `auto [a,b,c] = t;` (new variables) vs `std::tie(a,b,c) = t;` (assigns into existing ones; `std::ignore` skips). tie also makes cheap lexicographic comparators: `return std::tie(x.a, x.b) < std::tie(y.a, y.b);`
- Compile-time introspection: `std::tuple_size_v<T>`, `std::tuple_element_t<I, T>`.
- `std::tuple_cat(t1, t2)` concatenates; `std::apply(f, t)` calls f with the elements as arguments (the idiomatic "iterate a tuple" via a fold inside).
- Comparison operators compare lexicographically.

## Compile errors vs UB
Compile-time failures (all template machinery, nothing deferred to runtime):
- `get<int>(t)` with two (or zero) int elements — ambiguous/absent type.
- `get<5>(t)` on a 3-tuple — index out of range is a compile error, never an exception.
- `auto [a,b] = three_tuple;` — structured-binding count must match exactly.
- `get<i>(t)` with a runtime `i` — index must be a constant expression; there is no runtime indexing at all.
- Comparing tuples of different sizes (or non-comparable element types).
- `std::tie(a, 5)` — tie takes lvalues only; can't tie a literal/temporary.

UB / dangling (the few runtime hazards):
- `auto&& t = std::forward_as_tuple(1, 2);` then using `get<0>(t)` — forward_as_tuple builds a tuple of references to the temporaries, which die at the end of the full expression; the tuple outliving them dangles. Safe only when consumed inside the same expression (its intended use: forwarding into a function).
- Same shape with `std::tie`/structured bindings over a reference into a dead object — the tuple never extends element lifetimes.
- Reading a moved-from tuple's elements: valid but unspecified values (not UB, just meaningless).

## Traps / interview one-liners
- "Return `{value, ok}`-style multiples as a struct with names when the API is public; tuple/structured bindings for local plumbing."
- "std::tie of references + operator< is the standard way to write multi-key comparators without bugs."
- "get<T> is a compile error if T is ambiguous or absent — no runtime lookup, it's all template machinery."
