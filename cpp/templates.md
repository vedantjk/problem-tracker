# Function Templates: Instantiation, Deduction, Non-Type Parameters & Specialization

## What a function template is

Writing `max(int, int)` and `max(double, double)` with identical bodies is a maintenance problem and still fails the next caller who needs `long`. A function template is a stencil from which the compiler generates the overloads on demand: replace the type that should vary with a type template parameter, and put a template parameter declaration in front. `template <typename T> T max(T x, T y) { return (x < y) ? y : x; }` is the primary template; `typename` and `class` mean the same thing in that position. Types that did not exist when the template was written still work, because the actual type is fixed only when the template is used. There are three kinds of template parameters: type parameters, non-type parameters holding a constant value, and template template parameters holding a template. Name a trivially used type parameter with a single capital letter starting at `T`; give a parameter with real requirements a descriptive name such as `Allocator`, because the requirements are visible only from how the body uses the type, which is why library documentation states them explicitly.

## Instantiation

A function template is not a function and is not compiled on its own. When a call needs a version for particular types, the compiler instantiates one: it clones the template with `T` replaced by the actual type, and that generated function, formally a specialization, is an ordinary function from then on. Instantiation happens once per translation unit per set of types; later calls with the same types reuse the instance, and a template nobody calls generates nothing. The explicit form `max<int>(1, 2)` names the type; with `max<double>(1, 2)` the compiler instantiates the double version and then converts the `int` arguments as an ordinary call would.

Usually the template argument is deduced from the call. `max(1, 2)` and `max<>(1, 2)` both deduce `T` as `int`, with one difference in overload resolution: the empty angle brackets consider only template instances, while the plain call considers non-template functions too and prefers a non-template function over an equally good template instance. That preference is the reason to write plain calls: a non-template `print(bool)` that prints `true` instead of `1` wins over `print<T>` when both match. A template may mix template and ordinary parameters, `template <typename T> int f(T, double)`, and the ordinary ones behave like any parameter, including default arguments, which every instance shares. A generated function compiles only if the body makes sense for the type, so `addOne(std::string)` fails at `x + 1`, and it compiles whenever the body is syntactically valid whether or not it makes sense, so `addOne("Hello, world!")` performs pointer arithmetic and prints `ello, world!`. A deleted specialization, `template <> const char* addOne(const char*) = delete;`, turns that into a compile error.

Each instance is a separate function with its own static locals. A `static int id` inside `printIDAndValue<T>` counts `int` calls and `double` calls independently, so the output can run `1, 2, 1` instead of `1, 2, 3`.

## Deduction does not convert

Template argument deduction matches argument types exactly; the implicit conversions of ordinary overload resolution do not apply. `max(2, 3.5)` against `max<T>(T, T)` fails to compile, because `T` would have to be both `int` and `double`, and the compiler will not pick `double` and convert the `int`. This is deliberate: it keeps deduction simple, and it lets a template insist that two arguments have the same type. The fixes are to cast the arguments to a common type, to name the type, `max<double>(2, 3.5)`, which skips deduction and then converts, or to give each parameter its own type parameter. With `template <typename T, typename U> auto max(T x, U y)`, the parameters deduce independently, and the return type must be `auto`: returning `T` would narrow `3.5` to `3` when `T` is `int`, and returning `U` fails the mirror-image call. A function with a deduced return type must be defined before it is called, since the compiler needs the body to know the type. C++20 abbreviates the two-parameter form to `auto max(auto x, auto y)`, where each `auto` parameter becomes its own template parameter; there is no abbreviated spelling for two parameters that must share a type.

Function templates overload like functions. When several templates match, partial ordering picks the more specialized one, so `add<T>(T, T)` beats `add<T, U>(T, U)` for `add(1.2, 3.4)`, and a call neither template is more specialized for is ambiguous.

## Non-type template parameters

A non-type template parameter is a placeholder for a constant value rather than a type: `template <int N> void print() { std::cout << N; }` is called as `print<5>()`, and `std::bitset<8>` uses one for its size. Allowed types are integral and enumeration types, pointers and references to objects or functions, `std::nullptr_t`, and since C++20 floating-point types and literal class types. Their purpose is to carry a value into a context that needs a constant expression: function parameters can never be `constexpr`, even in `consteval` functions, so `static_assert(v >= 0)` inside `getSqrt(double v)` is impossible, while `template <double D> double getSqrt() { static_assert(D >= 0.0); ... }` rejects `getSqrt<-5.0>()` at compile time. Since C++17 `template <auto N>` deduces the parameter's type from the argument. Arguments undergo only converted-constant-expression conversions, a shorter list than list-initialization allows: a `char` converts to an `int` parameter, but a `constexpr int` does not convert to a `double` parameter. Overloading on different non-type parameter types is a trap: matching is not ranked by conversion quality, so `print<'c'>()` against `template <int N>` and `template <char N>` overloads is ambiguous.

## Templates across files

A template definition in a `.cpp` file is useless to other translation units: a forward declaration in `main.cpp` compiles, but no instance is ever generated in `add.cpp` because nothing there calls it, and the linker reports an undefined reference. Put template definitions in headers. The one-definition rule permits identical definitions of templates in many files, and functions instantiated from templates are implicitly `inline`, so every translation unit can instantiate the same `max<int>` and the linker merges them.

## Specialization

To give one type its own implementation, first prefer a plain non-template function: define `void print(double)` beside `template <typename T> void print(const T&)`, and calls with a `double` pick the non-template. The non-template need not match the template's signature, and it is preferred over both the template and any explicit specialization of it. Explicit full specialization exists for the cases a non-template cannot cover: after the primary template has been declared, `template <> void print<double>(const double& x) { ... }` replaces the generated instance for `double`. The empty angle brackets are mandatory, the signature must be the primary's with `T` substituted, so a primary taking `const T&` cannot be specialized with pass-by-value, and a full specialization is not implicitly `inline`, so one defined in a header needs the keyword or it violates the one-definition rule. Specializations may be deleted to forbid a type. A member function of a class template is a different case: `i.print()` on a `Storage<int>` calls `Storage<int>::print`, so changing it for `double` means specializing the member `Storage<double>::print`, still with `template <>` in front of the out-of-class definition, or specializing the whole class; leaving off `template <>` is the miss recorded in the baseline quiz.

Two facts about templates and virtual functions. A class template may have virtual functions, including a virtual destructor, because each instantiation is an ordinary class with an ordinary vtable. A member function template cannot be virtual: the vtable has to be complete when the class is compiled, and a template member would need a new slot for every instantiation anyone ever requested.

## Errors and pitfalls

- **Invalid: `max(2, 3.5)` against `max<T>(T, T)`.** Deduction does not convert; cast, name the type, or use two type parameters with `auto` return.
- **Invalid: calling a deduced-return-type template before its definition.** The body is needed to know the type.
- **Invalid: a virtual member function template.**
- **Invalid: a full specialization with a different signature**, or without the leading `template <>`.
- **Link error: template defined in a `.cpp` and used from another translation unit.** Definitions go in headers.
- **ODR violation: a full specialization in a header without `inline`.**
- **Ambiguity: two templates neither of which is more specialized**, or non-type overloads on different parameter types.
- **Logical error: expecting one static local across instantiations.** Each instance has its own.
- **Logical error: a template that compiles for the wrong type.** `addOne("text")` does pointer arithmetic; delete the specialization to forbid it.

## Additional syntax examples

```cpp
template <typename T> T max(T x, T y) { return (x < y) ? y : x; }
template <typename T, typename U> auto max(T x, U y) { return (x < y) ? y : x; }
auto max3(auto x, auto y) { return (x < y) ? y : x; }              // C++20 abbreviated

max<int>(1, 2);      // explicit, then converts arguments if needed
max<>(1, 2);         // deduce, templates only
max(1, 2);           // deduce, non-template preferred if one matches

template <int N> constexpr int factorial() { static_assert(N >= 0); return N <= 1 ? 1 : N * factorial<N - 1>(); }
template <auto V> void show() { std::cout << V; }                 // C++17 deduced non-type

template <typename T> void print(const T& x) { std::cout << x; }
template <> inline void print<double>(const double& x) { std::cout << std::scientific << x; }   // full specialization, inline for headers
template <> const char* addOne(const char*) = delete;

template <typename T>
struct Dynamic {
    virtual ~Dynamic() = default;                 // fine
    // template <typename U> virtual void copy(const U&);   // error: member template cannot be virtual
};
```

## Interview Q&A

### Why does `max(2, 3.5)` fail when `max(int, double)` would just convert?

Deduction is exact matching. Overload resolution converts arguments to fit a fixed signature, but a template has no signature until `T` is chosen, and the compiler refuses to choose `double` on your behalf and convert the `int`. Name the type, cast, or use two template parameters with an `auto` return type.

### When both a template and a non-template match, which is called?

The non-template, for a plain call. `max<>(1, 2)` restricts the search to template instances. This is why you can drop a hand-written `print(bool)` next to a generic `print<T>` and have the special case win without touching the template.

### Why do templates go in headers?

Because a template generates code only where it is used. A definition in one `.cpp` produces no instance for calls in another, so the linker finds nothing. Headers let each translation unit instantiate what it needs, and the one-definition rule allows the resulting identical inline instances to be merged.

### What is the difference between overloading a template with a non-template function and specializing it?

A non-template is a separate function that overload resolution prefers and that may have any signature. A full specialization replaces the instance the template would have generated for that type, must keep the template's signature, needs `template <>`, and is not implicitly inline. Prefer the non-template when it is possible; specialize when it is not, such as for a member of a class template.

### Can a member function template be virtual? Can a class template have a virtual destructor?

No, and yes. Virtual dispatch needs a vtable fixed at class compilation, which a member template would keep growing. A class template's virtual destructor is an ordinary virtual function of each instantiation.

## 16/09 deep dive: deduction, packs, folds, and ordering

### Common types and conversions after deduction

Deduction itself does not convert, but expressions inside an instantiated function use ordinary conversion rules. Comparing an `int` with a `double` is valid: the usual arithmetic conversions temporarily convert the `int` to `double` for the comparison without changing the original object. `std::common_type_t<T, U>` from `<type_traits>` names a type both operands can generally convert to; it does not inspect the runtime answer. Thus `std::common_type_t<int, double>` is `double`.

`auto max(T, U) -> std::common_type_t<T, U>;` can be forward-declared because its trailing return type is explicit. A declaration with a body-deduced return type, `auto max(T, U);`, is legal, but cannot be called until the compiler has seen the definition and deduced that return type.

`std::is_same_v<T, U>` is a compile-time `bool` testing exact type identity, including references and cv-qualifiers. It abbreviates `std::is_same<T, U>::value`. Explicit template arguments fill parameters left to right, and the rest are still deduced. For `template <typename T, typename U> void f(T, U)`, calls `f(i, d)`, `f<int>(i, d)`, and `f<double>(i, d)` print `0`, `0`, and `1`: only the third fixes `T` to `double`, deduces `U` as `double`, and then converts the first `int` argument during the call.

### Parameter packs and fold expressions

`template <typename... Args>` declares a type parameter pack: `Args` represents zero or more types. In `void printAll(Args... args)`, `args` is the corresponding value pack, and `sizeof...(Args)` is its length.

```cpp
template <typename... Args>
void printAll(Args... args)
{
    (std::cout << ... << args) << '\n';
}
```

`printAll(42, " hello ", 3.14)` expands conceptually to `std::cout << 42 << " hello " << 3.14 << '\n';` and prints `42 hello 3.14`. To print one item per line, fold the comma operator: `((std::cout << args << '\n'), ...);`. Fold expressions require parentheses; `std::cout << args << ... << '\n';` is invalid syntax.

Fold direction follows the pack's position:

- `(args + ... + 0)` is a binary **right** fold: `a1 + (a2 + (... + (an + 0)))`.
- `(0 + ... + args)` is a binary **left** fold: `(((0 + a1) + a2) + ... + an)`.
- `(args + ...)` is a unary right fold and requires a non-empty pack.

The `0` participates in every binary-fold expansion, but it is the additive identity and also makes an empty pack produce `0`. Direction can affect floating-point rounding and matters for non-associative or overloaded operators.

Before C++17 folds, a pack was often processed recursively:

```cpp
template <typename T>
T sum(T arg) { return arg; }

template <typename T, typename... Args>
T sum(T arg, Args... args)
{
    return arg + sum<T>(args...);
}
```

The explicit `<T>` locks every recursive call to the original first argument's type. `sum(0.5, 2, 0.5, 2)` therefore returns `double{5.0}`; `sum(2, 0.5, 2, 0.5)` uses `int`, truncates each `0.5` to zero as it becomes a recursive call's first parameter, and returns `4`. Streaming both with no separator prints `54`.

### Forwarding-reference deduction

In the deduced form `template <typename T> void foo(T&&)`, `T&&` is a forwarding reference. Passing an lvalue `int i` deduces `T = int&`; substitution gives `int& &&`, which collapses to `int&`. Therefore, `T x;` inside that instance becomes the invalid uninitialized-reference declaration `int& x;`. Any reference combination containing `&` collapses to `&`; only `&&` plus `&&` remains `&&`. See `value_categories.md` for the full treatment and `std::forward`.

### Return types in function-template signatures

Ordinary functions cannot differ only by return type: `void foo();` and `double foo();` conflict. A function-template signature does include its return type, so `template <typename T> void f();` and `template <typename T> double f();` may coexist. A direct `f<int>()` call is still ambiguous because call overload resolution does not use the requested result type, even in `double x = f<int>();`. A target function-pointer type can distinguish them: `void (*p)() = f<int>;` selects the first, while `double (*q)() = f<int>;` selects the second. Declaration distinctness and call-site selection are separate questions.

### “More specialized” means a subset of matches

For class partial specializations, `Obj<T, T>` matches equal-type pairs and `Obj<T, int>` matches pairs whose second type is `int`. Both match `Obj<int, int>`, but neither matching set contains the other: `Obj<double, double>` matches only the first, while `Obj<double, int>` matches only the second. The specializations are incomparable, so `Obj<int, int>` is ambiguous unless an exact full specialization `template <> class Obj<int, int> { ... };` resolves their intersection.

By contrast, `add<T>(T, T)` is more specialized than `add<T, U>(T, U)` because every same-type pair accepted by the first is also accepted by the second. “Looks more restrictive” is only a shortcut; the subset relationship is the useful mental model.

### Explicit function specialization is not an overload

An explicit function-template specialization belongs to a particular primary template and does not compete independently in overload resolution. C++ first selects the best non-template function or primary template, then checks whether that chosen primary has a matching specialization. Thus, if `foo<>(int*)` specializes an earlier `foo(T)`, but a later primary overload `foo(T*)` exists, `foo(p)` for an `int* p` chooses the more specialized `foo(T*)` primary and prints its result, not the specialization of `foo(T)`. This is another reason to prefer ordinary overloads over explicit function-template specializations.

## Practice history

### Reading

- 13/09/2026: learncpp 11.6 (function templates), 11.7 (instantiation), 11.8 (multiple template types), 11.9 (non-type template parameters), 11.10 (templates in multiple files), 26.3 (function template specialization).
- 16/09/2026: reviewed the sequence interactively and added the deduction, pack/fold, forwarding-reference, signature, recursive-sum, and specialization-ordering examples above.

### Questions (getcracked)

- Per platform record, rescraped 13/09/2026. Templates: Functions: Virtually a template. (virtual destructor in a class template is valid, a virtual member function template is not) ok. Template sum 1 and 2, Templatey signatures., There is no free template., First or second?, Template Specializations 1 and 2 not attempted.
- Worked through 16/09: Template sum (`54`), Templatey signatures, There is no free template, First or second?, and Template Specializations 1.
- Baseline quiz 29/08: full-specialization member definition without `template<>` MISSED; covered in the specialization section.
- Anki: deduction never converts; plain call prefers non-template; each instance has its own static locals; full specialization needs `template <>` and `inline` in headers; member function templates cannot be virtual; fold direction follows pack position; class partial ordering is a subset test; function specialization is considered only after its primary wins overload resolution.

<!-- gc-questions:start -->

## Related getcracked questions

Pulled from the Beginner C++ progress tree. ✓ answered correctly, ✗ attempted and missed, ○ not attempted yet. Regenerate with `python3 cpp/tools/gc_links.py` after re-scraping.

### Templates: Functions
- ✓ [Template sum 2](https://getcracked.io/question/876) — Easy
- ✗ [Templatey signatures.](https://getcracked.io/question/958) — Easy
- ✓ [There is no free template.](https://getcracked.io/question/944) — Easy
- ✓ [Virtually a template.](https://getcracked.io/question/953) — Easy
- ✓ [First or second?](https://getcracked.io/question/966) — Medium
- ✗ [Template Specializations 1](https://getcracked.io/question/692) — Medium
- ✓ [Template Specializations 2](https://getcracked.io/question/694) — Medium
- ✓ [Template sum 1](https://getcracked.io/question/875) — Medium

<!-- gc-questions:end -->
