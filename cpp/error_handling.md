# Error Handling: optional, expected & Exceptions

## optional represents a value that may be absent

`std::optional<T>` contains either a T or no value. For ordinary object T, the contained value is stored within the optional; the wrapper does not need a separate heap allocation for it. T itself may allocate. Copying an optional copies its contained value when present, and moving it uses the contained type's move behavior.

An optional needs to represent whether it is engaged, so its size can exceed sizeof(T). Common implementations use eight bytes for optional<int> and sixteen for optional<double>, but these are measurements rather than standard layout guarantees.

Default construction or `std::nullopt` creates an empty optional. A value initializer, class template argument deduction, `std::make_optional`, or `std::in_place` can construct an engaged one. In-place construction passes arguments directly to T's constructor and can avoid a separate temporary.

```cpp
std::optional<std::string> find_user(int id)
{
    if (id == 42) return "vedant";
    return std::nullopt;
}

if (auto user = find_user(42)) {
    std::cout << *user;         // The condition established that a value exists.
}
```

`has_value()` and boolean conversion test presence. `reset()` and assignment of nullopt destroy a present value and leave the optional empty. `emplace(args...)` destroys an old value, if any, and constructs a replacement. Swap exchanges the states and values under the type's requirements.

Comparisons can compare contained values or compare against nullopt. In ordering comparisons, an empty optional orders before an engaged optional. That is a library rule, not a judgment about the application's meaning of absence.

## Optional access and API choices

Dereference and arrow require a value to be present. Through C++23, violating that precondition has undefined behavior. C++26 library hardening can diagnose some precondition violations on hardened implementations; it does not make unchecked access a portable recovery mechanism.

`value()` checks presence and throws `std::bad_optional_access` if empty. `value_or(fallback)` returns the contained value or the fallback. It avoids the empty-access exception, but copying, converting, or evaluating the fallback can still throw. The fallback expression is evaluated as an ordinary function argument even when the optional is engaged.

Use optional when absence has a clear meaning, such as a lookup miss or an omitted value. If callers need a reason for failure, use a richer result such as expected. An optional value parameter can accept literals naturally, but may copy expensive values; an overload or a borrowing pointer can be more appropriate in some interfaces.

Through C++23, optional references are not supported; use a pointer or a reference wrapper when borrowing is needed. C++26 introduces `optional<T&>` with reference semantics, so do not apply the ordinary owned-value explanation to that specialization. See the [current optional specification](https://eel.is/c++draft/optional).

`optional<bool>` has three meaningful states: absent, false, and true. Its boolean conversion checks presence, not the stored bool. Similarly, optional<T*> can distinguish absence from an explicitly stored null pointer. Use these forms only when the extra state is intentional and clearly explained.

## transform, and_then, and or_else

C++23 adds operations that compose optional-producing code. `transform(f)` invokes f on the contained value and wraps its result when present. `and_then(f)` expects f to return an optional already and returns that optional result without another wrapper. `or_else(f)` supplies an alternative when empty.

```cpp
std::optional<int> divide(int a, int b)
{
    if (b == 0) return std::nullopt;
    return a / b;              // Inputs must also avoid signed division overflow.
}
std::optional<int> start = 5;
auto nested = start.transform([](int x) { return divide(x, 0); });
auto flat = start.and_then([](int x) { return divide(x, 0); });
```

Nested has type optional<optional<int>>: its outer layer is present because the callable ran, but its inner layer is empty. Flat is an empty optional<int>. `has_value()` reports the state of the layer it is called on; it is not lying about an inner failure.

## expected represents a result or an error

C++23's `std::expected<T, E>` holds either a success value or an error value. It has no ordinary empty third state. `expected<void, E>` represents success without a payload. Default construction creates a successful value-initialized T when that operation is available.

Construct success from a value or with `std::in_place`. Construct an error with `std::unexpected(error)` or the `std::unexpect` tag. The distinction allows the same underlying type to be used on both sides without guessing whether a value means success or failure.

`operator*` requires success; `error()` requires failure. Check the state before using either unchecked accessor. `value()` throws `std::bad_expected_access<E>` on failure, while `value_or` supplies a fallback. `error_or` supplies an error-side fallback in C++23; it was included with the [expected additions in P2505R5](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2022/p2505r5.html). Accessing the held value or error through a mutable expected can modify it in place.

T may be void or an eligible object type, but cannot be a reference, an array, a function, or certain library tag/error-wrapper types. E also has type restrictions. An expected can itself be the value type of another expected, so nested expected types are permitted. See the [expected type requirements](https://timsong-cpp.github.io/cppwp/n4950/expected.object.general).

Expected supports `and_then`, `transform`, `or_else`, and `transform_error`. The first two compose successful results; the latter two recover from or transform errors. As with optional, use and_then when the callable already returns the wrapper.

## Parsing with expected

A parse result can carry a useful error without throwing for ordinary malformed input. `std::from_chars` reports both a status and the position where parsing stopped. If the contract requires the entire input to be an integer, check both.

```cpp
std::expected<int, std::string> parse_int(std::string_view input)
{
    if (input.empty()) return std::unexpected("empty input");
    int value{};
    auto end = input.data() + input.size();
    auto [ptr, ec] = std::from_chars(input.data(), end, value);
    if (ec == std::errc::invalid_argument)
        return std::unexpected("invalid integer");
    if (ec == std::errc::result_out_of_range)
        return std::unexpected("integer out of range");
    if (ptr != end)
        return std::unexpected("trailing characters");
    return value;
}
```

This function is not marked noexcept because constructing a string error can allocate and throw. For a genuinely allocation-free error representation, an enum or another small value type can be appropriate. Expected makes error propagation explicit, but the operations on T and E still determine its costs and exception behavior.

## Exceptions and handler matching

Exceptions transfer control to a matching handler and can propagate through callers that do not handle them. This is useful when local recovery is impossible or a constructor cannot establish its invariant. Throw meaningful exception objects, generally from a hierarchy based on `std::exception`, so handlers can inspect `what()`.

Handlers are tested in order. Matching is more restricted than ordinary overload conversion: throwing int does not match catch(double), although specified class-base and pointer conversions are allowed. Catch class exceptions by const reference to avoid a handler copy and preserve polymorphic information. Put derived handlers before base handlers. Catch-all must be last; putting it first is a compile-time error.

After a handler finishes normally, execution continues after the complete try/catch statement. A bare `throw;` inside an active handler rethrows the original exception. `throw e;` creates a new exception from e's static type and can slice a derived exception caught through a base reference. The [handler rules](https://timsong-cpp.github.io/cppwp/n4950/except.handle) specify the permitted matching conversions.

The exception object has storage managed by the exception machinery, rather than being an ordinary local that dies when its throwing frame is left. Its construction can involve a copy or move, or direct construction from a prvalue. Do not assume every throw physically copies an object or that a pointer inside the exception keeps its target alive.

## Stack unwinding and RAII

When an exception propagates to a handler, fully constructed automatic objects on the exited path are destroyed in reverse construction order. The abandoned functions do not execute their remaining statements or ordinary returns. Resource Acquisition Is Initialization (RAII) makes this useful by attaching resource release to object destruction.

If a constructor fails, already-constructed bases and members are destroyed, but the incomplete object's own destructor is not run in the ordinary non-delegating case. Put resources in RAII members instead of relying on cleanup code in a destructor that may never be entered.

A function try block can catch failures from a constructor's member-initializer list as well as its body. A constructor handler cannot turn the failed construction into success by falling off its end; it implicitly rethrows. Accessing the failed object's members or bases in that handler is invalid.

An advanced return-path case occurs when a result object has been constructed and a local destructor then throws during return cleanup. The return object must also be destroyed as part of the specified cleanup. Track completed construction and destruction order rather than treating the result as already immune in the caller. This is specified in [constructor/destructor exception handling](https://timsong-cpp.github.io/cppwp/n4950/except.ctor). Historical compiler observations in the practice log need their exact versions and snippets before being treated as current conformance claims.

## Destructors, noexcept, and uncaught exceptions

Destructors normally have a non-throwing exception specification, but the implicit specification depends on base and member destructors. A destructor can also be explicitly declared `noexcept(false)`. An exception escaping a noexcept function calls `std::terminate`.

Even a potentially throwing destructor causes terminate if it exits by throwing while another exception is already unwinding the stack. Design destructors not to let exceptions escape; use an explicit operation to report a cleanup failure when callers must handle it.

If no handler is found, terminate is called. Whether unwinding occurs first is implementation-defined, so an uncaught exception does not guarantee local cleanup. The default terminate handler calls abort. A top-level handler can implement an application's reporting policy, but there is no universal rule to remove it in debug builds or to continue after every failure.

## Cost model and choosing an error channel

Many implementations store tables that tell the runtime where exception handlers are and which objects need cleanup. When an exception is thrown, the runtime uses those tables to find a handler and unwind the stack. This avoids an explicit exception check after each successful call, which is the basis of the phrase “zero-cost exceptions.” Code size, optimization constraints, register use, and instruction-cache effects can still cost something on the success path.

Throwing often involves exception-object storage, runtime searches, and cleanup, with costs that depend on the implementation and workload. There is no portable fixed microsecond cost. Expected uses ordinary branches and returns, but its payloads and error construction can allocate or perform other expensive work.

Use optional for meaningful absence, expected for an explicit value-or-error contract, and exceptions where propagation to a more distant handler fits the application. In latency-sensitive code, evaluate error frequency, allocation, propagation depth, and project policy rather than declaring one mechanism universally cheapest.

## Errors and pitfalls

Distinguish an empty-access precondition violation from the checked exception thrown by value(). Do not label value_or infallible. Check constructor cleanup separately from destruction of a fully constructed object. Do not infer noexcept from the use of expected, especially when its error payload is a string.

## Additional syntax examples

These are independent syntax sketches, including deliberately invalid examples marked `CE` (compile error). They are not one compilable program.

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
std::expected<int, std::string> convertToInt(const std::string& input)
{
    int value{};
    auto [ptr, ec] = std::from_chars(input.data(), input.data() + input.size(), value);
    if (ec == std::errc() && ptr == input.data() + input.size()) return value;
    if (ec == std::errc()) return std::unexpected("trailing characters");
    if (ec == std::errc::invalid_argument)        return std::unexpected("invalid number format");
    if (ec == std::errc::result_out_of_range)     return std::unexpected("number out of range");
    return std::unexpected("unknown conversion error");
}

auto r = convertToInt("11111111111111111");
if (r) std::cout << *r;
else   std::cout << r.error();                    // error() UB if r has a value — check first

std::expected<void, std::string> performAction(bool ok)
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
// A destructor is normally noexcept, subject to its bases/members; an escaping throw then terminates.
// at normal return: fires AFTER return expr; return value destroyed, caller gets exception
```

## Interview Q&A

### When would you use optional instead of expected?

Optional represents a value that may be absent when absence has a clear meaning, such as a lookup miss. Expected represents either a success value or a reason for failure. I use expected when the caller needs to distinguish errors or report what went wrong.

### How do dereference, value, and value_or differ for optional?

Dereference requires that a value is present. Value checks and throws bad_optional_access when empty. Value_or returns a value or a fallback, but evaluating the fallback or copying the result can still throw. I choose based on the contract I want at the call site.

### Why use and_then instead of transform for a function returning optional?

Transform wraps the callable's result, so an optional-returning callable creates a nested optional. And_then expects that wrapper already and returns it directly. That lets an empty inner result propagate as the empty result of the whole operation.

### What happens when a constructor throws?

The object has not completed construction, so its own destructor normally does not run. Its fully constructed bases and members are cleaned up. That is why I put owned resources in RAII members whose destructors can run independently during failed construction.

### How is throw different from throw e inside a handler?

A bare throw rethrows the original exception object. Throwing e creates a new exception from the expression's static type, so it can slice a derived exception caught as a base reference. I use bare throw when I want to propagate the same failure.

### Can a destructor throw?

The language permits a potentially throwing destructor, but it is usually a poor interface. Escaping a noexcept destructor terminates, and throwing while another exception unwinds also terminates. I keep destructor cleanup non-throwing and provide an explicit checked operation when failure must be reported.

### Are exceptions free when nothing is thrown?

Many implementations use stored tables to find handlers and cleanup code when an exception is thrown. That avoids an explicit exception check after every successful call, which is where the zero-cost name comes from. The tables take space, and code layout and optimization effects can still matter. I measure the relevant workload rather than assuming there is no cost.

### Does expected make a function noexcept?

No. Constructing or moving its value and error types can throw, and a string error may allocate. Expected controls how the ordinary result is represented, not whether every operation in the function is non-throwing.

## Practice history

The entries below preserve the original practice record. Compiler-conformance observations are historical and require the original snippet, version, and flags before being generalized. The old switch wording is also too broad: some trivial declarations may be bypassed, but a declaration without an explicit initializer can still perform nontrivial initialization.

### Questions (getcracked) / Quiz log

| Date | Question | Result | Reason |
|---|---|---|---|
| 01/09/2026 | "So close to unwinding" (bcad) | MISS (said cbd) | Thought unwinding skips remaining dtors (it RUNS them); missed that the pending return object is destroyed by unwinding, reverse-construction order ([except.ctor]¶2). Bonus: gcc/clang/MSVC all non-conforming (bacd/bad/bad). Anki: "ctor'd return obj + local dtor throws → ?" / "unwinding destroys return obj too, reverse construction order" |
| 01/09/2026 | transform on callable returning optional | MISS → retested clean same day (quiz #2 Q8) | transform WRAPS (→ optional<optional<int>>, outer engaged, has_value() true despite inner failure); and_then FLATTENS. Anki: "callable returns optional<T> → which monadic op?" / "and_then (transform double-wraps)" |
| 01/09/2026 | Claude quiz #2 Q1: catch(...) listed first | HALF | Said "catches everything" — it's a CE: catch-all must be LAST ([except.handle]). Anki: "catch(...) before other handlers → ?" / "CE (vs base-before-derived: compiles, dead code)" |
| 01/09/2026 | Claude quiz #2 Q2: uncaught exception + RAII | HALF | Got terminate; missed that unwinding is implementation-defined when uncaught → dtors NOT guaranteed (gcc/clang don't unwind). Anki: "uncaught throw — do local dtors run?" / "impl-defined; typically no (crash scene preserved)" |
| 01/09/2026 | Claude quiz #2 Q4: switch decl/init + skipped assignment | HALF | Right case; said "can't default-init" (backwards: default-init/declaration IS allowed, initialization is the CE) + called skipped-assignment read "garbage" (it's UB — REPEAT of standing trap line) |

<!-- gc-questions:start -->

## Related getcracked questions

Pulled from the Beginner C++ progress tree. ✓ answered correctly, ✗ attempted and missed, ○ not attempted yet. Regenerate with `python3 cpp/tools/gc_links.py` after re-scraping.

### std::exception and Stack Unwinding
- ✓ [Catch me if you can!](https://getcracked.io/question/965) — Easy
- ✓ [Hey, catch!](https://getcracked.io/question/993) — Medium
- ✗ [So close to unwinding.](https://getcracked.io/question/1008) — Cracked

### std::optional and nullopt
- ✗ [Divided Result](https://getcracked.io/question/2054) — Hard

<!-- gc-questions:end -->
