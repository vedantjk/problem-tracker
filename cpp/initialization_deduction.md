# Initialization & Type Deduction

For the meanings of lvalue, xvalue, and prvalue, and how they affect reference binding and moving, see [value categories](value_categories.md).

## Objects, variables, and initialization

An object occupies storage and has a type and lifetime. A variable is introduced by a declaration of an object or reference; not every object has a name, and a reference is not itself an object. An identifier is a name used in the program.

Initialization establishes an object's initial state. Assignment changes an existing object. Although both can use `=`, `std::string s = "hello";` initializes a string, while a later `s = "goodbye";` assigns to it. For class types, construction and assignment can call different functions.

| Example | Meaning |
|---|---|
| `int a = 5;` | This uses copy-initialization. |
| `int a(5);` | This uses direct-initialization. |
| `int a{5};` | This uses direct-list-initialization. |
| `int a{};` | The empty initializer gives this scalar the value zero. |
| `int a;` | This uses default-initialization, which does not initialize an automatic scalar's value. |

A local `int a;` must be assigned a value before an ordinary read. Through C++23, reading such an indeterminate `int` has undefined behavior. C++26 distinguishes erroneous and indeterminate values; it does not make uninitialized reads acceptable. See the [behavior catalog](ub_catalog.md).

Default-initializing a class invokes its default constructor. This does not necessarily initialize every scalar member. In `struct S { int a; std::string b; };`, a local `S s;` gives `b` an empty string but leaves `a` uninitialized. A scalar with static storage duration receives static initialization even without an explicit initializer.

## Braces, narrowing, and the most vexing parse

List-initialization rejects narrowing conversions. `int x{4.5};` is invalid even if truncation would be intentional. Some conversions from constant expressions are permitted when the actual value fits, such as `int x{4L};` on a target where four is representable. A nonconstant `double` cannot be list-initialized into an `int` merely because its current value happens to be integral.

Braces are useful, but their constructor-selection rules matter. `std::vector<int> a(10, 1);` creates ten elements containing one, whereas `std::vector<int> b{10, 1};` creates two elements. A matching initializer-list constructor receives preference.

If a declaration can be parsed as a function declaration, it is parsed that way. `std::string s();` declares a function instead of constructing an empty string. This is the most vexing parse; `std::string s{};` makes the object intent clear. The same issue arises with forms such as `Double d(MyInt(i));`.

A functional conversion expression requires the appropriate type spelling. `unsigned int{5}` is not valid expression syntax; use a type alias such as `using UInt = unsigned int;` followed by `UInt{5}`, or use `static_cast<unsigned int>(5)`.

## Aggregates and designated initializers

An aggregate is an array or a class whose elements or members can be initialized directly from a list. A simple data-only struct such as `Point` below is a common example.

In C++20/23, an aggregate class cannot have user-declared or inherited constructors or virtual functions. Its direct non-static data members must be public: these are members declared in the class itself that belong to each object, rather than shared static members or inherited members. Its base classes cannot be virtual, private, or protected. Default member initializers are permitted; aggregate rules have changed across language versions.

C++20 designated initialization names direct non-static members of an aggregate in declaration order. Members may be skipped; omitted members use their default member initializer when present, or the applicable empty-initialization rules. A missing reference member still needs a valid binding.

```cpp
struct Point { double x = 0; double y = 0; };
Point p{.y = 3};              // x keeps its default value, zero.
// Point q{.y = 3, .x = 2};   // Compile error in C++20/23: wrong order.
```

In C++20/23, do not mix positional and designated clauses, repeat a designator, designate a static member, or use C-style nested designators. Both `.x = 2` and `.x{2}` can supply a member initializer. These are the version-specific [C++23 initialization rules](https://timsong-cpp.github.io/cppwp/n4950/dcl.init).

## Static initialization, constinit, and thread_local

Static initialization occurs before dynamic initialization. It consists of constant initialization when the requirements are met, or zero-initialization otherwise. Constant initialization is often represented directly in the executable's data, while zero-initialized storage often uses BSS; section placement is an implementation detail.

Dynamic initialization performs remaining initialization work. Non-local dynamic initialization often happens before `main`, but the language permits deferred initialization in some cases. Avoid a global initializer that depends on another translation unit's dynamically initialized object being ready. This is the static initialization order problem.

A function-local static can initialize on first use, and its initialization is thread-safe since C++11. That guarantee does not make later writes to the object thread-safe. Another solution is to make the dependency constant-initialized.

For suitable static or thread-storage variables, the qualifiers express different intentions:

- `const` prevents ordinary modification, but does not require constant initialization.
- `constexpr` requires constant-expression initialization and makes an object const.
- `constinit`, introduced in C++20, requires static initialization and diagnoses an unsuitable initializer. It does not itself make the object const, and it cannot be used for an ordinary automatic local.

A `thread_local` variable has a separate instance for each thread, with thread storage duration. Initialized instances are destroyed at thread exit. Initialization timing depends on whether the variable is local or non-local and on the permitted implementation choices. At namespace scope, adding `static` changes linkage; `static thread_local` is not simply equivalent to `thread_local`.

Thread-local storage is useful for per-thread counters, random-number generators, and scratch buffers. Its access cost depends on the platform and TLS model; an x86-64 Linux implementation may use the `fs` segment register.

## const, volatile, and return values

Top-level const qualifies the object itself, as in `int* const p`. Low-level const describes the accessed object, as in `const int* p`. A read-only pointer or reference does not make the underlying object immutable through all aliases.

Top-level const on a by-value parameter is not part of the function type. `void f(int);` and `void f(const int);` declare the same function. The definition can use const to prevent changing its local parameter without changing the public signature.

Avoid const-qualified class return values in ordinary value-returning APIs because they can block moves in contexts that need them. However, `const std::string getName(); std::string s = getName();` does not inherently force a copy in C++17 and later: same-type prvalue initialization can construct `s` directly. Assignment to an existing string is a useful contrasting case, since a const result cannot bind to the usual move-assignment parameter.

`const` and `volatile` are the cv-qualifiers. Volatile access is relevant to some hardware and signal-related interfaces, but does not supply atomicity or thread synchronization. Some volatile operations were deprecated in C++20, with later revisions adjusting parts of that set. Use atomics and synchronization primitives for shared mutable state.

## auto deduction

For plain `auto`, deduction normally removes references and top-level const because a new value is being initialized. With `auto&`, the declaration asks for a reference and preserves the source's const qualification. In these examples, the source is a string:

```cpp
const std::string source = "hello";
auto copy = source;            // std::string: a separate, mutable value.
auto& alias = source;          // const std::string&: a reference to source.
const auto& view = source;     // const std::string&: a read-only reference.
auto&& forwarded = source;     // const std::string&: source is an lvalue.
```

An `auto&&` declaration in this deduction context is a forwarding reference. Lvalue initializers produce an lvalue reference after reference collapsing; rvalues generally produce an rvalue reference. A named rvalue-reference variable is itself an lvalue expression when used by name.

Given `const std::string& getConstRef();`, `auto r{getConstRef()};` creates a separate `std::string`. Plain `auto` deduces a value type, so `r` is neither a reference nor const. Use `auto&` or `const auto&` to keep a read-only reference to the original string, or `const auto` for a const copy. Here, `const auto&` makes the read-only intent explicit.

The keyword `constexpr` is not part of a type and is never deduced; a `constexpr auto` declaration must say so itself.

For pointers, plain auto keeps the pointer type and the pointee's const qualification. `auto*` additionally requires a pointer-compatible initializer. `const auto p = getPtr();` makes the pointer object const; `const auto* p = getPtr();` makes access to the pointee const. With `auto*` the position of const matters in the same way as for a written-out pointer type: `const auto*` qualifies the pointee, `auto* const` qualifies the pointer, and `const auto* const` qualifies both. Writing `const auto const` is invalid because it applies const to the same thing twice.

`auto s = "hi";` deduces `const char*` after array-to-pointer conversion. The `s` and `sv` literal suffixes from `std::literals` select `std::string` and `std::string_view`. With braces, `auto x = {1, 2};` deduces an initializer list, `auto x{5};` deduces int, and `auto x{1, 2};` is invalid.

## Reference binding and lifetime

A local `const T&` or `T&&` can extend a temporary's lifetime when the lifetime-extension rules apply. Binding a new reference to an existing reference does not extend the lifetime again. A temporary passed to a reference parameter normally survives only to the end of the full expression containing the call.

Returning a reference to that temporary does not extend it further. This is why a returned reference can dangle even when the receiving variable is `const auto&`. See [pointers and references](pointers_references.md) for examples and exceptions.

An unusual syntax detail is that casting an object to void discards its value; it does not invoke a user-defined `operator void()`. That conversion function can still be called explicitly by name.

## Errors and pitfalls

Distinguish an invalid binding from a valid binding that later dangles. A plain `auto&` cannot bind to an ordinary temporary. A `const auto&` may bind successfully, but whether the referred object stays alive depends on how that object was obtained. Likewise, distinguish a function declaration produced by the vexing parse from the later error caused by trying to use it as an object.

## Additional syntax examples

These are independent syntax sketches, including deliberately invalid examples marked `CE` (compile error). They are not one compilable program.

```cpp
int a = 5;   // copy-init
int b(5);    // direct-init
int c{5};    // direct-list-init (preferred)
int d{};     // value-init -> 0
int w1{4.5}; // CE: narrowing

struct Point { double x{0.0}; double y{0.0}; };
const Point p { .x = 10.0, .y = 20.0 };      // designated (C++20)
const Point o { .x{100.0}, .y{-100.0} };     // brace form ok
const Point t { .x = 50.0, .y{-40.0} };      // = and {} mix ok

struct Date { int year; int month; int day; static int mode; };
Date d1{ .mode = 10 };              // CE: static member
Date d2{ .day = 1, .year = 2010 };  // CE: out of order
Date d3{ 2050, .month = 12 };       // CE: positional + designated
Date d4{ .mh.min = 55 };            // CE: nested (C-only)

std::string foo();        // vexing parse: function decl
Double d(MyInt(i));       // vexing parse again
Double ok((MyInt(i)));    // fix; or Double ok{MyInt(i)};

struct X { operator void() { std::cout << "G"; } };
X x; (void)x; static_cast<void>(x);  // nothing printed
x.operator void();                    // G

unsigned int c2 = int{5};  // ok; unsigned int{5} is CE (multi-word)

const int ci{5};
auto b2{ci};       // int (const dropped - VALUE form only)
auto s{"hello"};   // const char*
using namespace std::literals;
auto s1{"goo"s};   // std::string
auto s2{"moo"sv};  // std::string_view

auto  v1 = obj.getRef();  // int   (copy)
auto& v2 = obj.getRef();  // int&  (or const int& if source is const!)

// auto with pointers (12.14): pointers never drop, top-level const does
std::string* getPtr();
auto  p1{ getPtr() };        // std::string*
auto* p2{ getPtr() };        // std::string* — CE if initializer weren't a pointer
const auto* p3{ getPtr() };  // const std::string*   (pointee const)
auto* const p4{ getPtr() };  // std::string* const   (pointer const)
const auto  p5{ getPtr() };  // std::string* const — const lands on the POINTER

// ---- storage-init (cppstories) ----
// the three init pathways for globals:
double z = 100.0;   // Constant initialization; executable section placement is implementation-specific.
int x;              // Zero-initialized to 0; commonly placed in BSS. A local int x; is uninitialized.
Value v{ 42 };      // The constructor determines whether constant or dynamic initialization applies.

// static init order fiasco, minimal repro:
// b.cpp
Point createPoint(double x, double y) { return Point{ x, y }; }
Point center = createPoint(100, 200);          // dynamic-init
// a.cpp
extern Point center;
Point offset = { center.x + 100, center.y + 200 };  // reads center — may still be ZEROED
// Cross-file dynamic initialization can depend on build/runtime choices; do not rely on link order.
// Use initialization on first use or establish constant initialization instead.

// constinit vs constexpr (C++20):
constinit std::pair<int, double> global { 42, 42.2 };  // compile-time init, MUTABLE
constexpr std::pair<int, double> constG { 42, 42.2 };  // compile-time init, const
global = { 10, 10.1 };   // ok
// constG = { 10, 10.1 };  // CE

// thread_local: one per thread, ctor/dtor per thread
struct Value {
    Value(int x) : v(x) { std::cout << "Value(" << v << ")\n"; }
    ~Value() noexcept   { std::cout << "~Value(" << v << ")\n"; }
    int v{ 0 };
};
thread_local Value tls{ 42 };
void foo() { tls.v = 100; }        // touches THIS thread's copy
// Each worker that initializes tls gets its own instance and destructor at thread exit.
// Main has an initialized instance only if the applicable initialization rules cause it to be initialized.

// static local: lazy init (first call), persists across calls
int counter_up() { static int counter = 0; return ++counter; }
// 4 calls → returns 4

// ---- const nuances (learncpp 5.1) ----
const std::string getName() { return "alex"; }
std::string s = getName();   // C++17+: direct prvalue construction; this does not force a copy.
s = getName();               // Assignment to an existing string: const blocks the usual move assignment.

void f(int);                 // header
void f(const int x) { }      // .cpp — SAME function; top-level const not in signature
// void f(int x) {} + void f(const int x) {}  → redefinition CE, not overload
```

## Interview Q&A

### How is initialization different from assignment?

Initialization establishes the initial state of a new object. Assignment operates on an object that already exists. For a class, initialization can call a constructor, while assignment can call an assignment operator. The presence of an equals sign alone does not tell me which is happening.

### Does auto always drop const?

No. Plain auto normally creates a value and drops top-level const. Auto with a reference preserves the const qualification needed for a valid binding. If the source is a const string, auto gives me a string copy, while auto-reference gives me a const string reference.

### What does constinit add beyond const and constexpr?

Const does not guarantee static initialization. Constexpr requires constant-expression initialization and makes an object const. Constinit requires static initialization for a suitable static or thread-storage variable while allowing later mutation unless I also specify const.

### Why can braces change the meaning of vector initialization?

List-initialization gives preference to an applicable initializer-list constructor. Parentheses with ten and one create ten copies of one, but braces with ten and one create two elements. I choose the syntax based on the constructor semantics I need.

### Does returning const by value always force a copy?

No. In C++17 and later, initializing a new object from a same-type prvalue can construct it directly. Const can still block moving in other contexts, such as assignment to an existing object, so I generally avoid const class return values.

### When does a const reference extend a temporary's lifetime?

It can extend the lifetime in eligible initialization expressions, such as a local const reference initialized from a temporary. It does not renew a lifetime through another reference or a function returning a reference. I trace the original temporary and the full expression in which it was created.

## Practice history

The entries below preserve the original practice record. Use the explanations above for the current rules and qualifications.

### Questions (getcracked)

- [x] Schrödinger's Initializer — 29/08 — ok
- [x] The designated representative. — 29/08 — ok
- [x] Forgot one? — 29/08 — ok

### Quiz log (Claude)

- 30/08 MISS + 31/08 REPEAT MISS: `auto& b = f()` where f returns `const T&` — said `T&` both times. auto& keeps const; deduction never produces an illegal binding. **Twice-missed: drill this.**
- 31/08: bit_cast sizes + `auto&`/`const auto&` temporary pair (Q11) — all ok.
