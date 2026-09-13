# Inheritance: Base Pointers, Virtual Functions, override/final & Virtual Destructors

## Derived objects and base pointers

A derived object is built from parts: one subobject for each base class, constructed first, and the derived part constructed last, destroyed in the reverse order. Because a `Derived` is-a `Base`, a `Base&` or `Base*` may refer to the base part of a `Derived` object. What such a reference can see is fixed by its static type: through a `Base&` only the members of `Base` are visible, so a `Derived::getName()` that hides `Base::getName()` is not reachable, and a member that exists only in `Derived` cannot be called at all. That is the limitation that virtual functions remove, and it is also why base references are useful in the first place: one function taking `const Animal&` accepts every current and future animal, and one array of `Animal*` can hold a mixed population, where a template parameter would neither document nor enforce that the argument is an `Animal`.

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

`override` and `final` are identifiers with special meaning rather than keywords, so they can still be used as ordinary names elsewhere, which is why old code that has a variable called `final` still compiles.

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

## Errors and pitfalls

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

- 13/09/2026: learncpp 24.9 (multiple inheritance), 25.1 (pointers and references to the base class), 25.2 (virtual functions), 25.3 (override, final, covariant return types), 25.4 (virtual destructors, virtual assignment, overriding virtualization); Microsoft C++ blog, the performance benefits of final classes. Bo Qian's multiple inheritance video not watched.

### Questions (getcracked)

- Per platform record, rescraped 13/09/2026. Multiple Inheritance (Issues): In a Diamond (ABACD, two A subobjects) ok. Base Class References & Pointers: Adding const, overrid-ially. (`override` on a const mismatch is a compile error) ok. Adding const, virtually? (const mismatch hides instead of overriding, prints 1) ok. Chop Chop Chop (by-value parameter slices, prints A) ok. Static* and Dynamic* (default arguments bind to the static type, prints D1) ok. Virtual Destructor: Herb's Destructor (public and virtual, or protected and non-virtual) ok. Override and Final: We're virtually there. (virtual functions can be inlined when the target is statically known; not through a pointer or reference whose dynamic type is open) wrong first attempt, retest in a week; Is it accessible?, override!, Removing the polymorphic not attempted.
- Anki: constness is part of the override signature; slicing happens on by-value copies; default arguments are static, bodies are dynamic; a virtual call through a non-final pointer cannot inline; base dtor public virtual or protected non-virtual; diamond constructs the shared base twice without virtual inheritance.

<!-- gc-questions:start -->

## Related getcracked questions

Pulled from the Beginner C++ progress tree. ✓ answered correctly, ✗ attempted and missed, ○ not attempted yet. Regenerate with `python3 cpp/tools/gc_links.py` after re-scraping.

### Multiple Inheritance (Issues)
- ✓ [In a Diamond](https://getcracked.io/question/718) — Easy

### Base Class References & Pointers
- ✓ [Adding const, overrid-ially.](https://getcracked.io/question/909) — Easy
- ✓ [Adding const, virtually?](https://getcracked.io/question/908) — Easy
- ✓ [Chop Chop Chop](https://getcracked.io/question/491) — Easy
- ✓ [Static* and Dynamic*](https://getcracked.io/question/851) — Medium

### Override and Final
- ○ [Is it accessible?](https://getcracked.io/question/707) — Easy
- ○ [override!](https://getcracked.io/question/1395) — Easy
- ○ [Removing the polymorphic](https://getcracked.io/question/1213) — Medium
- ✗ [We're virtually there.](https://getcracked.io/question/1178) — Medium

### Virtual Destructor
- ✓ [Herb's Destructor](https://getcracked.io/question/1218) — Cooked

<!-- gc-questions:end -->
