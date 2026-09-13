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

A const object of class type must be initialized when created and cannot be modified afterwards, so `const Date today{2020, 10, 14};` is fine while `today.day += 1;` is an error. The initialization requirement has a sharp edge for default initialization. `const C c;` with no initializer is only allowed if `C` is const-default-constructible, which means either its default constructor is user-provided (written by you, not `= default` on first declaration) or every non-static member that would otherwise be left indeterminate has a default member initializer. A class such as `struct C { C() = default; int i; };` fails both tests, so `const C c;` is a compile error ("uninitialized const"), not a read of junk. Give `i` an initializer, write `C() {}` by hand, or use `const C c{};`, which value-initializes and zeroes `i`. The rule exists because a const object can never be assigned later, so an indeterminate member in it could never become valid. The rule extends to member functions: a const object may only call member functions marked `const` after the parameter list, because the compiler cannot tell from outside whether an unmarked function modifies the object. `today.print()` fails on a const `today` if `print` is not const, even when the body only reads. Passing by const reference has the same effect inside the callee, so a `void doSomething(const Date& d)` can only call const members of `d`. Since almost every type is at some point handled through a `const T&`, a class whose readers are not const is unusable in practice.

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

## Constructors

A constructor is a special member function that runs automatically after storage for a non-aggregate class object has been obtained. It does not create the object; the storage exists first, and the constructor's job is to turn indeterminate storage into a valid object, which is where class invariants get established. A constructor has the class's name, exactly as capitalized, and no return type, not even `void`. It is almost always public, because it is how outside code makes objects. Constructors are never `const`: the object is exempt from const restrictions until construction finishes, so even a `const Something s;` runs a constructor that writes to members.

Declaring any constructor makes the type a non-aggregate, so aggregate initialization stops working. That is also the practical reason a class with private members needs a constructor: `class Foo { int m_x{}; int m_y{}; };` cannot be written as `Foo foo{6, 7};`, because the private members disqualify it as an aggregate, and only a `Foo(int x, int y)` constructor gives callers a way to supply values. Constructor parameters are ordinary parameters. The compiler applies the usual implicit conversions to arguments, so `Foo foo{'a', true};` matches `Foo(int, int)` with `'a'` promoted to 97 and `true` to 1, subject to the narrowing rules of brace initialization.

A constructor initializes the whole object at the moment it comes into existence. A setter modifies one member of an object that already exists. Those are different operations, and the difference is the subject of the next section.

## Member initializer lists

The member initializer list sits between the parameter list and the body, introduced by a colon, and names each member with its initializer in braces or parentheses. Copy-initialization with `=` is not allowed there. Members are initialized by the list before the body runs; by the time the body starts, every member already exists.

```cpp
class Foo {
    int m_x{};
    int m_y{};
public:
    Foo(int x, int y) : m_x{x}, m_y{y} { }
};
```

Assigning in the body instead is worse in three ways. It is two operations per member, a default initialization followed by an assignment, which for a `std::string` means constructing an empty string and then overwriting it. It cannot work at all for `const` members and reference members, which must be initialized and cannot be assigned. And it leaves a window in which the object is half-built. The standard's wording is that an object is initialized once the member initializer list has finished, and constructed once the body has finished. Prefer the initializer list for every member that takes a value from the constructor.

Members are initialized in the order they are declared in the class, not the order they appear in the initializer list. Writing `Foo(int x, int y) : m_y{std::max(x, y)}, m_x{m_y} {}` with `m_x` declared first initializes `m_x` from an `m_y` that does not exist yet, which is undefined behavior, and the list order gives no hint that anything is wrong. Compilers warn under `-Wreorder`. List members in declaration order and avoid initializing one member from another.

Three sources compete for a member's initial value, and the priority is fixed. An entry in the member initializer list wins. Otherwise the member's default member initializer, the `{}` or `= value` written at the declaration, is used. Otherwise the member is default-initialized, which for a scalar means indeterminate. So in a class with `int m_x{}; int m_y{2}; int m_z;` and a constructor `Foo(int x) : m_x{x} {}`, `Foo foo{6};` gives `m_x == 6`, `m_y == 2`, and `m_z` uninitialized. This is the same rule that made `Bad` earlier in this file undefined: a default member initializer is just the fallback for a member the constructor did not list.

## Default constructors, default arguments, and `= default`

A default constructor is one that can be called with no arguments. It runs for both `Foo foo{};` and `Foo foo;`, though value-initialization with empty braces is the form to prefer for class types, for a reason below. A constructor whose parameters all have default arguments is also a default constructor, so `Foo(int x = 0, int y = 0)` serves `Foo{}` and `Foo{6, 7}` alike. A class may have only one default constructor: declaring both `Foo()` and `Foo(int x = 1, int y = 2)` compiles, but `Foo foo{};` is then ambiguous and fails.

If a non-aggregate class declares no constructors at all, the compiler generates an implicit default constructor with no parameters, no initializer list, and an empty body, so members get their default member initializers or are left default-initialized. Declaring any constructor suppresses it, which is why a class with `Foo(int, int)` and nothing else cannot be written `Foo foo{};`. To get the generated one back alongside other constructors, write `Foo() = default;`. Prefer that over an empty-bodied `Foo() {}`, and not only for brevity: a defaulted constructor is not user-provided, so value-initialization `Foo foo{};` zero-initializes the object before running it, while a user-provided empty body skips the zeroing. With `int m_a;` and no initializer, `Default d{};` gives `m_a == 0` and `User u{};` leaves it indeterminate. The same user-provided distinction decides whether `const Foo f;` compiles, as covered in the const section.

Only provide a default constructor when an object made of default values is meaningful. A `Fraction` defaulting to zero over one is; an `Employee` with an empty name and id zero is not, and leaving out the default constructor forces callers to supply real data.

## Delegating constructors

Several constructors of one class often repeat the same initializer entries. Calling one constructor from the body of another does not fix this: `Employee(name, id);` inside a body is an expression that creates and immediately destroys a temporary `Employee`, and the members of the object under construction are untouched. Since C++11 a constructor may instead delegate by naming another constructor of the same class in its member initializer list.

```cpp
class Employee {
    std::string m_name{"???"};
    int m_id{0};
public:
    Employee(std::string_view name) : Employee{name, 0} { }     // delegates
    Employee(std::string_view name, int id) : m_name{name}, m_id{id} {
        std::cout << "Employee " << m_name << " created\n";
    }
};
```

A delegating constructor may do nothing else in its initializer list: a constructor either delegates or initializes members, not both, though it may still have a body that runs after the target constructor returns. Delegation must terminate in a non-delegating constructor; a cycle is ill-formed, and compilers reject the obvious cases. The target's body runs before the delegating constructor's body, and the object counts as constructed once the target returns, which matters for exception handling: if the delegating constructor's body throws, the destructor runs.

Two cheaper tools often remove the need to delegate. Default arguments collapse `Employee(name)` and `Employee(name, id)` into `Employee(std::string_view name, int id = 0)`; order the parameters so members the caller must supply come first and optional ones last, and declare the members in that same order. For shared body logic rather than shared initialization, a private helper member function called from each body avoids duplication without any constructor-to-constructor call.

## Temporaries and the six initialization forms

A temporary class object is written as the type followed by an initializer, `IntPair{5, 6}` or `Foo(1, 2)`, or as a bare braced list `{7, 8}` where the context fixes the type, such as a function argument or a return statement. Prefer the braced forms: `Foo()` and `Foo(x)` can be mistaken for declarations, and parentheses allow narrowing. `Foo()` and `Foo{}` both value-initialize. A temporary lives from its creation to the end of the full expression that contains it, so `print(IntPair{3, 4});` builds the pair, calls `print`, and destroys it at the semicolon. In an expression a temporary is a prvalue, which is why it cannot bind to a non-const lvalue reference parameter. `static_cast<T>(x)` also produces a temporary, direct-initialized from `x`; use it for narrowing and fundamental types, and `T{x}` for class types where narrowing protection and list constructors matter. The value-category details and lifetime extension by a `const&` are in [value_categories.md](value_categories.md) and [initialization_deduction.md](initialization_deduction.md).

Class objects accept the same six initialization forms as fundamental types, and each one runs overload resolution over the constructors:

```cpp
Foo f1;           // default-initialization: default constructor
Foo f2{};         // value-initialization: default constructor (preferred)
Foo f3 = 3;       // copy-initialization: non-explicit Foo(int) only
Foo f4(4);        // direct-initialization: any Foo(int), narrowing allowed
Foo f5{5};        // direct-list-initialization: any Foo(int), no narrowing (preferred)
Foo f6 = {6};     // copy-list-initialization: non-explicit Foo(int), no narrowing
```

The forms differ in three ways. List forms reject narrowing. Copy forms consider only non-explicit constructors. List forms prefer an `initializer_list` constructor when one matches, which is the `std::vector<int>{10, 1}` trap in [initialization_deduction.md](initialization_deduction.md). When the initializer is another `Foo`, every form calls the copy constructor: `Foo f7 = f3;`, `Foo f8(f3);`, `Foo f9{f3};`, and `Foo f10 = {f3};` are the same call.

Copy elision lets the compiler skip a copy or move it would otherwise perform, even when the copy constructor has side effects such as printing, so counting constructor calls by output is unreliable. `Something s{Something{5}};` behaves as `Something s{5};`. Since C++17 the same-type prvalue cases are guaranteed rather than optional: `return Something{};` and initialization from a by-value return construct the destination directly, and the copy constructor need not even exist for them. Named return value optimization, `Something s; return s;`, remains optional, so a class that relies on it still needs an accessible copy or move constructor. The rules are in [functions_scope_lambdas.md](functions_scope_lambdas.md).

## The copy constructor

A copy constructor initializes a new object from an existing object of the same type. If the class declares none, the compiler generates a public one that copies member by member, which is correct for types whose members own themselves and wrong for a raw owning pointer, as the `B = A` question above shows for its assignment twin. The user-written form takes a `const Fraction&` and initializes each member in the initializer list. The parameter must be a reference: a by-value parameter would need to be copied in, which calls the copy constructor, which needs to copy its parameter, and so on without end, and compilers reject it. Use a const lvalue reference so temporaries and const objects can be copied.

The copy constructor runs whenever a new object is made from an existing one: `Fraction fCopy{f};`, passing a `Fraction` by value, and, absent elision, returning one by value. It should have no side effects beyond producing an equal copy, and the implicit one is preferred unless the class owns a resource. `Fraction(const Fraction&) = default;` requests the generated one explicitly, which is useful when another declaration would suppress it. `Fraction(const Fraction&) = delete;` makes the type non-copyable, so `Fraction fCopy{f};` and pass-by-value are compile errors. A class that needs a user-written copy constructor almost always also needs a user-written destructor and copy assignment operator, the rule of three, extended to five by the move operations; that discussion lives in [smart_pointers_move.md](smart_pointers_move.md).

A derived class's copy and move constructors must hand the base subobject to a base constructor in the initializer list, and the value category of what they pass decides which base constructor runs. Inside `Car(Car&& other)`, the parameter `other` has a name, so as an expression it is an lvalue even though its type is an rvalue reference. `Car(Car&& other) : Vehicle(other)` therefore calls the base copy constructor, not the base move constructor. To move the base part you must write `Vehicle(std::move(other))`. The same applies member by member: a move constructor that writes `m_name(other.m_name)` copies the string. This is the "named rvalue reference is an lvalue" rule from [value_categories.md](value_categories.md), and it is the most common way a hand-written move constructor silently degrades into a copy.

```cpp
struct Vehicle {
    Vehicle() = default;
    Vehicle(const Vehicle&) { std::cout << "A"; }
    Vehicle(Vehicle&&)      { std::cout << "B"; }
};
struct Car : Vehicle {
    Car() = default;
    Car(const Car& other) : Vehicle(other) { std::cout << "C"; }
    Car(Car&& other) : Vehicle(other)      { std::cout << "D"; }   // prints AD: base is copied
    // Car(Car&& other) : Vehicle(std::move(other)) { ... }        // prints BD
};
Car one;
Car two(std::move(one));
```

A related copy-counting trap is `std::initializer_list`. Constructing one from named objects, `std::initializer_list<A> i{a};`, copies each element into the list's backing array, so `A`'s copy constructor runs once per element. The list object itself is only a pointer and a length over that array, so passing it by value to `f(std::initializer_list<A>)` copies the handle, not the elements, and calling `f(i)` twice prints nothing further. With `A(const A&)` printing `1`, the whole program prints `1` once.

## Converting constructors and `explicit`

Any constructor that can be called with one argument is a converting constructor by default: the compiler may use it for an implicit conversion, so with `Foo(int)` the call `printFoo(5)` builds a `Foo` from `5` on its own. Only one user-defined conversion may take part in any implicit conversion sequence. Given `Employee(std::string_view)`, the call `printEmployee("Joe")` fails, because it would need `const char*` to `string_view` and then `string_view` to `Employee`, which is two. `printEmployee("Joe"sv)` or `printEmployee(Employee{"Joe"})` each leave one conversion for the compiler and compile.

Marking a constructor `explicit` removes it from implicit conversions. It can then still be used by direct-initialization `Dollars d(5)`, direct-list-initialization `Dollars d{5}`, explicit construction of a temporary `print(Dollars{5})`, and `static_cast<Dollars>(5)`. It is not considered for copy-initialization `Dollars d = 5;`, copy-list-initialization `Dollars d = {5};`, an argument `print(5)`, or a return statement `return 5;` or `return {5};` in a function returning `Dollars`. Note that `return {};` in a function returning a type with an explicit default constructor is also an error; `return Dollars{};` is required.

Make single-argument constructors explicit by default. The exception is when the constructed object is semantically the same thing as the argument and the conversion is cheap, as with `std::string_view` from a C string; `std::string` from a C string is also implicit for convenience, even though it allocates. Copy and move constructors perform no conversion and are never marked explicit. Default and multi-argument constructors are usually left implicit too, though `explicit` on a multi-argument constructor blocks `Foo f = {1, 2};` and `return {1, 2};` and is occasionally wanted for that.

## Destructors

A destructor is the member function that runs automatically when an object's lifetime ends: at the closing brace for a local, at `delete` for a heap object, at the end of the full expression for a temporary, and when the enclosing object is destroyed for a member. It is named with a tilde and the class name, takes no parameters, has no return type, and a class has exactly one. Locals in one scope are destroyed in reverse order of construction. If the class declares no destructor the compiler generates one with an empty body, which then runs the destructors of the members and bases, so a class made of `std::string` and `std::vector` members needs nothing written.

Write a destructor only when the object holds something that must be released or finished: memory acquired with `new`, a file handle, a socket, a queue that should be flushed on close. Doing the cleanup in the destructor means every path out of a scope, including early returns and exceptions, releases the resource without the caller remembering anything. That pattern is RAII, and it is why owning a resource through a member with its own destructor is preferred to writing cleanup by hand. A class that manages a resource in its destructor also needs correct copy and move behavior, which is the rule of five again.

A destructor can be called explicitly, `a.~A();`, but for an object with automatic storage that is almost always a bug. The call runs the body and ends the object's lifetime, while the name `a` and its storage remain until the closing brace, where the compiler destroys `a` again. Destroying an object whose lifetime has already ended is undefined behavior, and a program that prints `1` twice is only one of the outcomes. The legitimate use is manual lifetime management in storage you control: destroy the object explicitly, then either leave the storage dead or construct a new object in it with placement new before anything else, including scope exit, touches it. Containers and allocators do exactly this, as described in [allocators.md](allocators.md).

Two things skip destructors. `std::exit()` terminates the program without unwinding the stack, so no local's destructor runs; only static-storage objects are destroyed. An exception that is never caught may terminate without unwinding, and whether destructors run first is implementation-defined. Destructors should not let exceptions escape; the reasoning and the `noexcept` interaction are in [error_handling.md](error_handling.md).

## Nested types

A class is a scope region in the same way a namespace is, so enumerations, type aliases, and other classes can be declared inside it. Outside the class they are named through the class, `Fruit::Type` or `Employee::IDType`; inside member functions they are used unqualified. Nested types obey the access specifiers, so a public nested type is usable by outside code and a private one is not. Declare nested types at the top of the class, because a member cannot use a type that has not been defined yet.

A nested enumeration is usually an unscoped `enum` rather than an `enum class`: the class already provides the scope, so `Fruit::apple` reads well and `Fruit::Type::apple` would be a double qualification. Naming the nested enum `Type` rather than `FruitType` avoids repeating the class name at every use. A nested alias such as `using IDType = int;` documents the meaning of a member and lets callers write `Employee::IDType id{e.getId()};` without knowing the underlying type.

A nested class is a member of the enclosing class but not a part of its objects: it has no `this` pointer to the outer object and cannot touch outer members directly. It does have the access rights of a member, so when handed an `Employee&` it may read `e.m_name` even though that member is private. Forward-declaring a nested class is allowed inside the enclosing class, and after the enclosing class is complete as `class outer::inner;`, but not before the enclosing class exists.

```cpp
class Employee {
public:
    using IDType = int;
    enum Type { fullTime, contractor };
    class Printer {
    public:
        void print(const Employee& e) const { std::cout << e.m_name << ' ' << e.m_id; }  // private access, via the parameter
    };
private:
    std::string m_name{};
    IDType m_id{};
    Type m_type{fullTime};
};
Employee::Printer p{};
```

## Friends

A friend is a function or class that a class grants full access to its private and protected members. Friendship is always granted by the class being accessed, written inside its body, never claimed from outside. A friend non-member function is declared with `friend` in the class and is otherwise an ordinary non-member: it has no implicit object, so the class is passed explicitly, and it may be defined outside the class or inline inside the body, where it remains a non-member despite its position. Non-members read better when both operands deserve equal treatment, `isEqual(v1, v2)` rather than `v1.isEqual(v2)`, which is the reason symmetric operators are usually friends or plain non-members; see [expressions.md](expressions.md) for the hidden-friend and argument-dependent-lookup angle. One function can be a friend of several classes, which needs a forward declaration of the later class so the earlier friend declaration can name it.

```cpp
class Humidity;                       // forward declaration so Temperature can name it
class Temperature {
    int m_temp{};
public:
    explicit Temperature(int t) : m_temp{t} {}
    friend void printWeather(const Temperature&, const Humidity&);
};
class Humidity {
    int m_humidity{};
public:
    explicit Humidity(int h) : m_humidity{h} {}
    friend void printWeather(const Temperature&, const Humidity&);
};
void printWeather(const Temperature& t, const Humidity& h) {
    std::cout << t.m_temp << ' ' << h.m_humidity << '\n';
}
```

`friend class Display;` inside `Storage` lets every member function of `Display` use `Storage`'s private members, and the declaration doubles as a forward declaration of `Display`. Friendship has three limits worth stating in an interview. It is not reciprocal: `Storage` gains nothing from befriending `Display`. It is not transitive: a friend of a friend is a stranger. It is not inherited: classes derived from a friend are not friends. A single member function can be made a friend, `friend void Display::displayStorage(const Storage&);`, but the compiler must have seen the full definition of `Display` to name its member, while `displayStorage` itself needs the full definition of `Storage` to use its members. The single-file layout that satisfies both is: forward-declare `Storage`, define `Display` with only the declaration of `displayStorage`, define `Storage` with the friend declaration, then define `displayStorage` last. Splitting the classes into headers and source files removes the ordering problem entirely.

Friends couple the outside code to the class's representation, so a change to the private members ripples into every friend. Two rules of thumb follow. A friend should still prefer the public interface over direct member access when it can. And a function should be a non-friend whenever an accessor makes that possible: `print(const Accumulator&)` calling `acc.value()` needs no friendship and survives a representation change.

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
- **Invalid: default-initializing a const object of a class that is not const-default-constructible.** `struct C { C() = default; int i; }; const C c;` does not compile; `const C c{};` does and zeroes `i`.
- **Invalid: calling a non-const member on a const object.** `const X x; x.mutate();` is an error even though the body might not modify anything; the compiler trusts the declaration, not the body.
- **Invalid: calling a `&&` member on an lvalue.** `A a; a.foo(1);` where `foo` is `&&`-qualified is an error; `std::move(a).foo(1)` or `A{}.foo(1)` is required.
- **Invalid: `mf(x, 42)` on a pointer to member.** Use `(x.*mf)(42)` or `std::invoke(mf, x, 42)`.
- **Invalid: the most vexing parse.** `Y y(X());` declares a function named `y` returning `Y` and taking a pointer to a function returning `X`. Nothing prints, and the error surfaces later at `y.f()`, where `y` is a function, not a `Y`. See [initialization_deduction.md](initialization_deduction.md) for the rule and the fixes; `Y y{X{}};` is the idiomatic one.
- **Invalid: `=` in a member initializer list.** `Foo() : m_x = 5 {}` is a syntax error; use braces or parentheses.
- **Invalid: two default constructors.** `Foo()` alongside `Foo(int = 1)` makes `Foo{}` ambiguous.
- **Invalid: a delegating constructor that also initializes a member.** `Foo() : Foo(1), m_y{2} {}` is rejected; delegate or initialize, not both.
- **Undefined behavior: initializer list order that reads an uninitialized member.** Members initialize in declaration order, so `: m_y{...}, m_x{m_y}` with `m_x` declared first reads an indeterminate `m_y`.
- **Invalid: a by-value copy constructor.** `Fraction(Fraction f)` would need to copy its own parameter; the language rejects it.
- **Invalid: two user-defined conversions in one implicit sequence.** `printEmployee("Joe")` with `Employee(std::string_view)` fails; pass `"Joe"sv` or `Employee{"Joe"}`.
- **Invalid: copy-initialization through an explicit constructor.** `Dollars d = 5;`, `print(5)`, and `return {5};` all fail; `Dollars d{5}` and `Dollars{5}` work.
- **Logical error: counting copies by printing from the copy constructor.** Elision may remove the call, and since C++17 the prvalue cases are guaranteed to.
- **Undefined behavior: explicit destructor call on an automatic object.** `A a; a.~A();` destroys `a` twice, once by the call and once at scope exit.
- **Logical error: forwarding a move constructor's parameter by name.** `Car(Car&& other) : Vehicle(other)` copies the base; `Vehicle(std::move(other))` moves it.
- **Logical error: `obj(i);` is a declaration.** It declares a variable `i` of type `obj` with redundant parentheses and runs the default constructor; it is not a call or a cast.
- **Logical error: assuming a conditional with two different class types fails.** If exactly one operand converts to the other's type, the whole expression has that type and the conversion runs; see [expressions.md](expressions.md).
- **Logical error: expecting destructors after `std::exit`.** Locals are not unwound; only static-storage objects are destroyed.
- **Logical error: calling a constructor from a constructor body.** `Employee(name, id);` builds and destroys a temporary; the object being constructed is unchanged.
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

### Does `struct C { C() = default; int i; }; const C c;` compile?

No. A const object must be fully initialized at creation, and default-initializing this `C` would leave `i` indeterminate, so the language requires the class to be const-default-constructible: a user-provided default constructor, or default member initializers on every member that would otherwise be uninitialized. A defaulted constructor is not user-provided, so the declaration is rejected. Change it to `const C c{};` and `i` is value-initialized to zero, or write `C() {}` by hand and the program compiles and then reads an indeterminate `i`, which is undefined behavior.

### Is `C c2 = c1;` two operations, a construction and then a copy?

No. Copy-initialization from an object of the same type is one call to the copy constructor, which builds `c2` directly from `c1`. The `=` is initialization syntax; `operator=` never runs. The two-operation form is `C c3; c3 = c1;`, where `c3` is default-constructed and then copy-assigned. `C c2 = c1;` and `C c2(c1);` behave identically when the source is already a `C`; they differ only when a conversion is needed, because copy-initialization will not consider an `explicit` constructor. Before C++17, `C c = C(other);` could construct a temporary and copy it; since C++17 that elision is guaranteed and the temporary never exists.

### A class owns a `new[]` array with no user-declared copy operations. What does `B = A;` do?

The implicitly generated copy assignment does a memberwise copy, so `B.ptr = A.ptr` and `B.size = A.size`. B's old array is leaked because its only pointer was overwritten, and A and B now share one array while each believes it owns it. Nothing fails on that line. Later, writes through either object show up in the other, and at scope exit both destructors `delete[]` the same pointer, which is undefined behavior and usually a double-free abort. The fix is a user-written copy assignment that allocates and copies, or better, holding the array in a type that already does this, such as `std::vector` or `std::unique_ptr<int[]>`. See [smart_pointers_move.md](smart_pointers_move.md) for the rule of five and why raw owning pointers fail.

### Why must the copy constructor take its parameter by reference?

Because passing by value is itself a copy. To call `Fraction(Fraction f)` the compiler would have to copy the argument into `f`, and the only way to do that is the copy constructor being defined, so the call never bottoms out. The standard makes the by-value form ill-formed. `const Fraction&` is the right parameter: it binds to lvalues, temporaries, and const objects alike, and the copy constructor has no business modifying its source.

### What does `explicit` on a constructor actually block?

Implicit conversion through that constructor. Concretely, copy-initialization `T t = arg;`, copy-list-initialization `T t = {arg};`, passing `arg` where a `T` parameter is expected, and `return arg;` or `return {arg};` from a function returning `T`. It leaves direct-initialization, direct-list-initialization, explicit temporaries `T{arg}`, and `static_cast<T>(arg)` available, so the caller can always convert by saying so. The default rule is to mark single-argument constructors explicit unless the argument really is the same value in a different type and the conversion is cheap.

### When does a destructor not run?

When the program leaves through `std::exit` or `std::abort` rather than by unwinding, when an uncaught exception terminates without unwinding, when an object was allocated with `new` and never deleted, and when a constructor throws partway through, in which case the object's own destructor never runs though its completed members are destroyed. A moved-from object still gets its destructor, which is why move operations must leave the source in a state its destructor can handle.

### Why does `Car(Car&& other) : Vehicle(other)` call the base copy constructor?

Because `other` is a name. A named variable is an lvalue in any expression regardless of its declared type, so `Vehicle(other)` binds to `const Vehicle&` and copies. Only `Vehicle(std::move(other))` yields an rvalue that selects `Vehicle(Vehicle&&)`. The same mistake with members, `m_data(other.m_data)`, copies too. A move constructor is only a move if every base and member initializer casts its source with `std::move`.

### What does `A a; a.~A();` print?

Nothing you can rely on. The explicit call runs the destructor body and ends `a`'s lifetime, then the closing brace runs the destructor again on a dead object, which is undefined behavior. Printing `11` is the common outcome, not the answer. Explicit destructor calls belong only in code that manages object lifetime by hand inside storage it owns, followed by placement new or by never touching the storage as an object again.

### What is the type of `flag ? C{} : D{}` when `C` and `D` are different classes?

The compiler tries to form an implicit conversion sequence from each operand to the other's type. If exactly one direction works, the result has that type and the conversion is applied; if both work, or neither, the expression is ill-formed. With `D(const C&)` present and no way to make a `C` from a `D`, the type is `D`, so a function `auto f(bool flag) { return flag ? C{} : D{}; }` returns `D`. When the flag is true a `C` temporary is built and then converted to `D`, so the calls print the constructors in that order and always call `D::foo`.

### In `obj c();` and `obj(i);`, which is a declaration and which is a call?

Both are declarations. `obj c();` is the most vexing parse: a function named `c` returning `obj`, so no constructor runs and compilers warn. `obj(i);` is a declaration of a variable `i` of type `obj` with parentheses around the declarator, exactly like `int(x);`, so the default constructor runs. Neither creates a temporary. A temporary of type `obj` is spelled `obj{}` or `obj()` with nothing inside the parentheses at expression scope, such as `auto e = obj{};`.

### Trace every special member call: which constructor, assignment, or destructor runs, and when?

Given a class that prints a letter from each of its six special members (`a` default, `b` copy ctor, `c` move ctor, `d` copy assign, `e` move assign, `f` dtor), work through statements one at a time and account for every temporary.

```cpp
A foo(A a) {            // by-value parameter
    a = A();            // a: default ctor for the temporary, e: move assign, f: temporary dies at the semicolon
    std::cout << 'H';
    return std::move(a); // c: move ctor into the return value; a parameter can never be elided
}

int main() {
    A* p = new A;        // a
    foo(*p);             // b: copy ctor for the parameter ... then after the call, f f: parameter and discarded return value
    if (p) {
        A b = A();       // a only: C++17 guaranteed elision, no copy or move
        A c;             // a
        b = c;           // d
    }                    // f f: c then b, reverse order of construction
    std::cout << 'K';
    delete p;            // f
}
// prints abaefHcffaadffKf
```

The three places people slip. First, `a = A()` is three events, not one: the temporary is constructed, move-assigned from, and destroyed at the end of the full expression. Second, `return std::move(a)` from a by-value parameter runs the move constructor: named return value optimization never applies to parameters, so `return a;` would also have moved, and the explicit `std::move` changes nothing here but would defeat elision for a local. Third, two objects die when the call `foo(*p)` completes, the parameter and the unnamed return value that nobody bound; the parameter may be destroyed at function exit or at the end of the calling full expression, which is implementation-defined, but either way both `f`s print before the next statement. `A b = A();` prints only `a` because since C++17 the prvalue initializes `b` directly and no copy or move constructor is involved, however loudly they print.

### What does friendship grant, and what does it not?

A friend function or class gets access to the private and protected members of the granting class, nothing more: it does not become a member, gets no implicit object, and takes on none of the class's interface. Friendship is one-directional, not transitive, and not inherited, so befriending `Display` gives `Storage` no access to `Display`, a friend of `Display` gets nothing from `Storage`, and a class derived from `Display` is not a friend. The practical guidance is to keep friends few, let them use the public interface where they can, and reach for a non-friend plus an accessor when that suffices.

### Can a member function access the private members of another object of the same class?

Yes. Access control is per class, not per object. Any member function of `Person` can read and write `m_name` on any `Person` it holds a reference or pointer to, which is what makes member comparisons, copy constructors, and swaps writable without accessors. Access is about which code may touch a member, not which instance owns it.

### Should a getter return by value or by reference?

By value when the member is cheap to copy, such as an `int`. By `const T&` when it is expensive, such as a `std::string`, with the return type matching the member's type exactly. The reference is safe as long as it is used while the object is alive, so use it in the same expression or copy it out; saving a reference obtained from a temporary dangles at the end of the full expression. Never return a non-const reference to a private member, since that is public write access in disguise.

### What is the difference between data hiding and encapsulation?

Encapsulation is bundling data with the functions that operate on it into one type. Data hiding is making the data private so the only path in is the public interface. A class that does both is what people mean by an encapsulated class in C++. The payoff is that invariants are enforced in one place, validation is possible, the representation can change without breaking callers, and a bad value can only have been written by the class's own code.

## Practice history

- 12/09/2026: read learncpp 14.9 (constructors), 14.10 (member initializer lists), 14.11 (default constructors and default arguments), 14.12 (delegating constructors).
- 13/09/2026: read learncpp 15.3 (nested types), 15.8 (friend non-member functions), 15.9 (friend classes and friend member functions), the Friends and Enemies node.
- 13/09/2026: read learncpp 14.13 (temporary class objects), 14.14 (copy constructor), 14.15 (class initialization and copy elision), 14.16 (converting constructors and explicit), 15.4 (destructors).
- 13/09/2026 Special Member Functions node, per platform record: Don't end me. ok, It's hidden ok, Not this, again. ok, Do it for you. ok, I'm here! Now I'm gone. ok. Wrong first attempt (retest in a week): Stop! Don't move! (declaring an ordinary constructor does not suppress the implicit move constructor; copy ctor, copy assignment, and destructor do). Copying and Not Copying (`std::initializer_list<A> i{a}` copies the element once; `f(i)` copies only the handle; prints `1`). r-expression (`Car(Car&& other) : Vehicle(other)` copies the base because `other` is an lvalue; prints AD). Tear it out root and stem (`a.~A()` on an automatic object then scope exit destroys twice; UB). ? 1 : 2 -> auto (conditional with different class types converts toward the one reachable type; `auto` deduces `D`; prints cD2d2). 96% of you will fail this. (six init forms plus `obj c();` vexing parse and `obj(i);` declaration; prints 112312221). Who'd you call? wrong first attempt (full special-member trace; `a = A()` is ctor + move assign + dtor, `return std::move(param)` move-constructs since parameters are never elided, parameter and discarded return value both die at the call; prints abaefHcffaadffKf).
- 12/09/2026: read learncpp 14.1 (intro to OOP), 14.2 (intro to classes), 14.3 (member functions), 14.4 (const objects and const member functions), 14.5 (access specifiers), 14.6 (access functions), 14.7 (returning references to data members), 14.8 (data hiding and encapsulation).
- 12/09/2026 getcracked, per platform record (rescraped 13/09): Class vs Struct ok, Struct over Class ok, X ways (four overload aspects) ok, skibidi pointer ok, & and && (`A().doSomething()` picks `&&`, named object picks `&`, prints 21) ok. MISSED: Class inStruction (`class A; struct A {}` compiles, definition sets access). MISSED: wtf const (`const C c;` with `C() = default` and uninitialized `int i` is a compile error, not junk; const-default-constructible rule). MISSED: Haha… (`Y y(X());` most vexing parse, error at `y.f()`). MISSED: Invoke me. (`mf(x, 42)` invalid; `(x.*mf)(42)` or `std::invoke`). MISSED: Drop these. (out-of-class definition may drop top-level parameter const and the default argument). Notes on the platform's explanations: for Invoke me., `std::reference_wrapper` is callable, so its `ref(5)` "Wrong" example is itself wrong; for Drop these., `int* const` is top-level const and is dropped from the signature like `const int`, only `const int*` and `const int&` are part of the type.
- Anki: `x = T()` is three events (ctor, move assign, dtor); returning a by-value parameter always moves, never elides; a named rvalue reference is an lvalue, so `Base(other)` in a move ctor copies; explicit destructor call on an automatic object is UB (double destruction); `obj(i);` declares `i`; `?:` with two class types picks the one the other converts to; copy constructor parameter must be a reference; explicit blocks `T t = x`, `f(x)`, and `return {x}` but not `T t{x}`; one user-defined conversion per implicit sequence; members initialize in declaration order, not initializer-list order; `Foo() = default` is not user-provided, so `Foo{}` zero-initializes first; a delegating constructor cannot also initialize members; `const C c;` needs a user-provided default constructor or initializers on every member; top-level const on a parameter (including `int* const`) is not part of the signature; a default argument is given once, in the declaration; `.*` needs parentheses around the call; `&&`-qualified member is rvalue-only; members initialize in declaration order.

<!-- gc-questions:start -->

## Related getcracked questions

Pulled from the Beginner C++ progress tree. ✓ answered correctly, ✗ attempted and missed, ○ not attempted yet. Regenerate with `python3 cpp/tools/gc_links.py` after re-scraping.

### Classes and Structs
- ✓ [Class vs Struct](https://getcracked.io/question/372) — Cooked
- ✗ [Class inStruction](https://getcracked.io/question/1329) — Easy
- ✓ [Struct over Class](https://getcracked.io/question/373) — Easy
- ✗ [wtf const](https://getcracked.io/question/969) — Medium

### Member Functions
- ✗ [Invoke me.](https://getcracked.io/question/1398) — Easy
- ✓ [skibidi pointer](https://getcracked.io/question/1265) — Easy
- ✗ [Haha…](https://getcracked.io/question/802) — Medium
- ✓ [X ways](https://getcracked.io/question/1062) — Medium

### Const Classes and Functions & Access Specifiers
- ✓ [& and &&](https://getcracked.io/question/827) — Cooked
- ✗ [Drop these.](https://getcracked.io/question/1066) — Medium

### Special Member Functions
- ✓ [Don't end me.](https://getcracked.io/question/447) — Easy
- ✓ [It's hidden](https://getcracked.io/question/738) — Easy
- ✓ [Not this, again.](https://getcracked.io/question/871) — Easy
- ✗ [Stop! Don’t move!](https://getcracked.io/question/986) — Easy
- ✗ [Copying and Not Copying](https://getcracked.io/question/964) — Medium
- ✓ [Do it for you.](https://getcracked.io/question/985) — Medium
- ✓ [I'm here! Now I'm gone.](https://getcracked.io/question/822) — Medium
- ✗ [r-expression](https://getcracked.io/question/683) — Medium
- ✗ [Tear it out root and stem](https://getcracked.io/question/1299) — Medium
- ✗ [? 1 : 2 -> auto](https://getcracked.io/question/1006) — Hard
- ✗ [96% of you will fail this.](https://getcracked.io/question/418) — Hard
- ✗ [Who'd you call?](https://getcracked.io/question/1233) — Hard

<!-- gc-questions:end -->
