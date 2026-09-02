# Functions, Scope & Lambdas

## Functions & calls
- `main`: int return, implicit return 0 (only main), can't be called, not always first (global initializers precede it).
- One return value; struct/pair/tuple + structured bindings for more; small structs (≤16B) return in RAX:RDX (SysV); RVO covers big ones.
- Call overhead: return address, register saves, arg shuffle per ABI, stack frame — and the call is an optimization BARRIER (the real cost). Inlining removes it at i-cache expense; net effect: measure.
- Flowing off the end of a non-void function: UB (CE only for `return;` with no value; `void f(){return 0;}` CE). Compilers warn, don't reject.

## Recursion & the call stack (learncpp 20.3, 01/09)
- Every recursive call pushes a frame; no base case → stack exhaustion → crash (learncpp's broken countdown died around count -11732). Default stack ≈ 8MB Linux / 1MB MSVC → depth limit is real: linear recursion on a 10^6-element LC input WILL overflow; recurse on log-depth structures (trees, halving), iterate on linear ones.
- Base case = input whose answer is trivial (0, 1, empty). Termination condition guards the recursive call.
- **Sequencing trap in recursive args**: `return sumTo(--sumto) + sumto;` — the two operands of `+` are indeterminately sequenced, so which `sumto` the right side reads is unspecified (pre-C++17 UB). Pass `sumto - 1`, never mutate. (→ expressions sequencing table.)
- **Static-local memoization idiom**:
  ```cpp
  int fibonacci(std::size_t count)
  {
      static std::vector results{ 0, 1 };   // CTAD → vector<int>; initialized once
      if (count < std::size(results))
          return results[count];
      results.push_back(fibonacci(count - 1) + fibonacci(count - 2));
      return results[count];
  }
  ```
  Naive fib(12) ≈ 1205 calls → 35 with memo. Notes: magic-static *initialization* is thread-safe (C++11); the *mutation* (`push_back`) is not — data race if called concurrently. Cache persists across top-level calls (static duration) — feature or bug depending on the problem.
- **Tail call** = call as the last action, nothing after it. Compilers *may* turn tail recursion into a loop (no stack growth) — but C++ does **not** guarantee TCO (unlike Scheme); at -O0 it won't happen, so never rely on it for correctness. The countdown's "pop" prints after the call → not a tail call, frames must survive.
- Iterative is almost always faster (no frame overhead / call is an optimization barrier, see above). Recursion earns its keep when: markedly simpler, depth is bounded, or the iterative version just hand-rolls a stack anyway (tree traversals). learncpp: "favor iteration over recursion, except when recursion really makes sense."

## Scope · duration · linkage (three separate properties)
- Scope: where the NAME is visible (compile-time). Duration: when the OBJECT lives (automatic/static/dynamic/thread). Linkage: whether the same name elsewhere is the same ENTITY (none/internal/external).
- Locals: block scope, automatic duration, no linkage. `static` local: block scope, static duration. Namespace-scope: external linkage by default; anonymous namespace/`static` → internal.
- Shadowing: inner hides outer; `::name` reaches a global, nothing reaches a shadowed local. -Wshadow.
- Return-by-value: C++17 GUARANTEES elision for prvalues (`return W{};`); NRVO for named locals (`W w; return w;`) universal in practice but OPTIONAL in the standard (-fno-elide-constructors shows the copies).

## Lambdas
- A lambda is a compiler-generated struct: captures = data members, body = `operator()` (const by default → `mutable` drops that). Unique unnamed type; store with auto.
- Sizes (verified): `[]` → 1 (empty struct), `[x]` int → 4, `[&x]` → 8 (reference stored as pointer).
- Captures: only automatic-duration variables need capturing (statics/globals/constexpr visible directly). By-value copies at DEFINITION time; by-ref dangles if the variable dies. `[=]`/`[&]` defaults first, capture only what's used, mix with the other kind, no duplicates. Init-capture `[y = expr]`. `[this]` = pointer, `[*this]` = copy (C++17); `[=]`-implicit-this deprecated C++20.
- Passing: std::function (type-erased, may heap-allocate, indirect call — no inlining), template `const T&` / C++20 `const auto&` (inlines: use in hot paths), function pointer (captureless only; `+[]{}` forces).
- Generic lambdas (auto params, C++14): one instantiation per type — a `static` local inside is PER-INSTANTIATION.
- Implicitly constexpr since C++17 when possible. Missing return in non-void: UB. `[] -> int {}` parenless: C++23.

## Tuple (returning multiples & more)
- Create: explicit types / CTAD `std::tuple t{42, 3.14f, true}` / make_tuple (decays). Access: `get<0>` (compile-time index only), `get<float>` (exactly-one-of-type only).
- Unpack: structured bindings `auto [a,b,c] = t` (new vars) vs `std::tie(a,b,c) = t` (existing; std::ignore skips). `std::tie(x.a,x.b) < std::tie(y.a,y.b)` = the multi-key comparator idiom.
- `tuple_size_v`, `tuple_element_t`, `tuple_cat`, `std::apply(f, t)`. Lexicographic comparison.
- CE: ambiguous/absent get<T>, out-of-range get<I> (never an exception), binding-count mismatch, runtime index, tie-ing a temporary, size-mismatched comparison. Dangling: forward_as_tuple stored past its expression; tuples never extend element lifetimes.
- Public APIs: return a named struct; tuple for local plumbing.

## Compile errors vs UB
- CE: modifying by-value capture without mutable; duplicate/misordered captures; std::function signature mismatch; sizeof(incomplete); `auto&` to temporary; two inline defs in one TU.
- UB: off-the-end non-void return; returning ref/pointer to a local (`int& f(){int x; return x;}`); use-after-scope via saved pointer; by-ref capture outliving its variable; differing inline defs across TUs (NDR).
- Unspecified: cross-TU global ctor order (static init order fiasco).
- Throws (not UB): calling a moved-from/empty std::function → bad_function_call.

## Questions (getcracked)
- [x] Once or twice? — 29/08 — ok
- [x] I am the shadows. — 29/08 — ok
- [x] Overloading lambdas! / Am I missing something? / Between two parts. — 29/08 — ok
- MISSED 30/08 (tree Q): sizeof captureless lambda — said 8 ("functor ≈ pointer"); empty struct → 1.

## Quiz log (Claude)
- 31/08: return-CE/UB triple (a,b,c) — ok. NRVO count right, naming imprecise: named local = NRVO (optional), prvalue = guaranteed elision. Mutable/const-operator() — ok twice.

## Syntax anchors
```cpp
auto l = [captures](params) -> ret { body; };

// 4 ways to receive a callable:
void repeat1(int n, const std::function<void(int)>& fn); // type-erased
template <typename T> void repeat2(int n, const T& fn);  // template (inlines)
void repeat3(int n, const auto& fn);                     // C++20
void repeat4(int n, void (*fn)(int));                    // captureless only

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

## Traps / interview one-liners
- "A lambda is a struct with operator(); captures are its members. Everything follows."
- "std::function in a hot loop = indirect call the optimizer can't see through; template param instead."
- "mutable exists because operator() is const by default."
- "By-ref capture + returning the lambda = the classic dangle."
- "Scope is names, duration is objects, linkage is identity."
- "Guaranteed elision = prvalues (C++17); NRVO = named locals, universal but optional."
- "Global initializers run before main; cross-TU order unspecified — static init order fiasco."
- "Pointers are cheap, pointees are owned — a pointer variable is 8 stack bytes, only allocations leak."
