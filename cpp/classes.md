# Classes, Structs & Member Functions

## From procedures to objects

Procedural code keeps data and the functions that operate on it apart: an `AnimalType` enum plus a `numLegs(type)` switch and an `animalName(type)` switch. Every new animal touches the enum and every switch, so the change is spread across the whole program. Object-oriented code bundles the properties and the behavior into one program-defined type, so `you.eat(apple)` reads as subject, action, and accessory, and adding a `Snake` type means writing one new type rather than editing several functions. Object-oriented programming does not replace procedural style; it adds a tool for managing complexity when a type's data and behavior belong together. The later pillars (encapsulation, inheritance, abstraction, polymorphism) all build on this packaging.

The word "object" is overloaded. In the core language an object is any region of storage with a type; in the object-oriented sense it is an instance of a class type that carries both state and behavior. The notes say "class object" when the second meaning matters.

## Class invariants and why classes exist

A class invariant is a condition that must hold for the whole lifetime of an object for it to be valid. A `Fraction` with `denominator == 0` violates its invariant; an `Employee` whose `firstInitial` no longer matches the first character of `name` violates a correlated invariant. A plain struct with public members cannot enforce either: `Fraction f{5, 0};` compiles, and any code that later touches `name` can forget `firstInitial`. Relying on every user of a type to maintain its invariants is the failure mode classes are designed to remove: private data plus member functions that are the only path for modification, so the invariant is checked in one place.

Technically a struct and a class are almost the same thing. Both are class types, both can have member functions, constructors, access specifiers, and inheritance. The only language differences are the defaults: members and base classes of a `struct` are public unless stated otherwise, and those of a `class` are private. Everything else is convention. Use `struct` for a bundle of data with no invariant, typically an aggregate with public members and no constructors. Use `class` when the type has an invariant to protect, which usually means private data, a constructor that establishes the invariant, and member functions that preserve it. Most of the standard library is classes; `std::string` and `std::string_view` are classes even though they are used as if they were built-in types.

The two keywords are interchangeable for naming the same type. `class A;` followed by `struct A {};` is one entity, and the definition's keyword decides the access defaults, so the members of that `A` are public. The standard requires the class-key of a forward declaration to "agree in kind" with the definition, but `class` and `struct` are the same kind for that rule; only `union` is a different kind, so `union A;` followed by `struct A {};` is ill-formed. Clang warns about a `class`/`struct` mismatch under `-Wmismatched-tags`, and old MSVC warned with C4099 because it once encoded the keyword into mangled names, which is why style guides still discourage the mismatch even though the language permits it.

```cpp
class A;            // forward declaration
struct A { };       // definition: same entity, members public

int main() {
    A a;            // fine
}
```

## Member functions and the implicit object

A member function is a function declared inside a class type (struct, class, or union). Functions declared outside are non-member functions. Other languages say "method"; in C++ that word is informal. A member function must be declared inside the class definition and may be defined either inside it or outside with a qualified name such as `void Date::print()`. A member function defined inside the class is implicitly `inline`, which is why a class definition with in-body member functions can live in a header without violating the one-definition rule.

When `today.print()` runs, `today` is the implicit object: it is passed to the function without appearing in the parameter list. Inside the body, an unqualified member name refers to that object's member, so `year` in `print` means `today.year`. The compiler implements this with a hidden pointer parameter, and `this` names it explicitly. `this->year` and plain `year` are the same thing; `this` is useful when a parameter shadows a member, when returning the object for chaining (`return *this;`), or when the object's address must be passed elsewhere.

```cpp
struct Person {
    std::string name{};
    int age{};

    void kisses(const Person& person) {
        std::cout << name << " kisses " << person.name << '\n';
    }
};

Person joe{"Joe", 29};
Person kate{"Kate", 27};
joe.kisses(kate);     // "Joe kisses Kate": name is joe's, person.name is kate's
```

Compare the non-member form `kisses(joe, kate)`, where the subject is one more argument among the others and every member access has to be qualified. The member form makes the initiating object explicit at the call site and implicit in the body.

Unlike a free function, a member function may use members that are declared later in the class, because the whole class body is treated as if member function bodies were compiled after all declarations. This applies to member function bodies and default arguments, not to default member initializers. Data members are initialized in declaration order regardless of how the initializers are written, so an earlier member's default initializer that reads a later member reads an object that does not exist yet, which is undefined behavior.

```cpp
struct Foo {
    int z() { return m_data; }   // fine: bodies see later members
    int m_data{};
};

struct Bad {
    int m_bad1{ m_data };        // UB: m_data is initialized after m_bad1
    int m_data{ 5 };
};
```

Two conventions follow from the struct-versus-class split. A struct should avoid declaring constructors, because a user-declared constructor makes the type a non-aggregate and removes aggregate initialization. A type with member functions but no data members is better written as a namespace, which says clearly that there is no state and does not require instantiating an object to call anything.

## Const objects and const member functions

A const object of class type must be initialized when created and cannot be modified afterwards, so `const Date today{2020, 10, 14};` is fine while `today.day += 1;` is an error. The rule extends to member functions: a const object may only call member functions marked `const` after the parameter list, because the compiler cannot tell from outside whether an unmarked function modifies the object. `today.print()` fails on a const `today` if `print` is not const, even when the body only reads. Passing by const reference has the same effect inside the callee, so a `void doSomething(const Date& d)` can only call const members of `d`. Since almost every type is at some point handled through a `const T&`, a class whose readers are not const is unusable in practice.

Inside a const member function `this` has type `const X*`. The function cannot modify a data member, cannot call a non-const member function on the implicit object, and cannot return a non-const reference to a member. It can still modify locals and parameters, call other const members, and call non-member functions. A `mutable` member is exempt and may be modified from a const member function; it exists for caches, counters, and mutexes that are not part of the logical state. A const member function is callable on both const and non-const objects, so mark every member that does not modify the observable state as `const`.

A member may be overloaded on constness alone. The compiler picks by the implicit object: a non-const object calls the non-const overload, a const object the const one. The common use is a pair of accessors where the return type differs, a `T&` from the non-const version and a `const T&` from the const version, rather than two bodies that print different things.

```cpp
struct Something {
    void print()       { std::cout << "non-const\n"; }
    void print() const { std::cout << "const\n"; }
};

Something s1{};
s1.print();             // non-const
const Something s2{};
s2.print();             // const
```

Only the object's constness matters here, not its value category, so `X{}.f()` can call a non-const `f` on the temporary. Ref-qualifiers, below, are the tool for constraining the value category.

## Access specifiers and data hiding

Every member has one of three access levels. Public members can be used by anyone. Private members can be used only by other members of the same class. Protected members can be used by members of the class and of classes derived from it, but not by outside code. The access specifiers `public:`, `private:`, and `protected:` set the level for everything that follows them in the class body; they may appear any number of times and in any order. The only technical difference between the keywords `struct` and `class` is the default before the first specifier: public for a struct, private for a class. The presence of a private member also makes the type a non-aggregate, so it loses aggregate initialization.

Access is checked per class, not per object. A member function of `Person` may read and write the private members of any other `Person` it can name, which is why a member `bool isEqual(const Point3d& p) const` can compare `m_x == p.m_x` directly and why copy constructors and comparison operators can be written as members without accessors.

```cpp
class Person {
private:
    std::string m_name{};
public:
    void setName(std::string_view name) { m_name = name; }
    void kisses(const Person& p) const {
        std::cout << m_name << " kisses " << p.m_name << '\n';   // p's private member: fine
    }
};
```

Data hiding is the practice of keeping the implementation of a type out of reach of its users: data members private, member functions public, so the only way in is through the public interface. Encapsulation is the broader word for bundling data with the functions that operate on it; in C++ usage a class that bundles data behind a public interface and hides the data is called encapsulated. The public interface is an implicit contract: users build on it, so changing it breaks them, while the private implementation can change freely.

The benefits are concrete rather than aesthetic. Users only need to understand the interface, not the internals of `std::string_view` to call `length()`. Invariants live in one place: an `Employee` whose `m_firstInitial` must track `m_name` keeps both private and updates them together in `setName`, so no outside code can desynchronize them. Validation and error handling become possible: a setter can reject an empty name before `front()` becomes undefined behavior. The representation can change, from three named `int` members to an array of three, without touching any caller that used `setValue1` and `getValue1`. And debugging narrows to one place: if a member holds a bad value, the only code that can have written it is the class's own members.

Two conventions follow. Declare the public interface first and the private implementation last, so a reader sees what the class does before how; the older private-first style is common in existing code. Private data members carry an `m_` prefix so they never collide with parameters, locals, or accessor names, and so a read of `m_name` in a body is visibly a read of persistent state.

## Access functions, and preferring non-member functions

An access function is a public member that reads or writes a private data member: a getter, which returns the value and should be `const`, or a setter, which modifies it and is not. Three naming styles are in use: `getDay` and `setDay`; the standard library's bare `day()` for both the getter and an overloaded setter; or a bare `day()` getter with a `setDay` setter, which learncpp recommends because the `set` prefix marks mutation while the getter reads naturally. The `m_` prefix on the member is what makes a bare `day()` getter possible without a name clash.

Access functions are not automatically good design. A `setAlive(bool)` says less than `kill()` and `revive()`; behavior-named members express intent and can enforce transitions. If a type needs a getter and a setter for every member with no validation in between, it is probably a struct with public members that has been dressed up. Provide access only for what outside code genuinely needs.

Prefer non-member functions when a function can be written against the public interface. A `print(const Yogurt&)` free function that uses `getFlavor()` keeps the class interface small, cannot bypass encapsulation, is unaffected by changes to the private representation, and lets each application format output its own way instead of baking one format into the class. Member functions are required for constructors, destructors, virtual functions, and some operators, and are the right choice when the function needs private access that should not be exposed; otherwise, especially for functions that do not modify state, reach for a non-member.

## Returning references to data members

A getter that returns a `std::string` by value copies the string on every call. Returning `const std::string&` avoids the copy and is safe in the common case, because the implicit object outlives the call: the member lives inside the object, and the object lives in the caller's scope. Match the return type to the member's type. Returning `std::string_view` from a `std::string` member works but creates a view of the member on every call, and returning `const auto&` deduces the right type but hides it from the reader, so `const std::string& getName() const` is the form to write.

The safety argument depends on the implicit object being an lvalue. When the object is a temporary, the member dies with it at the end of the full expression, and a saved reference dangles.

```cpp
Employee createEmployee(std::string_view name);   // returns by value

std::cout << createEmployee("Frank").getName();               // fine: used in the same expression
const std::string& ref{ createEmployee("Garbo").getName() };  // dangling: the temporary is gone
std::string val{ createEmployee("Hans").getName() };          // fine: copied before the temporary dies
```

The rule is to use the result of a reference-returning member immediately, or copy it into a non-reference variable if it must outlive the expression. This is the same lifetime rule as any function returning a reference into an object that may not outlive the caller's use, and the ref-qualified overload pattern earlier in this file is the class-side fix: a `&&` overload that returns by value or moves out, so a temporary never hands out a reference into itself.

Never return a non-const reference to a private member from a public function. `int& value() { return m_value; }` lets any caller write `f.value() = 5;`, which is public access to a private member with extra steps and defeats every benefit of data hiding. A const member function cannot return a non-const reference to a member at all, because `this` is a `const X*` and the member is const through it; `const int& getValue() const` is the version that compiles.

## What can overload a member function

A function is identified by its name plus its signature, and a member function's signature has more parts than a free function's. Each of the following can differ between two member functions with the same name and produce a distinct overload:

1. The number of parameters.
2. The types of the parameters. Top-level const on a parameter is not part of the signature, so `void foo(int)` and `void foo(const int)` declare the same function, and defining both is a redefinition error. Const behind a reference or pointer is part of the type, so `void foo(int&)` and `void foo(const int&)` are distinct overloads.
3. The cv-qualifier after the parameter list, meaning `const` and, in principle, `volatile`. Overloading on `const` is common: a const overload returning a `const T&` and a non-const overload returning a `T&`.
4. The ref-qualifier, `&` or `&&`, which constrains the value category of the implicit object.

Interview answers usually count four aspects; `volatile` member functions are legal but so rare that most people fold them into the cv-qualifier bullet. What cannot overload: the return type alone, `noexcept`, default arguments, and top-level const on parameters. A `static` member function has no implicit object, so it cannot carry cv-qualifiers or ref-qualifiers and cannot be overloaded with a non-static member function of the same signature.

```cpp
class A {
    void foo(const int i) const &&;   // one overload: (int), const, rvalue-only
    void foo(int i) const &;          // distinct: lvalue-only
    void foo(int i) &;                // distinct: non-const lvalue
    void foo(long i) const &&;        // distinct: different parameter type
    void foo(int i, int j) const &&;  // distinct: different arity
    // void foo(int i) const &&;      // error: same signature as the first (top-level const dropped)
};
```

### What must match between a declaration and an out-of-class definition

The header holds the declaration inside the class and the implementation file holds the definition with a qualified name. The two must agree on everything that is part of the signature or the function type: the parameter types after top-level const is stripped, the cv-qualifier, the ref-qualifier, and the exception specification. Three things may differ or be dropped without changing which function is being defined:

- **Parameter names.** They are not part of the signature. The definition may rename them or omit any it does not use, so `int A::add(int, int) const &&` is a valid definition of a member declared with named parameters.
- **Top-level const on parameters.** `const int a` and `int a` are the same parameter type, and so are `int* const p` and `int* p`, because the const applies to the parameter object itself rather than to what it refers to. Whether to keep the const in the definition is a body-only choice about whether the parameter may be reassigned. Const that sits under a reference or pointer, as in `const int&` or `const int*`, is part of the type and must match.
- **Default arguments.** A default argument is a property of a declaration, not of the function, and each parameter may receive its default exactly once in a given scope. Repeating `= 3` in the definition is an error even though the value is identical. The default belongs in the header, where every caller can see it; a default written only in the implementation file would be invisible to code that includes the header. A definition may add a default for a parameter that had none, though that is a maintenance trap, and defaults must be trailing: once a parameter has a default, every parameter after it needs one.

```cpp
// a.hpp
struct A {
    int add(const int a, const int b = 3) const &&;
};

// a.cpp
int A::add(int a, int b) const && {     // const dropped, default dropped, same function
    const auto c = a + b;
    return c;
}
// int A::add(int a, int b = 3) const && {}   // error: default argument repeated
// int A::add(int a, int b) const &  {}       // error: ref-qualifier differs, no such member declared
```

A stray semicolon after the closing brace of a function definition is an empty declaration, allowed at namespace scope since C++11 and harmless, though some compilers warn under `-Wextra-semi`.

## Ref-qualifiers

A ref-qualifier restricts the value category of the implicit object. A member function declared with `&` after the parameter list can only be called on an lvalue, and one declared with `&&` can only be called on an rvalue, typically a temporary or a moved-from expression. A member function with no ref-qualifier accepts both. Within one overload set with the same parameter list and cv-qualifiers, either every overload has a ref-qualifier or none does; mixing `void f();` with `void f() &;` is an error.

The practical use is to make an expensive-to-copy member cheap to take from a temporary while still safe to read from a named object. `std::optional::value()` is overloaded four ways, `&`, `const&`, `&&`, and `const&&`, so `opt.value()` returns a reference into the named optional and `std::move(opt).value()` or `make_opt().value()` returns an rvalue reference that can be moved from. `const &&` is legal and exists in the library for completeness, but it is rare in hand-written code because a const rvalue cannot be moved from anyway.

```cpp
struct Buffer {
    std::string data;
    const std::string& get() const & { return data; }     // named object: hand out a view
    std::string&&       get() &&      { return std::move(data); }  // temporary: hand over ownership
};

Buffer b;
auto& view = b.get();          // const& overload
std::string s = Buffer{}.get(); // && overload, moves out of the temporary
```

A `&&`-only member with no other overload is a design statement that the operation consumes the object. `void foo(const int) const &&` in the quiz above is exactly that: callable only on an rvalue `A`, and const because it does not modify it, which is a strange combination in practice but legal and a good test of whether you can read the signature.

## Pointers to member functions and std::invoke

Taking the address of a member function does not produce an ordinary function pointer, because the function needs an implicit object to run. `&X::foo` has type `void (X::*)(int)`, read as "pointer to member of `X` that is a function taking `int` and returning `void`". The `&X::name` spelling is required; `&x.foo` and plain `X::foo` are ill-formed. Const and ref-qualifiers are part of the type, so `&A::foo` for the `const &&` member above is `void (A::*)(int) const &&`. For an overloaded member the compiler cannot pick, so cast to the wanted type: `static_cast<void (X::*)(int)>(&X::foo)`. Pointers to data members exist too: `int X::* pm = &X::value;`.

Calling through a pointer to member needs an object and the `.*` or `->*` operator. Because those operators bind less tightly than the call operator, the parentheses are mandatory: `(x.*mf)(42)` for an object or reference and `(px->*mf)(42)` for a pointer. Writing `mf(x, 42)` is not valid, because `mf` is not a callable object; it is a member pointer that needs the special syntax. `x.*mf(42)` is also wrong, since it tries to call `mf(42)` first.

`std::invoke`, from `<functional>` in C++17, hides the syntax. `std::invoke(f, args...)` calls any callable with the convention that callable needs: a plain function or function pointer is called directly, a pointer to member function receives the first argument as the object (a reference, a `std::reference_wrapper`, a raw pointer, or anything that can be dereferenced with `*`, which includes smart pointers), and a pointer to data member returns the member. Generic code that accepts "any callable" should call through `std::invoke` rather than `f(args...)` so member pointers work. `std::mem_fn(&X::foo)` is the older tool with the same effect: it returns a function object `g` such that `g(x, 42)` works as a normal call.

```cpp
struct X {
    void foo(int);
    int value;
};

X x;
X* px = &x;
auto mf = &X::foo;           // void (X::*)(int)

(x.*mf)(42);                 // direct call through object
(px->*mf)(42);               // direct call through pointer
std::invoke(mf, x, 42);      // same, generic syntax
std::invoke(mf, px, 42);     // pointer works too
std::invoke(&X::value, x);   // reads x.value
auto g = std::mem_fn(&X::foo);
g(x, 42);                    // ordinary call syntax

// mf(x, 42);                // error: member pointer is not a callable object
```

One correction to a common example: `std::reference_wrapper` is itself callable. For `int f(int); std::reference_wrapper ref = f;`, both `ref(5)` and `std::invoke(ref, 5)` are valid, because `reference_wrapper::operator()` forwards to the wrapped callable. The case where `std::invoke` is genuinely needed is a pointer to member, or generic code that must accept both.

C++23 changes the picture with explicit object parameters. A member declared `void foo(this X& self, int)` takes its object as a visible first parameter, so `&X::foo` is an ordinary `void (*)(X&, int)` and `mf(x, 42)` becomes valid. That is one of the motivations for the feature: member functions that compose with ordinary function-pointer code without `std::invoke` or `std::mem_fn`.

On the Itanium ABI a pointer to member function is two words (a function address or vtable offset plus a `this` adjustment for multiple inheritance), so `sizeof(void (X::*)())` is 16 on x86-64 Linux, not 8. It is not convertible to `void*` and cannot be null-checked by casting; compare against `nullptr` directly.

## Errors and pitfalls

- **Invalid: redefining on top-level const.** `void foo(int);` and `void foo(const int);` declare one function. Two definitions are a redefinition error, and the parameter's const only affects the body of whichever definition exists.
- **Invalid: mixing ref-qualified and unqualified overloads.** `void f();` and `void f() &;` with the same parameters and cv-qualifiers cannot coexist.
- **Invalid: calling a non-const member on a const object.** `const X x; x.mutate();` is an error even though the body might not modify anything; the compiler trusts the declaration, not the body.
- **Invalid: calling a `&&` member on an lvalue.** `A a; a.foo(1);` where `foo` is `&&`-qualified is an error; `std::move(a).foo(1)` or `A{}.foo(1)` is required.
- **Invalid: `mf(x, 42)` on a pointer to member.** Use `(x.*mf)(42)` or `std::invoke(mf, x, 42)`.
- **Invalid: the most vexing parse.** `Y y(X());` declares a function named `y` returning `Y` and taking a pointer to a function returning `X`. Nothing prints, and the error surfaces later at `y.f()`, where `y` is a function, not a `Y`. See [initialization_deduction.md](initialization_deduction.md) for the rule and the fixes; `Y y{X{}};` is the idiomatic one.
- **Undefined behavior: default member initializer reading a later member.** Members initialize in declaration order, so `int a{ b }; int b{ 5 };` reads an uninitialized `b`.
- **Invalid: returning a non-const reference from a const member function.** `int& get() const` fails because the member is const through `this`; return `const int&`.
- **Undefined behavior: saving a reference returned from a member of a temporary.** `const auto& r = make().name();` dangles at the semicolon; use it in the same expression or copy it.
- **Design error: public non-const reference to a private member.** `int& value()` is a public member with extra steps.
- **Logical error: forgetting `const` on an accessor.** The class works until someone holds a `const X&`, at which point every read becomes a compile error somewhere far from the class.
- **Design error: constructor on a struct meant as an aggregate.** Adding a constructor silently removes aggregate initialization and designated initializers.

## Additional syntax examples

```cpp
// Definition outside the class; the class body still holds the declaration.
struct Date {
    int year{}, month{}, day{};
    void print() const;
    void print(std::string_view prefix) const;   // overload on parameter list
};

void Date::print() const { std::cout << year << '/' << month << '/' << day; }
void Date::print(std::string_view prefix) const { std::cout << prefix; print(); }

// const / non-const accessor pair.
struct Box {
    int v{};
    int&       value()       { return v; }
    const int& value() const { return v; }
};

// Chaining through *this.
struct Builder {
    std::string s;
    Builder& add(std::string_view part) & { s += part; return *this; }
    Builder&& add(std::string_view part) && { s += part; return std::move(*this); }
};

// Pointer to member function type spelled out, and a typedef for it.
using Handler = void (X::*)(int);
Handler h = &X::foo;

// Explicit object parameter, C++23.
struct Counter {
    int n{};
    void bump(this Counter& self) { ++self.n; }
};
```

## Interview Q&A

### Does `class A; struct A {};` compile, and is `A` a struct or a class?

It compiles. Struct and class are the same kind of entity and the keywords are interchangeable for the same type; only the defaults for member and base access differ, and those come from the definition, so this `A` has public members. The standard's "agree in kind" rule for forward declarations treats `class` and `struct` as one kind and only `union` as another. Compilers may warn about the mismatch, and MSVC historically cared because it mangled the keyword, which is why style guides discourage it.

### How many ways can a member function be overloaded?

Four in the usual count: the number of parameters, the parameter types with top-level const ignored, the cv-qualifier after the parameter list, and the ref-qualifier. Return type alone, `noexcept`, and default arguments do not create overloads. If pressed, `volatile` is a second cv-qualifier and technically a separate axis, and `static` versus non-static cannot coexist for the same signature.

### What does `void foo(const int) const &&` mean?

A member function taking an `int` by value, whose top-level const only matters inside the body, that promises not to modify the object, and that can only be called on an rvalue `A`. So `A{}.foo(1)` and `std::move(a).foo(1)` compile, and `a.foo(1)` on a named `a` does not. It is an unusual combination because a const rvalue cannot be moved from, but it is legal and a good test of reading a declaration from right to left.

### Why does `Y y(X());` not construct a `Y`?

Because anything that can be parsed as a function declaration is. `X()` in that position is a parameter of type "function returning `X`", which adjusts to a pointer to function, so `y` is declared as a function taking `X(*)()` and returning `Y`. No object is created, nothing prints, and the program fails to compile at `y.f()` because a function has no members. Braces fix it: `Y y{X{}};` cannot be a function declaration. Extra parentheses, `Y y((X()));`, or `auto y = Y(X());` also work. With the fix the output is `XYf`.

### How do you call through a pointer to member function, and why does `mf(x, 42)` fail?

`mf` is a pointer to member, not a callable, so it needs an object and the member-pointer call operator: `(x.*mf)(42)` or `(px->*mf)(42)`, with the parentheses because `.*` binds looser than the call. `std::invoke(mf, x, 42)` does the same thing with uniform syntax and also accepts a pointer, a `reference_wrapper`, or a smart pointer as the object, which is why generic code should always call through `std::invoke`. `std::mem_fn(mf)` produces a normal function object for the same purpose. In C++23 a member with an explicit object parameter decays to an ordinary function pointer, and then `mf(x, 42)` is valid.

### When do you reach for ref-qualifiers?

When the same operation should behave differently on a temporary and on a named object, most often to move a member out of a temporary while returning a reference from an lvalue, as `std::optional::value()` does. Also to make an operation consume-only with a `&&`-only overload, so calling it on a named object is a compile error rather than a silent use-after-move later.

### Can a member function access the private members of another object of the same class?

Yes. Access control is per class, not per object. Any member function of `Person` can read and write `m_name` on any `Person` it holds a reference or pointer to, which is what makes member comparisons, copy constructors, and swaps writable without accessors. Access is about which code may touch a member, not which instance owns it.

### Should a getter return by value or by reference?

By value when the member is cheap to copy, such as an `int`. By `const T&` when it is expensive, such as a `std::string`, with the return type matching the member's type exactly. The reference is safe as long as it is used while the object is alive, so use it in the same expression or copy it out; saving a reference obtained from a temporary dangles at the end of the full expression. Never return a non-const reference to a private member, since that is public write access in disguise.

### What is the difference between data hiding and encapsulation?

Encapsulation is bundling data with the functions that operate on it into one type. Data hiding is making the data private so the only path in is the public interface. A class that does both is what people mean by an encapsulated class in C++. The payoff is that invariants are enforced in one place, validation is possible, the representation can change without breaking callers, and a bad value can only have been written by the class's own code.

## Practice history

- 12/09/2026: read learncpp 14.1 (intro to OOP), 14.2 (intro to classes), 14.3 (member functions), 14.4 (const objects and const member functions), 14.5 (access specifiers), 14.6 (access functions), 14.7 (returning references to data members), 14.8 (data hiding and encapsulation).
- 12/09/2026 getcracked: Class inStruction (`class A; struct A {}` compiles, definition sets access) ok. X ways (four overload aspects incl. ref-qualifier) ok. Haha… (`Y y(X());` most vexing parse, compilation error at `y.f()`) ok. Invoke me. (`mf(x, 42)` invalid; `(x.*mf)(42)` or `std::invoke`) ok. Note for the platform's explanation of Invoke me.: `std::reference_wrapper` is callable, so its `ref(5)` "Wrong" example is itself wrong. Drop these. (out-of-class definition may drop top-level parameter const and the default argument) ok; the platform's explanation lists `int* const` as const that must match, but that is top-level const on the parameter and is dropped from the signature like `const int`; only `const int*` and `const int&` are part of the type.
- Anki: top-level const on a parameter (including `int* const`) is not part of the signature; a default argument is given once, in the declaration; `.*` needs parentheses around the call; `&&`-qualified member is rvalue-only; members initialize in declaration order.

<!-- gc-questions:start -->

## Related getcracked questions

Pulled from the Beginner C++ progress tree. ✓ answered correctly, ✗ attempted and missed, ○ not attempted yet. Regenerate with `python3 cpp/tools/gc_links.py` after re-scraping.

### Classes and Structs
- ○ [Class vs Struct](https://getcracked.io/question/372) — Cooked
- ○ [Class inStruction](https://getcracked.io/question/1329) — Easy
- ○ [Struct over Class](https://getcracked.io/question/373) — Easy
- ○ [wtf const](https://getcracked.io/question/969) — Medium

### Member Functions
- ○ [Invoke me.](https://getcracked.io/question/1398) — Easy
- ○ [skibidi pointer](https://getcracked.io/question/1265) — Easy
- ○ [X ways](https://getcracked.io/question/1062) — Easy
- ○ [Haha…](https://getcracked.io/question/802) — Medium

### Const Classes and Functions & Access Specifiers
- ○ [& and &&](https://getcracked.io/question/827) — Cooked
- ○ [Drop these.](https://getcracked.io/question/1066) — Medium

<!-- gc-questions:end -->
