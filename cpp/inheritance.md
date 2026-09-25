# Inheritance: Construction Order, Access, Hiding, Virtual Functions, override/final, vtables, Abstract Classes & Virtual Bases

## Derived objects and base pointers

A derived object is built from parts: one subobject for each base class, constructed first, and the derived part constructed last, destroyed in the reverse order. Because a `Derived` is-a `Base`, a `Base&` or `Base*` may refer to the base part of a `Derived` object. What such a reference can see is fixed by its static type: through a `Base&` only the members of `Base` are visible, so a `Derived::getName()` that hides `Base::getName()` is not reachable, and a member that exists only in `Derived` cannot be called at all. That is the limitation that virtual functions remove, and it is also why base references are useful in the first place: one function taking `const Animal&` accepts every current and future animal, and one array of `Animal*` can hold a mixed population, where a template parameter would neither document nor enforce that the argument is an `Animal`.

## Order of construction and destruction

Inheritance models is-a; composition models has-a. `class Derived : public Base` makes every `Derived` object a `Base` part followed by a `Derived` part, and the parts are built in that order: most-base first, most-derived last, so that by the time a derived constructor body runs every inherited member already exists. For a chain `A <- B <- C <- D`, `D d;` runs the constructors `A`, `B`, `C`, `D`, and the destructors in exact reverse, `~D`, `~C`, `~B`, `~A`. Within one class the same rule applies to members: bases first, then data members in declaration order, then the body. So a class `X` with a member `Z z;` prints `zx` on construction and `XZ` on destruction, and a class `X : public Z` prints the same `zxXZ`. The full sequence when `Derived d{1.3, 5};` is instantiated: memory for the whole object is set aside, the derived constructor is entered, the base constructor named in its initializer list runs (the default one if none is named), the derived member initializer list runs, the derived body runs, control returns.

A derived constructor cannot initialize a base member in its member initializer list. `Derived(double cost, int id) : m_cost{cost}, m_id{id} {}` is a compile error, because only the class that owns a member may initialize it, and the base part is already fully constructed when the derived list runs; allowing it would let const and reference base members be rewritten. The fix is to name the base constructor in the list, `Derived(double cost, int id) : Base{ id }, m_cost{ cost } {}`, which runs first wherever it is written. Assigning `m_id = id;` in the body compiles when the member is accessible, but it is assignment after construction, fails for const and reference members, and does the work twice. Each constructor may name only its immediate base; `C(...) : A{...}` two levels up is an error, except for a virtual base, covered below. With base members initialized through the base constructor, they can be private, and a base that should only be built as part of a derived object gets protected constructors.

Two consequences the platform tests. Objects with static storage duration are constructed before `main` and destroyed after it in reverse order of construction, so with a global `Z z;` and locals `X x; Y y;` in `main`, the output is `zxyYXZ`. And a function-local static is constructed the first time control passes through its declaration; if that constructor throws, the object does not count as initialized and construction is attempted again on the next pass. With `void foo() { static X x; }` where `X` holds a `Z` whose constructor prints `z` and throws on the first call, `foo()` inside a `try` prints `z`, the `X` body never runs and no destructor runs because nothing finished constructing, the handler prints `y`, the second `foo()` prints `zx`, and at exit the static is destroyed, `XZ`: `zyzxXZ`.

```cpp
class Base { public: int m_id{}; Base(int id = 0) : m_id{ id } {} };
class Derived : public Base {
    double m_cost{};
public:
    Derived(double cost = 0.0, int id = 0) : Base{ id }, m_cost{ cost } {}   // Base first, always
    // Derived(double cost, int id) : m_cost{ cost }, m_id{ id } {}          // error: m_id belongs to Base
};
```

## Inheritance and access specifiers

`public` members are open to everyone, `private` to the class and its friends, and `protected` to the class, its friends, and its derived classes, but not to the public. A derived class may use the public and protected members it inherits and can never touch the private ones, whatever the inheritance type. The inheritance type, `public`, `protected`, or `private` after the colon, changes how those members look to code outside, and to classes derived further down: public inheritance keeps every access as it was; protected inheritance makes public and protected members protected; private inheritance makes both private. Private base members stay inaccessible in every case. A `class` that omits the inheritance type inherits privately; a `struct` inherits publicly; always write it out. The rule for reading any access question is that access is decided by the static type through which the member is reached: `Base b; b.m_public = 1;` is fine even if some `Derived` inherits privately, and a `Derived` that privately inherits can still call a protected base function from inside its own member functions. So `class B : private A` with `A` holding a protected `Private()` and `B` calling it from a public member compiles and prints as expected. Private inheritance says the base is an implementation detail rather than an is-a; composition usually says it better.

| base member | public inheritance | protected inheritance | private inheritance |
|---|---|---|---|
| public | public | protected | private |
| protected | protected | protected | private |
| private | inaccessible | inaccessible | inaccessible |

Prefer private members with accessors over protected members. Protected couples every derived class to the base's representation, so a change to the base breaks them all; use it only when the derived classes are few and under the same control.

Access is also checked against the static type for virtual calls. A derived class may override a public virtual function in its private section, and a call through a `Base&` still reaches that override, because the compiler checks access on `Base::foo`, which is public, and dispatch then runs `X::foo`. With `class X : public Z { private: void foo() override; }` and `void goo(Z& z) { z.foo(); }`, `goo(x)` prints `X`. Access specifiers restrict names, not the functions behind them.

## Adding, redefining, and hiding inherited functionality

A derived class adds members by declaring them. The relationship is one-way: a `Base` object, or a `Base&` before virtual functions enter, knows nothing about members added in `Derived`, so `Base b; b.getValue();` fails when `getValue` lives in `Derived`. Redefining an inherited non-virtual function is declaring one with the same name in the derived class; through a `Derived` object the derived version runs, through a `Base&` the base version, and the redefinition takes the access of the section it is declared in, not the base's. To extend rather than replace, call the base version explicitly, `Base::identify();`; an unqualified `identify()` inside `Derived::identify` calls itself forever. A friend such as `operator<<` cannot be scope-qualified, so the derived operator prints the base part by casting, `out << static_cast<const Base&>(d);`, to a reference so nothing is copied.

Name lookup stops at the first class, walking up from the most-derived, that has any member with that name, and overload resolution then happens only among that class's candidates. So one derived overload hides every base overload of the same name. `struct Foo { void Baz(double); }; struct Bar : Foo { void Baz(); };` makes `bar.Baz(42)` a compile error: lookup finds `Bar::Baz`, stops, and `Bar::Baz()` takes no argument. A using-declaration, `using Base::print;`, re-exposes every base overload alongside the derived ones, so `d.print(5)` picks `Base::print(int)` again. The same lookup rule makes a name that two bases both provide ambiguous: `struct C : A, B {}` where both `A` and `B` define `operator()` gives `f("hello")` a compile error even though only `B`'s overload could take a string, because lookup fails before overload resolution runs. Bring one in with `using B::operator();` or qualify.

Access of an inherited public or protected member can be changed with a using-declaration under the desired specifier, `public: using Base::printValue;`, for functions and variables alike, all overloads at once, and never for private base members. Placing `using Base::m_value;` under `private:` hides the member through `Derived`, but hiding is not encapsulation: `Base& b{ d }; b.m_value = 1;` still compiles, because the member is public in `Base`. A derived class may also delete an inherited function, `int getValue() const = delete;`, which makes `d.getValue()` an error while `d.Base::getValue()` and `static_cast<Base&>(d).getValue()` still work. The derived class only controls what the object looks like when viewed as a `Derived`.

```cpp
struct Foo { void Baz(double x) { std::cout << "I'm Foo! " << x; } };
struct Bar : Foo { void Baz() { std::cout << "I'm Bar!"; } };
Bar bar; bar.Baz(42);                                  // error: Bar::Baz hides Foo::Baz, takes no arguments

struct A { void operator()(int) const; };
struct B { void operator()(std::string) const; };
struct C : A, B {};
C f; f("hello");                                       // error: operator() ambiguous between A and B

class Derived : public Base {
public:
    using Base::print;                                 // re-expose Base::print(int) and Base::print(double)
    void print(double);
    int getValue() const = delete;                     // d.getValue() fails; d.Base::getValue() still works
};
```

## Virtual functions and overrides

A virtual function is a member function that, when called through a pointer or reference, resolves to the most-derived override for the dynamic type of the object. Mark it with `virtual` in the base class; a derived function with the same name, the same parameter types, the same constness, and the same return type is an override, and it is implicitly virtual whether or not the keyword is repeated. The resolution walks from the static type down to the dynamic type: with `class D : C : B : A` and a `C` object referenced as `A&`, calling a virtual `getName` picks `C::getName`, not `D`'s, because the object is a `C`. Virtual resolution only happens through a pointer or reference. Calling a virtual member directly on an object always calls that object's own type's version, and passing a `Derived` by value into a `Base` parameter slices it: the parameter is a fresh `Base` copy-constructed from the base part, its dynamic type is `Base`, and `a.print()` inside prints the base version. Virtual dispatch is runtime polymorphism; overload resolution and templates are compile-time polymorphism.

The signature must match exactly, and the failure mode is silent. A derived function that takes `short` where the base took `int`, or that adds `const`, is not an override. It is a new function that hides the base name in the derived class, the base version stays virtual on its own, and a call through a `Base*` runs the base version. With `struct A { virtual void foo(int); }; struct B : A { virtual void foo(int) const; };`, calling `a->foo(0)` on an `A*` that points at a `B` prints A's `1`. Return types must also match, with one exception: if the base returns a pointer or reference to a class, the override may return a pointer or reference to a class derived from it. That is a covariant return type. The caller still gets the static return type of the function it named, so `b->getThis()` through a `Base*` yields a `Base*` even though `Derived::getThis` ran, and a non-virtual member called on that result resolves to the base version.

Default arguments are not virtual. They are substituted at the call site from the static type, while the function body comes from the dynamic type. With `struct C { virtual void foo(int a = 1); }; struct D : C { void foo(int a = 2) override; };`, calling `d->foo()` through a `C*` prints `D1`: D's body, C's default. Give overrides the same defaults as the base, or better, no defaults on virtual functions at all.

Do not call virtual functions from constructors or destructors expecting the derived version. While the base constructor runs the derived part does not exist yet, and while the base destructor runs it is already gone, so the call resolves to the base version in both cases. The cost of virtual functions is a vtable pointer in every object of a polymorphic class and an indirect call through the vtable, which blocks inlining and can mispredict; make a function virtual only when something overrides it. The layout side of this, vptr placement and sharing with the primary base, is in [memory_layout.md](memory_layout.md).

```cpp
struct A { virtual void foo(int) { std::cout << "1"; } };
struct B : A {
    virtual void foo(int) const { std::cout << "2"; }   // new function, not an override: const differs
};
A* a = new B();
a->foo(0);                                             // prints 1
```

## override and final

`override`, written after the parameter list and after any `const`, tells the compiler this function must override a base virtual function. If it does not, because the name, parameters, constness, or return type differ, or because the base function is not virtual, the program does not compile. That turns the silent hiding above into an error: adding `override` to `B::foo(int) const` is a compile error, which is exactly what you want. `override` implies `virtual`, so write `void f() override;` rather than `virtual void f() override;`. Every override should carry it; there is no cost.

`final` in the same position forbids further overriding of that function, and `class B final : A` forbids deriving from `B`. Both are enforced at compile time. Beyond documentation, `final` enables devirtualization: when the compiler can prove which override a call reaches, it emits a direct call and can inline the body. It can already do that when the dynamic type is visible, such as `dog d; d.speak();`, and `final` extends that to calls through a `derived&` or `derived*`, since nothing below `derived` can exist. Either the class or the function being `final` is enough. Without it the compiler loads the vtable and jumps through it.

So the answer to "can a virtual function be inlined" is yes: `virtual` is about how a call resolves, and `inline` is about what happens once the target is known. A virtual call through a pointer or reference to a type that might have further overrides cannot be inlined because the target is not known until runtime. A call on an object, or through a pointer or reference whose dynamic type the compiler can prove, including because the class or function is `final`, can be.

`override` and `final` are identifiers with special meaning rather than keywords, so they can still be used as ordinary names elsewhere, which is why old code that has a variable called `final` still compiles, and `int override{1}; std::cout << override;` prints `1`.

Virtual-ness starts at the class that first says `virtual` and only flows downward. With `class A { void f(); }`, `struct B : A { virtual void f(); }`, and `class C : B { void f(); }`, `A::f` is an ordinary function, `B::f` starts a virtual chain, and `C::f` overrides `B::f`. An `A*` to a `B` calling `f()` resolves statically to `A::f`, a `B*` to a `C` dispatches to `C::f`, and `B c = *(new C);` slices, so `c.f()` runs `B::f`. Six calls, `A* -> A`, `A* -> B`, `B* -> C`, then `A`, `B`, and the sliced `B`, print `AACABB`.

## Multiple inheritance and the diamond

A class may list several bases, separated by commas, each initialized in the constructor's initializer list in the order the bases are declared. A small class inherited only to add a capability is a mixin, such as `Button : Box, Label, Tooltip`. Two problems follow. If two bases declare a member with the same name, an unqualified use in the derived class is ambiguous and must be qualified, `teacher.Person::getName()`. And when two bases share a common base, the derived class holds two copies of it, one inside each. That is the diamond. With `D : B, C` and both `B` and `C` deriving from `A`, constructing a `D` prints `ABACD`: `B`'s subobject builds its own `A` then itself, `C`'s subobject does the same, then `D` runs. Any reference to an `A` member through a `D` is ambiguous until qualified. Virtual inheritance, `class B : virtual public A`, makes the two paths share a single `A` subobject, initialized by the most-derived class; that is a later lesson and is noted in [memory_layout.md](memory_layout.md) for its layout cost. Multiple inheritance is worth keeping for interfaces and mixins and otherwise avoiding; `std::cin` and `std::cout` are built on it, through `basic_iostream` inheriting both an input and an output stream.

```cpp
class A { public: A() { std::cout << "A"; } };
class B : public A { public: B() { std::cout << "B"; } };
class C : public A { public: C() { std::cout << "C"; } };
class D : public B, public C { public: D() { std::cout << "D"; } };
D d;                                                   // ABACD: two A subobjects
```

## Virtual destructors

Deleting a derived object through a base pointer runs only the base destructor unless the base destructor is virtual. The derived destructor never runs, so whatever it owned leaks. A base class that will be deleted polymorphically must declare `virtual ~Base() = default;` or an equivalent; derived destructors are then virtual automatically and do not need to be written just to say so. The cost is the vtable pointer, which the class probably already pays for its other virtual functions. Herb Sutter's rule gives the two consistent designs: a base class destructor should be either public and virtual, so that deleting through the base pointer works, or protected and non-virtual, so that deleting through the base pointer does not compile and the class can be used only as a base, with no vtable added. The protected option also forbids destroying a `Base` directly in any context, including a local variable, so it suits pure interface bases and mixins. The modern guidance: a class not designed as a base gets no virtual members and no virtual destructor and is composed instead of inherited; a class designed as a base, or with any virtual function, gets a public virtual destructor; a class that should end the hierarchy is marked `final`.

Virtual assignment operators are possible and a poor idea; leave assignment non-virtual. A base version of a virtual function can be called explicitly through the scope operator, `base->Base::getName()`, when the virtual dispatch is deliberately bypassed, which is rare.

## Early binding, late binding, and the vtable

Binding is deciding which function definition a call reaches. A direct call to a non-member function, a non-virtual member, an overload, or a template instantiation is bound early: the compiler knows the target and emits a direct jump. A call through a function pointer is bound late, because the pointer's value is only known at runtime, so the program loads the pointer and jumps through it. A `switch` that picks a branch at runtime does not change this; each call inside a case is still a direct call. Virtual functions are the second form of late binding, and the compiler implements them with a table.

Every class that declares or inherits a virtual function gets its own virtual table, a static array of function pointers built at compile time with one slot per virtual function, each slot pointing at the most-derived implementation that class can see. The base class that first declares a virtual function gains a hidden data member, the vptr, which unlike `this` is real storage inside every object, so the object grows by one pointer. The constructor sets the vptr to the table of the object's dynamic class; derived classes inherit the member and point it at their own table. With `Base` declaring `function1` and `function2`, `D1` overriding only `function1`, and `D2` overriding only `function2`, the tables are `{Base::function1, Base::function2}`, `{D1::function1, Base::function2}`, and `{Base::function1, D2::function2}`. A call `p->function1()` through a `Base*` loads `p->vptr`, indexes the `function1` slot, and calls whatever it finds. The cost is one pointer per object, one table per class, and three operations per call (load the vptr, index, indirect jump) instead of one direct jump, plus the lost inlining discussed under `final`. A class with no data members and one virtual function still has `sizeof` at least a pointer. The placement of the vptr, sharing with a primary base, and what tail padding reuse does to `sizeof` on a given ABI are in [memory_layout.md](memory_layout.md).

## Pure virtual functions, abstract classes, and interfaces

Writing `= 0` in place of a body makes a virtual function pure: a placeholder that every concrete derived class must override. Only a virtual function can be pure. A class with at least one pure virtual function is abstract and cannot be instantiated, which the compiler enforces because otherwise an object could exist whose virtual call has nothing to run. An abstract class still has constructors, data members, and ordinary member functions; its constructor runs as the base part of every derived object's construction, and is often made protected to say so. A derived class that leaves any inherited pure virtual function unimplemented is itself abstract, all the way down the chain until every one has a body.

A pure virtual function may still have a definition. The body must be written outside the class, `std::string_view Animal::speak() const { return "buzz"; }`, the class stays abstract, and a derived override can opt into that default explicitly with `Animal::speak()`. That is the idiom for a default that derived classes must choose rather than inherit silently. Inside the vtable the pure slot holds a null pointer or a pointer to an error routine such as MSVC's `__purecall`, which is what fires if a pure virtual is reached from a constructor.

An interface class has no data members and only pure virtual functions; it is a usage pattern, not a language feature, often named with an `I` prefix such as `IErrorLog`. A function taking `IErrorLog&` accepts a file logger, a screen logger, or a network logger without knowing which. Every interface class needs a virtual destructor, even an empty one, so that deleting an implementation through the interface pointer runs the right destructor.

```cpp
class IErrorLog {
public:
    virtual bool openLog(std::string_view filename) = 0;
    virtual bool writeError(std::string_view msg) = 0;
    virtual ~IErrorLog() = default;
};
```

## Virtual base classes

The diamond from the multiple inheritance section is fixed by declaring the shared base virtual on the intermediate classes: `class Scanner : virtual public PoweredDevice` and `class Printer : virtual public PoweredDevice`. Everything derived from both then holds one `PoweredDevice` subobject. The keyword belongs on the edge from the intermediate class to the shared base, not on the most-derived class's list; `Copier : virtual public Scanner` would not deduplicate anything.

The most-derived class constructs the virtual base. `Copier`'s initializer list names `PoweredDevice{ power }` directly, the one case where a class may call a non-immediate base constructor, and the `PoweredDevice{ power }` calls written in `Scanner` and `Printer` are ignored while a `Copier` is being built. They are still required, because they run when a `Scanner` or `Printer` is the most-derived object. If the most-derived class does not mention the virtual base, its default constructor is used, or compilation fails if there is none. Virtual bases are constructed before all non-virtual bases, so every base exists before anything derived from it runs. The cost is a vptr in every class that inherits a virtual base, even without virtual functions, because the offset from `this` to the shared subobject depends on the most-derived type and has to be looked up.

```cpp
class PoweredDevice { public: PoweredDevice(int power) {} };
class Scanner : virtual public PoweredDevice {
public: Scanner(int s, int power) : PoweredDevice{ power } {}
};
class Printer : virtual public PoweredDevice {
public: Printer(int p, int power) : PoweredDevice{ power } {}
};
class Copier : public Scanner, public Printer {
public:
    Copier(int s, int p, int power)
        : PoweredDevice{ power }, Scanner{ s, power }, Printer{ p, power } {}   // Copier builds the shared base
};
```

## Errors and pitfalls

- **Invalid: initializing a base member in a derived constructor's initializer list.** Name the base constructor instead: `Derived(int id) : Base{ id } {}`.
- **Invalid: calling a grandparent constructor.** Each class names only its immediate base, except a virtual base, which the most-derived class constructs.
- **Invalid: a reference member or const member assigned in the body.** They must be in the initializer list; see [classes.md](classes.md).
- **Invalid: a derived overload that hides the base overloads.** `Bar::Baz()` hides `Foo::Baz(double)`, so `bar.Baz(42)` fails; add `using Foo::Baz;`.
- **Invalid: a name provided by two bases.** Lookup is ambiguous before overload resolution, even for `operator()`; qualify or add a using-declaration.
- **Invalid: `Animal a;` for a class with a pure virtual function**, or for a derived class that left one unimplemented.
- **Invalid: `= 0` on a non-virtual function**, or a pure virtual's body written inline in the class.
- **Logical error: `class D : Base` inherits privately.** A `class` defaults to private inheritance, a `struct` to public.
- **Logical error: expecting a private override to be unreachable.** Access is checked on the static type; `z.foo()` through a `Z&` runs the private `X::foo`.
- **Logical error: hiding a base member with `private: using Base::m;` and calling it encapsulation.** A `Base&` to the object still reaches it.
- **Logical error: unqualified `identify()` inside `Derived::identify()`.** Infinite recursion; write `Base::identify()`.
- **Logical error: `virtual` on the wrong edge.** `Copier : virtual Scanner` does not deduplicate `PoweredDevice`; the intermediates must inherit virtually.
- **Invalid: `override` on a function that overrides nothing.** Parameter, constness, or return-type mismatch, or a non-virtual base function, is a compile error. This is the feature working.
- **Invalid: overriding a `final` function, or deriving from a `final` class.**
- **Invalid: a return type that differs and is not covariant.** `int` versus `double` fails; `Derived*` for `Base*` is allowed.
- **Logical error: a near-miss override without `override`.** Different parameter type or added `const` silently creates a hidden function; calls through the base run the base version.
- **Logical error: slicing.** Passing or storing a derived object by value in a base variable copies only the base part and loses the dynamic type.
- **Logical error: default arguments on virtual functions.** They bind statically; the derived body runs with the base's default.
- **Logical error: virtual call inside a constructor or destructor.** Resolves to the class whose constructor or destructor is running.
- **Resource leak, and UB by the standard: deleting a derived object through a base pointer whose destructor is not virtual.**
- **Ambiguity: unqualified use of a member that two bases provide, or of the shared base in a non-virtual diamond.**

## Additional syntax examples

```cpp
struct Base {
    virtual ~Base() = default;
    virtual Base* clone() const { return new Base(*this); }
    virtual std::string_view name() const { return "Base"; }
};
struct Derived final : Base {
    Derived* clone() const override { return new Derived(*this); }   // covariant return
    std::string_view name() const override { return "Derived"; }
};

void report(const Base& b) { std::cout << b.name(); }               // by reference: dispatches
void sliced(Base b)        { std::cout << b.name(); }               // by value: always Base

Base* p = new Derived;
p->name();          // Derived
p->Base::name();    // Base, dispatch bypassed
delete p;           // ~Derived then ~Base, because ~Base is virtual

struct Interface {
protected:
    ~Interface() = default;     // protected non-virtual: cannot delete through Interface*
public:
    virtual void run() = 0;
};
```

## Interview Q&A

### A global `Z z;` and `X x; Y y;` in `main`, each printing a lowercase letter on construction and uppercase on destruction. Output?

`zxyYXZ`. Statics are constructed before `main` and destroyed after it, locals in declaration order and destroyed in reverse.

### `void foo() { static X x; }` where `X` has a member `Z` whose constructor prints `z` and throws the first time. `main` calls `foo()` in a `try`, prints `y` in the handler, then calls `foo()` again. Output?

`zyzxXZ`. The first call prints `z` and throws inside `Z`'s constructor, so neither `X` nor `Z` finished constructing and nothing is destroyed; the static is not marked initialized. The handler prints `y`. The second call retries: `z`, then `X`'s body prints `x`. At exit the completed static is destroyed, `X` then `Z`.

### `class B : private A` calls a protected `A::Private()` from a public member. Does it compile?

Yes, and it prints. The inheritance type only changes how `A`'s members look through `B` to outsiders and further-derived classes. Inside `B`'s own members, public and protected base members are always usable.

### `struct C : A, B {}` where both bases define `operator()` with different parameter types. What does `C f; f("hello");` do?

Compile error. Name lookup for `operator()` finds a match in both direct bases and stops as ambiguous before overload resolution has a chance to notice that only `B`'s overload accepts a string. Add `using B::operator();` in `C` or qualify the call.

### `Bar : Foo` declares `void Baz()` while `Foo` has `void Baz(double)`. What does `bar.Baz(42)` print?

Nothing, it does not compile. Lookup stops at `Bar`, the first class with a member named `Baz`, and `Bar::Baz()` takes no argument. `using Foo::Baz;` in `Bar` restores the base overload.

### A derived class overrides a public virtual function in its private section. Called through a `Base&`, what runs?

The private derived override. Access is checked against the static type of the expression, `Base::foo`, which is public; virtual dispatch then runs `X::foo`. The program prints `X`.

### `int override{1}; std::cout << override;`

Prints `1`. `override` and `final` are contextual identifiers, not reserved keywords.

### `A::f` non-virtual, `B : A` makes `f` virtual, `C : B` overrides. Calls through `A*` to an `A`, `A*` to a `B`, `B*` to a `C`, then on an `A`, a `B`, and a `B` copy-initialized from a `C`. Output?

`AACABB`. `A::f` is not virtual, so both `A*` calls run `A::f`. `B::f` starts the virtual chain, so the `B*` to a `C` dispatches to `C::f`. The direct calls run each object's own version, and `B c = *(new C);` slices to a `B`.

### `class B : public A` with `A` holding `int i` and `B` adding `int x`. Layout on a 64-bit system?

The base subobject comes first: `[ A::i ][ B::x ]`. A derived object is its base part followed by its own members, which is what lets a `B*` be treated as an `A*` without adjustment for a single non-virtual base.

### `class A { int i1; virtual void foo(); }; class B : public A { int i2; };` What does `sizeof(A) << sizeof(B)` print on 64-bit?

`1616` on the Itanium ABI used by GCC and Clang. `A` is a vptr plus a 4-byte int, padded to 16. `A` is not a plain-old-data type, so the ABI lets `B` place `i2` in `A`'s 4 bytes of tail padding, and `B` is still 16. MSVC does not reuse tail padding and gives 24. See [memory_layout.md](memory_layout.md).

### Can a pure virtual function have a body, and why would it?

Yes, defined outside the class. The class stays abstract, and a derived override can call `Base::f()` to reuse it. It gives a default that derived classes must opt into explicitly instead of inheriting by accident.

### What does a virtual base change about construction?

The most-derived class constructs the virtual base directly in its initializer list, even though it is not an immediate parent, and the initializers for that base written in the intermediate classes are ignored. Virtual bases are constructed before any non-virtual base. Every class with a virtual base carries a vptr so the offset to the shared subobject can be found.

### What is printed when a `B` with `virtual void foo(int) const` is called through an `A*` whose `foo(int)` is not const?

A's version. Constness is part of the signature, so `B::foo(int) const` does not override `A::foo(int)`; it is a new virtual function that hides the name inside `B`. Through an `A*` the call resolves against A's virtual function, whose only override is none, so it prints `1`. Writing `override` on B's function turns this into a compile error, which is the reason to write it.

### Why does `doit(b)` print `A` when `doit` takes its parameter by value?

Because the parameter is a `Base` object copy-constructed from the `Base` part of `b`. The dynamic type of that copy is `Base`, so the virtual call has nothing more derived to find. Slicing is a by-value problem; `const Base&` or `Base*` keeps the dynamic type.

### Through a `C*` to a `D`, `d->foo()` prints `D1` when C defaults `a` to 1 and D to 2. Why?

The body comes from the dynamic type and the default argument from the static type. Defaults are filled in at the call site by the compiler, which only knows it is calling `C::foo`, so it passes 1; then dispatch runs `D::foo`. Never vary default arguments across overrides.

### Can virtual functions be inlined?

Yes. Inlining happens once the compiler knows which function a call reaches. It knows for a call on an object, and for a call through a pointer or reference when it can prove the dynamic type, including when the class or the function is `final`. It does not know for a call through a pointer or reference to a type that could still be overridden further, so that call goes through the vtable and stays out of line.

### What does `class D : B, C` with both deriving from `A` print on construction, and why is it a problem?

`ABACD`. Each of `B` and `C` carries its own `A`, so `A` is constructed twice, and any `A` member reached through `D` is ambiguous. Virtual inheritance collapses the two into one shared `A`; without it, the diamond is a maintenance trap and usually a sign the design wants an interface rather than a shared base.

### What should a base class destructor look like?

Either public and virtual, so deleting through a base pointer runs the derived destructor, or protected and non-virtual, so deleting through a base pointer does not compile and the base carries no vtable for the destructor's sake. A class with any virtual function should take the first option; a pure interface can take the second; a class not designed as a base needs neither and should not be inherited from.

### Does a class template with a virtual destructor compile, and can a member function template be virtual?

The virtual destructor is fine: `Dynamic<T>` is a class, and each instantiation has an ordinary virtual destructor. A member function template cannot be virtual, because the vtable is fixed when the class is compiled and a template would need a new slot for every instantiation used anywhere in the program. See [templates.md](templates.md).

## Practice history

### Reading

- 13/09/2026 (later): learncpp 24.1 (introduction to inheritance), 24.2 (basic inheritance), 24.3 (order of construction of derived classes), 24.4 (constructors and initialization of derived classes), 24.5 (inheritance and access specifiers), 24.6 (adding new functionality), 24.7 (calling inherited functions and overriding behavior), 24.8 (hiding inherited functionality), 25.5 (early and late binding), 25.6 (the virtual table), 25.7 (pure virtual functions, abstract base classes, interface classes), 25.8 (virtual base classes). Bo Qian access modifier and duality of public inheritance videos not watched.
- 13/09/2026: learncpp 24.9 (multiple inheritance), 25.1 (pointers and references to the base class), 25.2 (virtual functions), 25.3 (override, final, covariant return types), 25.4 (virtual destructors, virtual assignment, overriding virtualization); Microsoft C++ blog, the performance benefits of final classes. Bo Qian's multiple inheritance video not watched.

### Questions (getcracked)

- Per platform record, rescraped 13/09/2026. Multiple Inheritance (Issues): In a Diamond (ABACD, two A subobjects) ok. Base Class References & Pointers: Adding const, overrid-ially. (`override` on a const mismatch is a compile error) ok. Adding const, virtually? (const mismatch hides instead of overriding, prints 1) ok. Chop Chop Chop (by-value parameter slices, prints A) ok. Static* and Dynamic* (default arguments bind to the static type, prints D1) ok. Virtual Destructor: Herb's Destructor (public and virtual, or protected and non-virtual) ok. Override and Final: We're virtually there. (virtual functions can be inlined when the target is statically known; not through a pointer or reference whose dynamic type is open) wrong first attempt, retest in a week; Removing the polymorphic (AACABB: virtual starts at B, sliced copy is a B) ok; wrong first attempt (retest in a week): Is it accessible? (private override is still reached through a `Z&`, access is checked on the static type, prints X), override! (`override` is a contextual identifier, prints 1).
- 13/09/2026 (later), per platform record. Construction Order: Constructing it, with it. (member Z inside X, zxXZ) ok, Constructing it. (base Z of X, zxXZ) ok, Do you understand creation? (global before main, destroyed last, zxyYXZ) ok, Parents are always right? (base subobject first, `[A::i][B::x]`) ok, A mix of creations. (static local whose constructor throws is retried, zyzxXZ) ok; the three single-class questions (Under the Shadow, References in Class, Is it const?) are logged in [classes.md](classes.md). Access Modifiers: private, public, protected (private inheritance still lets B call A's protected member, prints 1) ok. Adding & Hiding Functionality: Under the Shadow ok; wrong first attempt (retest in a week): Where are we? (`operator()` from two bases is ambiguous lookup, compile error), I'm printing mom... (`Bar::Baz()` hides `Foo::Baz(double)`, `bar.Baz(42)` is a compile error). Pure Virtual Functions and Abstract Classes: Free Real Estate (`sizeof` 16 and 16, tail padding of a non-POD base is reused for `i2` on the Itanium ABI) wrong first attempt, retest in a week.
- Anki: bases then members in declaration order, destruction reversed; a derived initializer list names the base constructor, never a base member; a static local whose constructor throws is retried next call; inheritance type changes the outside view only, the derived class always sees public and protected; access is checked on the static type, so a private override runs through a `Base&`; one derived overload hides all base overloads, `using Base::f` restores them; a name in two bases is ambiguous before overload resolution; `override` and `final` are identifiers; pure virtual may have an out-of-class body; most-derived class constructs the virtual base; tail padding of a non-POD base is reusable on Itanium (16/16), not on MSVC (16/24); constness is part of the override signature; slicing happens on by-value copies; default arguments are static, bodies are dynamic; a virtual call through a non-final pointer cannot inline; base dtor public virtual or protected non-virtual; diamond constructs the shared base twice without virtual inheritance.

<!-- gc-questions:start -->

## Related getcracked questions

Pulled from the Beginner C++ progress tree. ✓ answered correctly, ✗ attempted and missed, ○ not attempted yet. Regenerate with `python3 cpp/tools/gc_links.py` after re-scraping.

### Access Modifiers
- ✓ [private, public, protected](https://getcracked.io/question/862) — Easy

### Construction Order
- ✓ [Constructing it, with it.](https://getcracked.io/question/705) — Easy
- ✓ [Constructing it.](https://getcracked.io/question/706) — Easy
- ✓ [Do you understand creation?](https://getcracked.io/question/703) — Easy
- ✗ [Is it const?](https://getcracked.io/question/735) — Easy
- ✓ [Parents are always right?](https://getcracked.io/question/1081) — Easy
- ✗ [References in Class](https://getcracked.io/question/734) — Easy
- ✓ [A mix of creations.](https://getcracked.io/question/704) — Hard

### Adding & Hiding Functionality
- ✗ [I'm printing mom...](https://getcracked.io/question/1721) — Medium
- ✗ [Where are we?](https://getcracked.io/question/913) — Medium
- ✓ [Under the Shadow](https://getcracked.io/question/716) — Hard

### Multiple Inheritance (Issues)
- ✓ [In a Diamond](https://getcracked.io/question/718) — Easy

### Base Class References & Pointers
- ✓ [Adding const, overrid-ially.](https://getcracked.io/question/909) — Easy
- ✓ [Adding const, virtually?](https://getcracked.io/question/908) — Easy
- ✓ [Chop Chop Chop](https://getcracked.io/question/491) — Easy
- ✓ [Static* and Dynamic*](https://getcracked.io/question/851) — Medium

### Override and Final
- ✗ [Is it accessible?](https://getcracked.io/question/707) — Easy
- ✗ [override!](https://getcracked.io/question/1395) — Easy
- ✓ [Removing the polymorphic](https://getcracked.io/question/1213) — Medium
- ✗ [We're virtually there.](https://getcracked.io/question/1178) — Medium

### Virtual Destructor
- ✓ [Herb's Destructor](https://getcracked.io/question/1218) — Cooked

### Pure Virtual Functions and Abstract Classes
- ✗ [Free Real Estate](https://getcracked.io/question/1837) — Medium

<!-- gc-questions:end -->
