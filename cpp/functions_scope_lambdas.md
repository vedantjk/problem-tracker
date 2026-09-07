# Functions, Scope & Lambdas

## Function calls and return values

A function call initializes parameters, transfers control to the function body, and eventually returns control or propagates an exception. The application binary interface (ABI) determines details such as argument registers, stack use, saved registers, and how results are returned. C++ does not specify a particular calling convention.

A function returns one result, but that result can be a named struct, pair, or tuple containing several values. Small aggregates may return in registers; their classification depends on the ABI and member types. On x86-64 System V, some small integer aggregates use `RAX` and `RDX`, while floating members can use different registers. Size alone does not decide the convention.

Function calls may also constrain optimization when the compiler cannot see or reason about the body. Inlining can expose optimization opportunities, at the cost of increased code size and possible instruction-cache pressure. Calls are not an absolute optimization barrier; whole-program analysis, visible definitions, and other information can let the compiler reason across them.

Flowing off the end of an ordinary non-void function other than main has undefined behavior. Writing a bare `return;` in such a function normally requires a diagnostic. Main is special: reaching its end returns zero. A void function can return without a value.

## Copy elision and NRVO

Since C++17, a same-type prvalue can initialize its destination directly. In `Widget make() { return Widget{}; }`, the returned object can be constructed directly in its final destination without requiring a move or copy between intermediate objects.

Named Return Value Optimization (NRVO) applies to a different pattern: `Widget w; return w;`. It is permitted, not guaranteed. When it does not occur, the return rules may move from the eligible local. Avoid adding `std::move(w)` merely to “help” NRVO, because that changes the eligible expression.

```cpp
Widget direct() { return Widget{}; }     // Guaranteed direct construction case.
Widget named() { Widget w; return w; }   // NRVO is optional.
```

Compiler options such as `-fno-elide-constructors` can expose optional elision, but they cannot turn the guaranteed C++17 prvalue case into a required copy. Return-by-value is often efficient; object construction and any real work inside the function still have costs.

## Recursion and the call stack

A recursive function needs a base case and a step that moves toward it. Without optimization, each active call needs its own frame and local state. Deep linear recursion can exhaust the available stack. The safe depth depends on frame size, compiler options, the operating system, and thread configuration; example crash depths are observations, not limits guaranteed by C++.

Recursion is often a natural fit for branching structures. A balanced tree may have logarithmic depth, but an arbitrary tree can be a linear chain. Check the worst-case depth instead of assuming that a tree is shallow.

Tail recursion places the recursive call where no further work is required after it. A compiler may replace it with iteration, but C++ does not guarantee tail-call optimization. A print or destructor that must run after the call can prevent a straightforward transformation.

Avoid modifying a variable while also reading it in an unsequenced sibling expression. `return sumTo(--n) + n;` is not fixed by C++17's parameter sequencing: the decrement in the argument and the sibling read remain unsequenced. Write `return sumTo(n - 1) + n;` when that matches the intended recurrence.

## Static-local memoization

A static local cache persists across calls. It can reduce repeated work, but it also shares state across every caller of that function. Initialization is thread-safe since C++11; later mutation is not automatically synchronized.

```cpp
int fibonacci(std::size_t n)
{
    static std::vector<int> results{0, 1};
    if (n < results.size()) return results[n];
    int a = fibonacci(n - 1);
    int b = fibonacci(n - 2);
    results.push_back(a + b);
    return results[n];
}
```

This sketch stores values from the base cases upward. Its int arithmetic eventually overflows, and concurrent calls can race on the vector. Those constraints belong in the explanation whenever using it as an example. For production code, choose a suitable range and synchronization or a caller-owned cache.

## Scope, storage duration, lifetime, and linkage

Scope determines where a name can be found. Storage duration determines how long storage is available. Object lifetime starts and ends according to initialization and destruction rules, so it is related to but not identical to storage duration. Linkage determines whether declarations in different scopes or translation units can name the same entity.

An ordinary local variable normally has block scope, automatic storage duration, and no linkage. A static local keeps block scope but has static storage duration. Namespace-scope names often have external linkage, with exceptions such as ordinary non-extern const objects and names given internal linkage. Anonymous namespaces are useful for translation-unit-local implementation details. C++20 modules also introduce module linkage.

An inner declaration can shadow an outer name. `::name` can select a global, but there is no comparable general syntax for retrieving an arbitrary shadowed local. Compiler warnings such as `-Wshadow` help reveal accidental hiding.

Cross-translation-unit dynamic initialization dependencies can access an object before its required initialization has happened. See [static initialization](initialization_deduction.md) for function-local static and constant-initialization alternatives.

## Lambdas and captures

A lambda expression creates an object of a unique unnamed closure class. Its call operator implements the body. Captures by value become stored state in that closure. This provides a useful struct-like model, but exact layout is not a portable guarantee.

A non-mutable ordinary lambda's call operator is const. Adding `mutable` allows it to modify its own by-value captures; it does not turn those copies into references to the originals.

```cpp
int ammo = 10;
auto copy = [ammo]() mutable { return --ammo; };
auto alias = [&ammo]() { return --ammo; };
```

The first lambda updates its stored copy. The second updates the external ammo variable and is only safe while that variable remains alive. Returning a lambda that captures a local by reference is a common dangling-reference bug.

Capture initializers run when the lambda expression is evaluated. Init-capture, such as `[p = std::move(owner)]`, can transfer an object into the closure. `[this]` captures the pointer; `[*this]` copies the object in C++17 and later. Implicit capture of this through `[=]` was deprecated in C++20.

A capture default (`[=]` or `[&]`) comes first. Explicit captures must follow the allowed combinations, and duplicate captures are invalid. Globals and static locals do not need ordinary captures.

Some uses of a local `constexpr` variable need only its compile-time value and do not require capture. Uses that need the actual object, such as taking its address in the example below, require capture; the formal term for such a use is odr-use.

```cpp
constexpr int limit = 10;
auto value = [] { return limit; };         // Uses the constant value without capture.
auto address = [&limit] { return &limit; }; // Needs the actual local object.
```

The reference-capturing lambda and any pointer it returns must not be used to access `limit` after that local object's lifetime ends.

A captureless closure is commonly one byte, a captured int commonly adds int-sized storage, and a reference capture often uses a pointer. The standard leaves reference-capture representation unspecified, so treat measured closure sizes as implementation observations. See the [lambda capture rules](https://timsong-cpp.github.io/cppwp/n4950/expr.prim.lambda.capture).

## Choosing a callable interface

A function pointer is simple and can receive a suitable captureless lambda. A capturing lambda needs its state preserved, so it cannot use that conversion. Unary plus can force the function-pointer conversion for a suitable captureless lambda.

A template callable parameter, including a C++20 abbreviated template using `auto`, preserves the concrete type and often gives the optimizer visibility. A `const F&` parameter cannot call a mutable-only call operator, so choose the parameter form according to the intended callable contract.

`std::function` erases the concrete callable type behind a uniform interface. It may allocate and commonly uses indirect dispatch, although allocation and optimization depend on the implementation and context. Calling an empty wrapper throws `std::bad_function_call`. A moved-from wrapper is valid with an unspecified value; do not assume every moved-from wrapper is empty.

A generic lambda with auto parameters has a templated call operator. A static local inside it is separate for each relevant specialization. Since C++17, suitable lambda call operators can be implicitly constexpr. C++23 allows the parenless `[] -> int { ... }` form.

## Tuples and structured bindings

A tuple groups heterogeneous values. Construct it using explicit template arguments, class template argument deduction, or `std::make_tuple`. Make_tuple normally decays its arguments, with special handling for reference wrappers.

`std::get<I>` uses a compile-time index. `std::get<T>` requires exactly one element of that type. An invalid index or missing/duplicate type is a compile-time error, not a bounds exception. Structured bindings introduce names for the elements; `std::tie` assigns into existing variables and can use `std::ignore` to discard a result.

`tuple_size`, `tuple_element`, `tuple_cat`, and `std::apply` support inspection, composition, and calling a function with tuple elements. Tuple comparison is lexicographic. A comparison using `std::tie(x.a, x.b)` is a concise way to express ordering by two keys.

A tuple containing references does not generally extend the referents' lifetimes. In particular, storing the result of `std::forward_as_tuple` with temporaries can leave dangling references after the statement. A named result struct is often clearer than a tuple in a public interface.

## Errors and pitfalls

Check lifetime before returning references or closures, and check maximum recursion depth before choosing recursion. Mismatched inline definitions are an ODR violation with no diagnostic required, rather than a useful runtime “UB experiment.” Distinguish empty-callable exceptions from null-function-pointer undefined behavior.

## Additional syntax examples

These are independent syntax sketches, including deliberately invalid examples marked `CE` (compile error). They are not one compilable program.

```cpp
auto l = [captures](params) -> ret { body; };

// 4 ways to receive a callable:
void repeat1(int n, const std::function<void(int)>& fn); // Type-erased; allocation and dispatch costs depend on the implementation.
template <typename T> void repeat2(int n, const T& fn);  // Template; concrete type can enable inlining, but does not guarantee it.
void repeat3(int n, const auto& fn);                     // C++20
void repeat4(int n, void (*fn)(int));                    // Function pointer; suitable captureless lambdas can convert.

auto print = [](auto value) {            // generic: static per-instantiation
    static int callCount{0};
    std::cout << callCount++ << ": " << value << '\n';
};
print("hello"); // 0   print("world"); // 1
print(1);       // 0!  print(2);       // 1
print("again"); // 2

int ammo{10};
auto shoot1 = [ammo]() mutable { --ammo; };  // copy decrements
auto shoot2 = [&ammo]()        { --ammo; };  // the real ammo

[health, armor, &enemies](){};  // explicit mix
[=, &enemies](){};              // default first, other-kind explicit
[&, armor](){};
[&, &armor](){};   // CE   [=, armor](){};        // CE
[armor, &health, &armor](){};  // CE   [armor, &](){};  // CE

std::find_if(v.begin(), v.end(),
    [userArea{width * height}](int a) { return userArea == a; }); // init-capture

auto f = [] -> int { };  // C++23 form; calling it w/o return = UB
```

## Interview Q&A

### What is a lambda under the hood?

It is an object of a compiler-generated closure class with a call operator. By-value captures provide stored state, while reference captures refer to external objects. That model explains mutable captures and lifetime risks, but exact size and layout depend on the implementation.

### Why does a lambda need mutable?

An ordinary lambda's call operator is const by default. Mutable lets the body modify its own captured copies. It does not make a by-value capture update the original variable; I need a reference capture for that, along with a valid lifetime.

### How do you choose between a template callable and std::function?

A template preserves the concrete type and often enables more optimization, but can produce more instantiations. Std::function provides one stable type for different callables and is convenient for storage, with possible allocation and dispatch costs. I choose based on the interface and measure important hot paths.

### What is the difference between scope and lifetime?

Scope concerns where a name is visible. Lifetime concerns when the object exists and can be used. A static local is a good example: its name has block scope, but an initialized object can survive between calls. Storage duration and linkage describe separate aspects again.

### Is return-value optimization guaranteed?

The C++17 same-type prvalue construction case is guaranteed. NRVO, which returns a named local, is optional. I keep those cases separate and usually return the local by name so the compiler can apply NRVO or the applicable move rules.

### When is recursion a poor choice?

When the worst-case depth can exhaust the stack, or when iteration expresses the same logic simply with less overhead. I do not rely on tail-call optimization for correctness. Even tree recursion can be linear-depth if the input tree is skewed.

### Is a static local cache thread-safe?

Its initialization is thread-safe, but later reads and writes still need the usual synchronization. A vector cache that multiple threads modify can race. I would either protect it or make the cache owned by the caller or thread.

## Practice history

The entries below preserve the original practice record. Use the explanations above for the current rules and qualifications.

### Questions (getcracked)

- [x] Once or twice? — 29/08 — ok
- [x] I am the shadows. — 29/08 — ok
- [x] Overloading lambdas! / Am I missing something? / Between two parts. — 29/08 — ok
- MISSED 30/08 (tree Q): sizeof captureless lambda — said 8 ("functor ≈ pointer"); empty struct → 1.

### Quiz log (Claude)

- 31/08: return-CE/UB triple (a,b,c) — ok. NRVO count right, naming imprecise: named local = NRVO (optional), prvalue = guaranteed elision. Mutable/const-operator() — ok twice.
