# Pointers & References

For the meanings of lvalue, xvalue, and prvalue, and how they affect reference binding and moving, see [value categories](value_categories.md).

## Pointers and references

A pointer is an object whose value can identify an object or function, a position one past an object, or a null pointer. A reference is an alias for another entity and is not itself an object. A pointer variable can be reassigned; a reference must be initialized and cannot later be rebound.

For an ordinary object pointer, dereferencing a valid pointer yields an lvalue referring to its pointee. Thus `*(&x)` refers to `x`. The symbols depend on context: `&` can declare a reference, take an address, or perform bitwise AND; `*` can declare a pointer, dereference one, or multiply.

The address-of operator produces a typed pointer value, not a bare address. C++ has no address literals, so for an `int x`, the expression `&x` is a prvalue of type `int*` whose value is x's address. Printing `typeid(&x).name()` shows a pointer type (GCC's mangled spelling is `Pi`, pointer to int), and this typing is why `&x` participates in overload resolution, deduction, and pointer arithmetic as an `int*` rather than as a number.

```cpp
int x = 5, y = 6;
int* p = &x;
int& r = x;
p = &y;                      // p now points to y.
r = y;                       // This assigns 6 to x; r still refers to x.
```

Declare each pointer with its own star: `int* p1, p2;` declares one pointer and one int. Ordinary object pointers commonly occupy eight bytes on x86-64 platforms, regardless of the pointed-to type, but this is not a universal C++ layout guarantee.

## Null, uninitialized, and dangling pointers

Value-initializing `int* p{};` produces a null pointer. A local `int* p;` without an initializer must be assigned before its value is used. A null check distinguishes null from non-null; it does not prove that the pointee is alive or accessible.

A pointer becomes dangling when it no longer identifies a live object that can be accessed as intended. Destroying an object does not reset every pointer to it. There is no general validity test available from a raw pointer alone; track ownership and lifetime instead.

There is a subtle distinction between an object's lifetime ending and its storage being released. After storage duration ends, indirection through an invalid pointer has undefined behavior, while other uses of that invalid pointer value can have implementation-defined behavior. If storage still exists but the object's lifetime has ended, separate restricted-use rules apply. Avoid the blanket claim that every operation on every dangling pointer has the same classification. See [pointer validity](https://eel.is/c++draft/basic.compound) and [object lifetime](https://timsong-cpp.github.io/cppwp/n4950/basic.life).

## Lvalue references and const views

An ordinary non-const `T&` requires a compatible lvalue. It cannot bind directly to a const T or to an ordinary T temporary. Compatibility can include a derived-to-base binding, so “exactly the same type” is too restrictive.

A `const T&` accepts a wider range of initializers, including compatible lvalues and suitable temporaries. Some bindings perform a conversion and refer to a new temporary instead of the original object:

```cpp
short s = 3;
const int& converted = s;
s = 42;                      // converted still refers to the temporary int(3).
```

By contrast, a const reference bound directly to an int aliases that int. Another non-const alias can modify the object, and the change is visible through the const reference. Const access is a restriction on that access path.

Initializing `int& r2 = r1;` creates another reference to the same int; it does not create a reference object that refers to a reference object. The spelling `int&&` is not a reference to a reference either; since C++11 it declares an rvalue reference, a different kind of reference that binds to temporaries, so there is no syntax for a reference to a reference because the language has no such thing. `std::reference_wrapper` provides a reassignable wrapper when rebinding behavior is needed. A reference declared `constexpr` needs a constant-expression initializer; static-storage referents are the usual straightforward case. Constant evaluation has additional context-sensitive rules, so this is not a general storage-duration test for every possible reference use.

## Const pointers

The const qualification of the pointer and the pointee are independent:

| Declaration | Can the pointer be reassigned? | Can this pointer modify the pointee? |
|---|---|---|
| `int* p` | Yes. | Yes, if the pointee is otherwise modifiable. |
| `const int* p` | Yes. | No. |
| `int* const p` | No. | Yes, if the pointee is otherwise modifiable. |
| `const int* const p` | No. | No. |

A pointer to const may refer to a non-const object. The reverse implicit conversion is forbidden because it would permit modification of a const object. A const pointer must have an initializer.

Const applied to a type alias qualifies the whole aliased type, not a syntactic piece of it. With `using int_ptr = int*;`, the declaration `const int_ptr foo` means `int* const foo`, a const pointer to int, because the alias stands for the complete type `int*` and the const is top-level on that. It does not mean `const int* foo`. The same holds for `typedef`. Reading const-with-alias as textual substitution is the trap; an alias is a type, and const on a pointer type consts the pointer. This was missed on the 29/08 baseline quiz.

## Passing values, references, and pointers

Pass small, inexpensive values by value. Passing a large or expensive object by `const T&` avoids making a parameter copy when it binds directly. A temporary conversion can still be needed. “At most two pointer widths with inexpensive copy semantics” is a useful heuristic for value parameters, not a language rule.

Use `T&` for a required existing object that the function may modify. Use a pointer when optional presence or pointer-specific behavior is part of the interface. A pointer parameter itself is passed by value: reassigning that local pointer does not reassign the caller's pointer. C++ also has genuine reference parameters at the language level; do not describe all parameter passing as pass-by-value merely because an ABI may implement references using addresses.

```cpp
void reset_copy(int* p) { p = nullptr; }       // Only the local copy changes.
void reset_caller(int*& p) { p = nullptr; }    // The caller's pointer changes.
```

A reference to a pointer, `int*&`, is valid. A pointer to a reference, `int&*`, is not. Ordinary address-taking also cannot take the address of a literal such as `&5`.

The cost of passing a parameter includes both creating the parameter and accessing it inside the function. Small values are often inexpensive to copy and can be kept in registers. References avoid copying the referred object, but the compiler may need to account for aliases: other names or pointers that reach the same object. A reference does not necessarily add a memory read on every use, because the compiler can often optimize the access.

For a cheap independent input, pass by value. For a large existing object that the function only reads, a const reference usually avoids an unnecessary copy. Small class objects, such as a string view or an iterator, can also be cheap values; the fact that a type is a class does not determine the right parameter form.

```cpp
int square(int value);                       // Receives its own small value.
void inspect(const LargeRecord& record);     // Borrows an existing record.
void rename(Record& record);                 // May modify the caller's record.
```

Ownership is a separate decision from copying cost. Passing a `std::unique_ptr<T>` by value accepts ownership; taking `T&` or `const T&` borrows the object. Passing a `std::shared_ptr<T>` by value gives the function a share of ownership. When a function only uses the object, borrowing the object usually states that intent more directly. Some types also need references for their behavior: a stream such as `std::ostream` cannot be copied, and copying a derived object into a base-class value loses the derived portion, which is called slicing.

```cpp
void consume(std::unique_ptr<Record> record); // Takes sole ownership.
void inspect(const Record& record);          // Borrows without ownership.
void retain(std::shared_ptr<Record> record); // Receives shared ownership.
```

For read-only string input, a `std::string_view` parameter accepts an existing string, another view, or a string literal without copying the characters. It can also describe a substring. A `const std::string&` parameter binds cheaply to an existing string, but a literal requires a temporary string, and a view requires an explicit conversion to a string. Constructing that string copies characters and may allocate; short strings can fit inside the string object itself. Prefer the string reference when the function specifically needs a string object or its null-terminated storage. A view's characters need not end with a null character. The view does not own those characters, so do not retain it beyond their lifetime.

```cpp
void print_text(std::string_view text);
void needs_string(const std::string& text);

std::string_view part = "example";
print_text(part);                   // Copies the view, not the characters.
needs_string(std::string{part});    // Explicitly constructs a string.
```

When a function computes a result, a return value usually makes the call easier to understand. A named result struct can carry several related outputs. Copy elision can remove a copy or move of the result, though creating the result itself still has a cost.

```cpp
struct SinCos { double sine; double cosine; };
SinCos getSinCos(double degrees);
// The caller can write: SinCos result = getSinCos(45.0);
```

An output parameter can still be useful for reusing an existing buffer or working with an established API. An input/output parameter is appropriate when the function reads an existing object and changes it in place. With a non-const reference parameter, a call such as `update(record)` does not itself show that the object changes, so the function name and contract matter. A pointer spelling such as `update(&record)` shows address-taking, but does not by itself promise modification.

Choose a clear null-handling contract for pointer parameters: reject null, report it, or give it a documented meaning. An assertion disappears in many release builds, so it cannot implement required runtime validation by itself.

## Function pointers and nullptr

`int (*fp)(int)` declares a pointer to a function taking int and returning int. The parentheses distinguish it from a function returning a pointer. A function name usually converts to a function pointer; both `foo` and `&foo` can initialize it. An overloaded name needs enough target-type information to select an overload.

Call a valid function pointer as `fp(5)` or `(*fp)(5)`. Calling a null function pointer has undefined behavior. Default arguments belong to declarations at the call site and are not part of a function pointer's type. A pointer to `void f(int = 0)` still requires one argument when called through the pointer.

To make the pointer itself non-reseatable, the `const` goes after the asterisk, as in `int (*const fp)(int){ foo }`, following the same rule as object pointers. Deduction also follows the object-pointer rules: `auto fp{ &foo };` deduces `int (*)(int)`, and `auto fp{ foo };` deduces the same type because the function decays to a pointer during deduction. Only a reference declaration such as `auto& fr{ foo };` keeps a function reference instead of a pointer.

Function pointers do not have a standard implicit conversion to `void*`. Streaming a non-null function pointer therefore commonly selects the bool overload and prints `1`, or `true` with `boolalpha`. Converting it to an object pointer for address printing is conditionally supported, not universally portable. A `using` alias can make callback signatures easier to read; see [lambdas and callable wrappers](functions_scope_lambdas.md) for alternatives.

`nullptr` is a prvalue of type `std::nullptr_t`, which is not a pointer type. It converts to null pointer and null member-pointer values. Given `print(int)` and `print(int*)`, `print(0)` selects the int overload and `print(nullptr)` selects the pointer overload. `NULL` is an implementation-defined null pointer constant and can produce surprising overload resolution. An overload taking `std::nullptr_t` accepts expressions of that type, including variables of that type; an `int*` containing null still has type `int*`.

## Returning references and extending lifetimes

A returned reference or pointer is usable only while its referent remains valid. Returning an ordinary local object's address or reference leaves the caller with a dangling result. Returning a reference parameter or a member can be safe, but only if the original argument or containing object lives long enough. A static local outlives the call, though exposing mutable static state creates sharing concerns. The concrete trap is a function like `const int& getNextId()` that increments a static counter and returns a reference to it. If the caller writes `const int& id1{ getNextId() };` and then `const int& id2{ getNextId() };`, both references alias the same static object, so printing them gives "22" rather than "12". Copying instead, `const int id1{ getNextId() };`, snapshots the value at the time of the call and gives "12". Whether the caller copies or binds is decided by the caller's declaration, not by the function's return type.

Eligible reference initialization can extend a temporary's lifetime, but returning a reference to an argument does not extend that argument again. A temporary passed to a reference parameter normally dies at the end of the full expression containing the call. Copying a value from the returned reference before then can be safe; copying from an already dangling reference is not.

The two-argument `std::min` and `std::max` return a const reference and choose the first argument on ties. In `const int& r = std::max(a, b + 1);`, r dangles after the statement if the temporary is selected. If a value is wanted, storing the result by value avoids retaining that reference.

A non-const reference return permits assignment through the call expression, as with a container's `operator[]`. This is useful only when the lifetime and mutation contract are clear.

## Array decay and pointer arithmetic

An array often converts to a pointer to its first element, but taking the address of the array produces a pointer to the entire array. For `int x[5]`, `x + 1` advances one int, whereas `&x + 1` advances one array of five ints. Assuming four-byte ints, these correspond to offsets of four and twenty bytes from the start. The conceptual offset zero in a quiz is not a real object at the null address.

Pointer arithmetic follows the pointed-to type, not the pointer's own size. It must also remain within the permitted array range, including the one-past position. The one-past pointer can be formed but cannot be dereferenced to access an element. `sizeof(x)` measures the full array, while `sizeof(x + 0)` measures a pointer.

For main's argument array, `argv[argc]` is guaranteed to be null. This allows terminator-based traversal, although `argc` is usually the clearest bound.

## unique_ptr and ownership transfer

A `std::unique_ptr<T>` owns its current pointee. Moving it into a by-value parameter transfers ownership to that parameter and leaves the source empty. The pointee is destroyed if that owner is destroyed without releasing or transferring it first. Its original creation scope does not determine its destruction time.

Parameter destruction timing is implementation-defined: it can occur when the function exits or at the end of the enclosing full expression. If the ownership-taking call is one statement and the next print is another statement, the owned object has been destroyed before the next print. Do not use that reasoning for a later insertion in the same full expression without considering the timing rule. See [parameter destruction](https://timsong-cpp.github.io/cppwp/n4950/expr.call).

Taking `const std::unique_ptr<T>&` does not transfer ownership. If the function only needs the pointee, `T&` or `const T&` often expresses borrowing more directly without coupling the API to an ownership wrapper.

## Additional syntax examples

These are independent syntax sketches, including deliberately invalid examples marked `CE` (compile error). They are not one compilable program.

```cpp
int x{5};
int* ptr{ &x };     // & = address-of
*ptr = 6;           // * = dereference, yields lvalue → x == 6
int* p1, * p2;      // star per name; `int* p1, p2` makes p2 an int

int* pn{};          // value-init → nullptr
if (pn) { }         // null check via bool conversion

const int* a{};        // ptr-to-const: *a = 1 CE, a = &y ok
int* const b{ &x };    // const ptr: b = &y CE, *b = 1 ok; must init
const int* const c{ &x };

int foo(int);
int (*fp)(int){ foo };    // decay; &foo also fine
(*fp)(5);  fp(5);         // same call
using CmpFn = bool(*)(int,int);
void selectionSort(int* arr, int size, CmpFn cmp);
auto fp2{ &foo };

void f(int x = 0);
void (*fpd)(int){ f };  // fpd() CE — defaults don't travel through pointers

void nullify(int*& refptr) { refptr = nullptr; }  // reseats caller's ptr
// int&* — CE: no pointer to reference

void print(int) ; void print(int*);
print(0);        // int
print(NULL);     // impl-defined / possibly ambiguous
print(nullptr);  // int*
void print(std::nullptr_t);  // Accepts std::nullptr_t expressions;
int* pv{nullptr}; print(pv); // still int* (types, not values)

void safe(const int* ptr) { assert(ptr); if (!ptr) return; /* use *ptr */ }

int x[5]{0,1,2,3,4};       // Offsets from the array start, assuming sizeof(int)==4:
// &x + 1 advances 20 bytes   (int(*)[5]: strides sizeof(int[5]))
// x  + 1 advances 4 bytes    (decayed int*: strides sizeof(int))
// sizeof(x) == 20; sizeof(x + 0) is typically 8 on x86-64.

void hello();
std::cout << hello;        // 1 — fp→bool (no void* conversion for fps)
std::cout << reinterpret_cast<void*>(&hello);  // the address (cond.-supported)

for (char** p = argv; *p; ++p)   // argv[argc] == 0, guaranteed
    std::cout << *p << '\n';

// references
int v1{5}, v2{6};
int& r{ v1 };
r = v2;              // v1 = 6; NO rebind — references never reseat
// int& bad;         // CE: must initialize
// int& bad2{ 5 };   // CE: non-const ref can't bind rvalue

short s{ 3 };
const int& cr{ s };  // conversion → binds a TEMPORARY int(3)
s = 42;              // cr still 3 — watching a snapshot, not s

const int& ext{ 5 };            // lifetime-extended: fine for ext's whole life
const int& bounce(const int& x) { return x; }
const int& dang{ bounce(5) };   // DANGLING: extension doesn't cross a return

int& maxRef(int& a, int& b) { return (a > b) ? a : b; }
maxRef(v1, v2) = 7;             // call is an lvalue: writes the bigger one

void getSinCos(double deg, double& sinOut, double& cosOut);  // out-param style: avoid
```

## Interview Q&A

### How do pointers and references differ?

A pointer is an object I can reassign, and it can represent no target using null. A reference is an alias that I bind during initialization and cannot rebind. Assigning through a reference changes the referred object. Both require me to ensure that the target remains alive before I use it.

A reference expresses a required object and must be initialized, which rules out some mistakes that a pointer permits. It does not prove validity: I can still create a reference through an invalid pointer or keep one after its object dies. Pointers also need care with initialization, null values, and arithmetic. Neither form manages the target's lifetime by itself.

### Does a const reference mean the object cannot change?

It only prevents modification through that reference. If the object itself is non-const, another alias can modify it and I will see the change. Also, a binding that performs a conversion can refer to a temporary copy instead of the original object.

### When would you pass a pointer instead of a reference?

I use a pointer when absence is meaningful or the API needs pointer-specific behavior. A reference usually expresses a required object more clearly. For a small cheap value, passing by value may be simpler than either option. I make ownership and lifetime expectations explicit in all three cases.

### Why does changing a pointer parameter not change my pointer?

The parameter is a copy of the pointer value. Writing through it can change the shared pointee, but assigning a new address changes only that local copy. To reassign the caller's pointer, the function needs a reference to the pointer or another explicit output mechanism.

### What is special about nullptr?

It has its own type, std::nullptr_t, and converts to null pointer values without behaving like an ordinary integer argument. That avoids the common overload problem with zero or NULL. A pointer variable holding null still participates in overload resolution according to its pointer type.

### Why do x + 1 and &x + 1 advance different distances for an array?

In the first expression, x decays to a pointer to an element. In the second, taking the address preserves the whole array type as the pointee. Adding one advances by one pointed-to object, so the first advances an element and the second advances the entire array.

### When is an object destroyed after moving its unique_ptr into a function?

Ownership has moved to the function's parameter, so I track that owner next. If it keeps ownership until destruction, destroying the parameter deletes the object. The parameter may be destroyed at function exit or at the end of the full expression, and the original pointer is empty after the move.

### Can returning a const reference keep a temporary alive?

Returning the reference does not extend the temporary's lifetime again. If it was an argument temporary, it normally expires at the end of the full expression containing the call. I can consume it while it is alive, but retaining the returned reference can leave it dangling.

## Practice history

The entries below preserve the original practice record. Use the explanations above for the current rules and qualifications. In particular, “at function return” in the old ownership card must be qualified: parameter destruction may occur at function exit or at the end of the full expression. The original quiz snippet must be checked before claiming a fixed print order within one full expression.

### Questions (getcracked) / Quiz log

- [x] &x + 1 vs x + 1 (array at 0, sizeof(int)=4) — 02/09 — ok (20, 4). Note gc's own explanation said "size of the pointer" for op two; correct reasoning is size of the POINTEE.
- [x] In one out the other (int& + const int& aliasing same var) — 02/09 — ok (prints 1).
- [x] East to West (`const int_ptr foo` vs `const int* bar`) — 07/09 — ok. `foo` is `int* const` (const on an alias is top-level on the whole aliased type), `bar` is `const int*`. Same fact as the 29/08 quiz miss "const alias = top-level const".
- [x] Triple-pointer array puzzle (`const char* c[]`, `char const** cp[]`, `char const*** cpp`) — 07/09 — ok: `MID s Exam OOP`. Method: track the pointer level, `[]` and `+` index within the current level, postfix `[]` binds before prefix `*`; the fourth dereference lands on a `char`, so one expression prints a single character.
- [ ] **MISSED 02/09: I'm moving in.** (unique_ptr by-value param) — answered 1342; A dies with the PARAM at end of x, not with p1 at end of main. Reason: tracked lifetime by where the object was created, not by who currently owns the pointer.
  - **Anki**: front: "`x(unique_ptr<A> ptr)` called with `std::move(p1)` — when does ~A run?" back: "When ptr (the param) is destroyed at x's return — ownership moved in; p1 is null and its dtor is a no-op. By-value unique_ptr param = sink; const& = borrow (then A dies with p1)."
