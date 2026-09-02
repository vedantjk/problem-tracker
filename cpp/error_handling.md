# Error Handling (std::optional · exceptions)

## std::optional — core model (learncpp + cppstories, read 01/09)
- Vocabulary type (family: variant, any, string_view): "a T that might not be there," **value semantics** — it *contains* the T inline, no heap, assignment copies. sizeof = T + bool + padding: `optional<int>` = 8, `optional<double>` = 16 (alignment doubles the cost).
- Create: `optional<int> o;` / `= std::nullopt` (empty) · `optional<int> o{5}` · CTAD `optional o(10)` · `make_optional<T>(args)` · **in-place**: `optional<Complex> o{std::in_place, 3.0, 4.0}` (constructs inside, no temporary — for non-movable/expensive types).
- Check: `if (o)` (bool conversion) or `o.has_value()`.
- Access, three safety tiers:
  1. `*o` / `o->` — **UB if empty** (like dereferencing end(); no check)
  2. `o.value()` — throws `std::bad_optional_access` if empty
  3. `o.value_or(fallback)` — never fails
- Modify: `o.emplace(args)` (destroys old value if any, constructs new), `o.reset()` (destroys → empty), `o = nullopt`, `swap`.
- Comparisons: `o == 10` compares the contained value; `o == std::nullopt` checks emptiness; relational ops work and **empty < any engaged value**.
- Optional parameters: `void f(std::optional<int> id = std::nullopt)` — accepts rvalues (unlike const T*). But for expensive T prefer `const T*` or an overload — optional copies.
- **No `optional<T&>`** through C++23 (CE); C++26 adds it (P2988). `optional<T*>` is redundant (pointers already nullable), `optional<bool>` is a confusing tri-state — avoid both.
- When: "exactly one obvious reason for no value" — lookup miss, not-yet-loaded, optional input. NOT for error reporting (no room for a reason — that's `std::expected` (C++23) or exceptions).
- C++23 monadic ops: `and_then` / `transform` / `or_else` — chain without if-ladders.

## Exceptions (learncpp 27.1-27.7)
_(read 01/09; notes to be written after quiz — misses so far: gc "So close to unwinding" bcad question: thought unwinding skips remaining dtors + missed that the pending return object is destroyed by unwinding in reverse-construction order; [except.ctor]¶2. Note: gcc/clang/MSVC all non-conforming on it: bacd/bad/bad.)_

## Compile errors vs UB
```cpp
std::optional<int&> r;        // CE through C++23 (C++26: ok)
std::optional<int> e;         // empty
*e;                           // UB — no check, like *end()
e.value();                    // throws std::bad_optional_access (NOT UB)
int v = e.value_or(42);       // fine, v = 42
```

## Syntax anchors
```cpp
#include <optional>

std::optional<std::string> find_user(int id)
{
    if (id == 42) return "vedant";
    return std::nullopt;
}

if (auto u = find_user(42))            // engaged check + scope in one
    std::cout << *u;                   // safe: checked

std::optional<std::vector<int>> ov{ std::in_place, {1, 2, 3} };  // built in place
ov.emplace(5, 0);                      // destroy old, construct vector(5,0)
ov.reset();                            // destroy → empty

// C++23 monadic chain
auto len = find_user(42)
    .transform([](const std::string& s) { return s.size(); })
    .value_or(0);
```

## Traps / interview one-liners
- "`*o` on empty is UB; `o.value()` throws — know which one you're writing."
- "Value semantics: optional copies its T. sizeof(optional<double>) = 16 — the bool costs a whole alignment slot."
- "Empty compares less than everything engaged."
- "optional answers IF it failed, expected/exceptions answer WHY."
- "No optional references until C++26; optional<bool> and optional<T*> are smells."
