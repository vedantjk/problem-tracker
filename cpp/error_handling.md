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
| 01/09/2026 | transform on callable returning optional | MISS → retested clean same day (quiz #2 Q8) | transform WRAPS (→ optional<optional<int>>, outer engaged, has_value() true despite inner failure); and_then FLATTENS. Anki: "callable returns optional<T> → which monadic op?" / "and_then (transform double-wraps)" |
| 01/09/2026 | Claude quiz #2 Q1: catch(...) listed first | HALF | Said "catches everything" — it's a CE: catch-all must be LAST ([except.handle]). Anki: "catch(...) before other handlers → ?" / "CE (vs base-before-derived: compiles, dead code)" |
| 01/09/2026 | Claude quiz #2 Q2: uncaught exception + RAII | HALF | Got terminate; missed that unwinding is implementation-defined when uncaught → dtors NOT guaranteed (gcc/clang don't unwind). Anki: "uncaught throw — do local dtors run?" / "impl-defined; typically no (crash scene preserved)" |
| 01/09/2026 | Claude quiz #2 Q4: switch decl/init + skipped assignment | HALF | Right case; said "can't default-init" (backwards: default-init/declaration IS allowed, initialization is the CE) + called skipped-assignment read "garbage" (it's UB — REPEAT of standing trap line) |

## Exceptions (learncpp 27.1-27.7, read + quizzed 01/09)
- **Why** (27.1): return codes weld error handling into control flow (cryptic values, one-return-slot, check-every-call), and ctors can't return codes at all. Exceptions decouple.
- **Matching** (27.2): `throw` anything. Handlers match with **no conversions** (int won't match catch(double)) except derived→base and adding const. Catch class types `const&` (no copy, no slice). After a catch body, execution resumes after the LAST catch. `catch (...)` must be **last — CE otherwise** (contrast: base-before-derived compiles, derived handler just becomes dead code + warning).
- **Unwinding** (27.3): search first (current try → caller → up; nothing destroyed during search), then unwind frame-by-frame: locals' dtors run in reverse construction order, frames are *abandoned* (no returns execute). **[except.ctor]¶2**: everything constructed-but-not-destroyed since the try is destroyed — including a pending RETURN OBJECT (constructed before locals are torn down; on the normal path it's the caller's property and never destroyed by the callee) — all in reverse construction order. gc "bcad" question = exactly this; gcc/clang/MSVC all non-conforming (bacd/bad/bad), so Compiler Explorer can't settle it.
- **Uncaught** (27.4): no handler → `std::terminate` → abort. **Whether the stack unwinds first is implementation-defined** — gcc/clang don't, preserving the crash scene; RAII cleanup is only guaranteed if SOME handler exists. Hence catch-all wrapping main in release, compiled out in debug.
- **Exception classes** (27.5): ctor throws → constructed MEMBERS destructed, class dtor never runs → resources belong in RAII members, not raw + cleanup-in-dtor (that code is unreachable on the throwing path). Thrown object is COPIED to storage outside the stack (must be copyable, no pointers to locals). Std hierarchy: everything : `std::exception`, virtual `what()`; derive from `runtime_error` (stores the string) or override `what()` `noexcept override`.
- **Rethrow** (27.6): bare `throw;` re-propagates the original object; `throw e;` copy-inits from the static type → **slices** a Derived caught as Base&.
- **Function try blocks** (27.7): only real use = catching member-init-list throws. Ctor catch can't swallow — end-of-catch implicitly rethrows; touching the failed object's members = UB.
- **Throwing destructors** (session extras, verified): dtors are implicitly `noexcept` since C++11 — escape = terminate (gcc even warns `-Wterminate`). With `noexcept(false)`: at a normal return the dtor throw fires AFTER the return expression is evaluated — the built return value is destroyed and the caller gets the exception instead. Dtor throwing while another exception unwinds = terminate, no appeal → **destructors never throw**.
- **Cost model** (not in learncpp, interview-critical): table-driven "zero-cost" unwinding — happy path executes zero extra instructions; compiler emits `.eh_frame` tables mapping return addresses → frame layouts + landing pads (dtor-running cleanup stubs). A throw = two-phase table walk (search, then unwind) + exception-object allocation → microseconds. Asymmetry defines HFT policy: fine for rare events, banned on hot paths (`-fno-exceptions` shops); `std::expected` is the hot-path answer.

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

// exceptions — the working set
try { throw Derived{}; }
catch (const Derived& d) { }   // derived BEFORE base or it's dead code
catch (const Base& b)    { }
catch (...)              { }   // must be LAST (CE otherwise)

catch (Base& b)
{
    log(b);
    throw;        // bare: original object, no copy, no slice (throw b; slices)
}

struct B
{
    A a;
    B(int x)
    try : a{ x } { }                          // covers init list + body
    catch (const std::exception& e)
    {
        std::cerr << e.what();                // touching this->a here = UB
    }                                         // falling off end: implicit rethrow
};

~Loud() noexcept(false) { throw std::runtime_error{"boom"}; }
// default dtor = noexcept → throw would terminate (-Wterminate)
// at normal return: fires AFTER return expr; return value destroyed, caller gets exception
```

## Traps / interview one-liners
- "`*o` on empty is UB; `o.value()` throws — know which one you're writing."
- "Value semantics: optional copies its T. sizeof(optional<double>) = 16 — the bool costs a whole alignment slot."
- "Empty compares less than everything engaged."
- "optional answers IF it failed, expected/exceptions answer WHY."
- "expected: value_or exists for T; error() is UB when engaged — the access tiers exist on BOTH sides."
- "expected's error path is a plain return — predictable cost, no unwinder; why hot paths prefer it to throw."
- "No optional references until C++26; optional<bool> and optional<T*> are smells."
