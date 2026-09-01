# auto / Type Deduction

## Core model
- auto uses template type deduction rules: **drops top-level const and references**. `const int a; auto b = a;` → int. `auto x = a.getx()` where getx returns int& → int (a copy). Want them back: `auto&`, `const auto&`, `auto&&` (forwarding).
- String literals deduce as `const char*`, never std::string. Suffixes from `std::literals`: `"goo"s` → std::string, `"moo"sv` → string_view.
- Braces: `auto x = {1,2}` → initializer_list; `auto x{5}` → int; `auto x{1,2}` → error.
- Conversion-operator oddity: `operator void()` is never used for casts — `(void)x` and `static_cast<void>(x)` discard the value without calling it; only explicit `x.operator void()` runs it.
- Direct-list-init of a temporary needs a simple (one-word) type specifier: `unsigned int{5}` is a compile error, `int{5}` is fine (so is a using-alias for the multi-word type).

## Quiz misses
- 30/08 (Claude): `const string& f(); auto& b = f();` — said `string&`; it's `const string&`. Top-level const drops only for value deduction; deducing a reference keeps the const (a non-const ref can't bind to const). `auto` = copy w/o const, `auto&` = ref WITH const.

## Compile errors vs UB
Compile errors:
- `auto x{1, 2};` — direct-list-init with >1 element. `auto x;` — no initializer to deduce from.
- `unsigned int{5}` — temporary needs a one-word type specifier (`int{5}` fine, or alias it).
- `auto& b = f();` where f returns by value... is fine only if const; plain `auto&` to a temporary is CE.

UB:
- Dangling through a temporary's member: `auto& s = get_pair().first;` — lifetime extension doesn't chain through function-call results; `s` dangles at the semicolon... (actually CE for plain auto&; `const auto&`/`auto&&` compiles and dangles — the compiling version is the dangerous one).

## Syntax anchors
```cpp
struct X { operator void() { std::cout << "G"; } };
X x;
(void)x;                  // conversion fn NOT used for void casts
static_cast<void>(x);     // same - nothing printed
x.operator void();        // only this prints G

unsigned int c = int{5};  // ok; unsigned int{5} would be CE (multi-word type)

const int a{5};
auto b{a};        // int (const dropped)
auto s{"hello"};  // const char*, NOT std::string
using namespace std::literals;
auto s1{"goo"s};  // std::string
auto s2{"moo"sv}; // std::string_view

auto  v1 = obj.getRef();  // int   (ref dropped -> copy)
auto& v2 = obj.getRef();  // int&  (say it explicitly)
```

## Traps / interview one-liners
- "auto never deduces a reference — every `auto x = f()` is a copy unless you write `auto&`."
- "`auto s = \"hi\";` is a const char*; the std::string never existed."
- "Dropping const/ref is deliberate: silent references were considered more dangerous than silent copies."
