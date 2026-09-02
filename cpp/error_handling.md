# Error Handling (std::optional · std::expected · exceptions)

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
- **transform vs and_then (gc question, 01/09 — MISSED)** — the nested-optional trap:
  - `transform(f)`: f returns a plain value; transform **wraps** it → callable returning `optional<int>` yields `optional<optional<int>>`. The OUTER layer is engaged whenever the callable ran at all, so `has_value()` lies about the inner failure.
  - `and_then(f)`: f must itself return an optional; and_then **flattens** (no extra wrap). Callable already returns optional → use and_then.
  ```cpp
  std::optional<int> safe_divide(int a, int b)
  { return b == 0 ? std::nullopt : std::optional{a / b}; }

  std::optional<int> opt{ 5 };
  auto r1 = opt.transform([](int x){ return safe_divide(x, 0); });
  // r1: optional<optional<int>> — ENGAGED outer, empty inner → r1.has_value() == true (!)
  auto r2 = opt.and_then([](int x){ return safe_divide(x, 0); });
  // r2: optional<int> — nullopt, as intended
  ```
  - Rule: callable returns T → transform; callable returns optional<T> → and_then. (Haskell fmap vs bind, if that helps it stick.)

## std::expected<T, E> — C++23 (cppstories, read 01/09)
- "optional with a reason": holds a T (success) **or** an E (error) — never both, never neither. The missing piece between `optional` (no why) and exceptions (costly why). Value semantics, inline storage like optional.
- Success: `expected<int, string> r{42};` default-ctor → T's default (0). Error: wrap it — `return std::unexpected("msg");` — or construct in place with the `std::unexpect` tag: `expected<int, string> e{std::unexpect, "err"}`. `std::in_place` tag for in-place T.
- Access mirrors optional's tiers, doubled:
  - value side: `*r` (UB if error) · `r.value()` (throws `std::bad_expected_access<E>` if error) · `r.value_or(dflt)`
  - error side: `r.error()` — **UB if it actually holds a value**; check `if (!r)` first. C++26 adds `error_or`.
  - both sides are mutable in place: `*r += 10;` `r.error() += " extended";`
- `expected<void, E>` is the "may fail, returns nothing" shape: `return {};` on success.
- Type rules: T can be void, not a reference (use `reference_wrapper`), not a C array, not expected itself. E must be a plain object type.
- Monadic quartet: `and_then` (callable returns expected — flattens, same rule as optional's!) · `transform` (callable returns plain T — wraps) · `or_else` (handle/replace the error) · `transform_error` (map E→E', e.g. errno → your enum). Same nested-wrapping trap as optional above.
- Canonical parse example: `std::from_chars` + map `std::errc` to messages — return `value` or `std::unexpected(reason)`.
- vs exceptions: error path is a normal return — no unwind tables in play, cost is symmetric and predictable → the error-handling style low-latency code prefers on hot paths.

## Questions (getcracked) / Quiz log
| Date | Question | Result | Reason |
|---|---|---|---|
| 01/09/2026 | "So close to unwinding" (bcad) | MISS (said cbd) | Thought unwinding skips remaining dtors (it RUNS them); missed that the pending return object is destroyed by unwinding, reverse-construction order ([except.ctor]¶2). Bonus: gcc/clang/MSVC all non-conforming (bacd/bad/bad). Anki: "ctor'd return obj + local dtor throws → ?" / "unwinding destroys return obj too, reverse construction order" |
| 01/09/2026 | transform on callable returning optional | MISS | transform WRAPS (→ optional<optional<int>>, outer engaged, has_value() true despite inner failure); and_then FLATTENS. Anki: "callable returns optional<T> → which monadic op?" / "and_then (transform double-wraps)" |

## Exceptions (learncpp 27.1-27.7)
_(read 01/09; notes to be written after quiz — misses tracked in the quiz log above.)_

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

// std::expected — parse with a reason
#include <expected>
#include <charconv>
std::expected<int, std::string> convertToInt(const std::string& input) noexcept
{
    int value{};
    auto [ptr, ec] = std::from_chars(input.data(), input.data() + input.size(), value);
    if (ec == std::errc())                        return value;
    if (ec == std::errc::invalid_argument)        return std::unexpected("invalid number format");
    if (ec == std::errc::result_out_of_range)     return std::unexpected("number out of range");
    return std::unexpected("unknown conversion error");
}

auto r = convertToInt("11111111111111111");
if (r) std::cout << *r;
else   std::cout << r.error();                    // error() UB if r has a value — check first

std::expected<void, std::string> performAction(bool ok) noexcept
{
    if (ok) return {};                            // void success
    return std::unexpected("action failed");
}
```

## Traps / interview one-liners
- "`*o` on empty is UB; `o.value()` throws — know which one you're writing."
- "Value semantics: optional copies its T. sizeof(optional<double>) = 16 — the bool costs a whole alignment slot."
- "Empty compares less than everything engaged."
- "optional answers IF it failed, expected/exceptions answer WHY."
- "expected: value_or exists for T; error() is UB when engaged — the access tiers exist on BOTH sides."
- "expected's error path is a plain return — predictable cost, no unwinder; why hot paths prefer it to throw."
- "No optional references until C++26; optional<bool> and optional<T*> are smells."
