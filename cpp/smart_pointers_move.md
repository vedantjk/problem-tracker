# Smart Pointers and Move Semantics

For the meanings of lvalue, xvalue, and prvalue, and how they affect reference binding and moving, see [value categories](value_categories.md).

## Why raw owning pointers fail

A raw pointer that owns a heap object depends on the programmer writing `delete` on every path out of the function. That contract breaks in ordinary code. An early return skips the delete. An exception thrown between the `new` and the `delete` skips it too, because the abandoned statements never run. Nothing about a pointer variable knows that it owns anything, so nothing happens automatically when it goes out of scope.

```cpp
void someFunction()
{
    Resource* ptr = new Resource();
    int x;
    std::cin >> x;
    if (x == 0)
        return;          // ptr is never deleted
    delete ptr;
}
```

The fix is to give ownership to an object that has a destructor. A fully constructed local object of class type is destroyed on normal scope exit and during exception unwinding. Putting resource cleanup in that destructor is Resource Acquisition Is Initialization (RAII) applied to memory. Abrupt termination, such as `std::abort`, does not provide this cleanup. An owning smart pointer wraps a pointer and releases its ownership in its destructor; `*` and `->` let the caller access the managed object.

```cpp
template <typename T>
class Auto_ptr1
{
    T* m_ptr{};
public:
    Auto_ptr1(T* ptr = nullptr) : m_ptr(ptr) {}
    ~Auto_ptr1() { delete m_ptr; }
    T& operator*() const { return *m_ptr; }
    T* operator->() const { return m_ptr; }
};
```

With `Auto_ptr1<Resource> res(new Resource());` the resource is released whether the function returns early, returns normally, or unwinds through an exception. See [error handling](error_handling.md) for the unwinding rules that make this work.

## The shallow-copy problem

The first version has a fatal flaw: the compiler-generated copy constructor and copy assignment copy the pointer. Two objects now hold the same address, both destructors run, and the same resource is deleted twice. Double delete is undefined behavior and in practice corrupts the heap allocator's bookkeeping.

```cpp
Auto_ptr1<Resource> res1(new Resource());
Auto_ptr1<Resource> res2(res1);   // shallow copy: same m_ptr in both
// end of scope: res2 deletes it, then res1 deletes it again
```

The same thing happens through any copy, including passing an `Auto_ptr1` by value or returning one from a function, so a copyable smart pointer is unusable as written. Two common ownership designs solve this problem. One forbids copying and transfers ownership through moves; the other allows copies to share ownership and counts the owners to decide when to delete. These are the designs of `std::unique_ptr` and `std::shared_ptr`. A different owning class could instead define copying to create a separate resource, which is called a deep copy.

## Transferring ownership before C++11: std::auto_ptr

Before C++11 there were no rvalue references for defining distinct move operations. `std::auto_ptr` expressed ownership transfer through its copy operations instead. The copy constructor takes a non-const reference, steals the pointer, and nulls the source.

```cpp
template <typename T>
class Auto_ptr2
{
    T* m_ptr{};
public:
    Auto_ptr2(T* ptr = nullptr) : m_ptr(ptr) {}
    ~Auto_ptr2() { delete m_ptr; }

    Auto_ptr2(Auto_ptr2& a)              // non-const: the source is modified
    {
        m_ptr = a.m_ptr;
        a.m_ptr = nullptr;
    }

    Auto_ptr2& operator=(Auto_ptr2& a)
    {
        if (&a == this) return *this;
        delete m_ptr;
        m_ptr = a.m_ptr;
        a.m_ptr = nullptr;
        return *this;
    }

    T& operator*() const { return *m_ptr; }
    T* operator->() const { return m_ptr; }
    bool isNull() const { return m_ptr == nullptr; }
};
```

This is what `std::auto_ptr` did, and it is why `std::auto_ptr` was deprecated in C++11 and removed in C++17. The problems were not bugs in the implementation; they were consequences of using copy syntax for a move.

Passing an `auto_ptr` by value silently transfers ownership into the parameter, which deletes the resource when the function returns, and the caller is left holding null without any sign in the call that anything happened. Copy syntax that mutates its source violates every reader's expectation that `b = a` leaves `a` alone. Standard containers copy elements freely, so an `auto_ptr` inside a `std::vector` had its ownership stolen by operations that were supposed to be non-destructive, and the library formally forbade it. And `auto_ptr` always called `delete`, never `delete[]`, so it could not own a dynamic array correctly.

## What C++11 changed

The lesson C++11 drew from `auto_ptr` is that copying and moving are different operations and need different syntax. C++11 added rvalue references, written `T&&`, which bind to temporaries and to objects the programmer has explicitly marked as movable. A class can now provide a move constructor and move assignment operator that take `T&&`, alongside ordinary copy operations that take `const T&`. For a class with the usual copy and move overloads, an ordinary lvalue such as `a` selects copying, while a non-const source expressed as `std::move(a)` can select moving. The available overloads and source type still matter: `std::move` does not guarantee that a move operation exists or is selected.

With that distinction available, a smart pointer can delete its copy operations outright and provide only move operations. That is `std::unique_ptr`: sole ownership, no copying, and ownership transfer through move operations. `std::shared_ptr` takes the other branch, copyable with a reference count, and `std::weak_ptr` observes a `shared_ptr` without owning. Here is the modern replacement for the earlier owning-pointer sketches:

```cpp
#include <memory>
#include <utility>

void example()
{
    auto first = std::make_unique<int>(42);
    auto second = std::move(first);
    // first is now empty. second owns the int containing 42.
    // When second is destroyed, it deletes that int.
}
```

`std::make_unique<int>(42)` creates the int and returns its owner. `std::move(first)` expresses `first` as a source that may be moved from; it does not transfer the pointer by itself. Constructing `second` from that expression invokes `unique_ptr`'s move constructor, which transfers ownership and leaves `first` empty. Writing `auto second = first;` would request a copy and fail to compile. Other types define their own moved-from state, so the empty-source guarantee here is specific to `unique_ptr`. For the parameter-passing conventions, sink by value versus borrow by reference, see [pointers and references](pointers_references.md). For the state of a moved-from object, see the [UB catalog](ub_catalog.md).

## Using std::move

`std::move`, from `<utility>`, is a cast. It takes an lvalue and returns it as an rvalue reference, which is what lets overload resolution pick a move operation for an object that has a name. It performs no move itself; whether anything is transferred depends on the constructor or assignment that receives the result. See [value categories](value_categories.md) for the expression-level view.

The canonical demonstration is swap. Written with copies, swapping two objects costs one copy construction and two copy assignments, each of which may allocate. Written with `std::move` it costs three moves, each a pointer shuffle:

```cpp
template <typename T>
void mySwapMove(T& a, T& b)
{
    T tmp{ std::move(a) };   // move construct: a is now moved-from
    a = std::move(b);        // move assign
    b = std::move(tmp);      // move assign
}
```

This is why sorting algorithms and container reallocation got faster in C++11 without any change to their source: every swap and every element relocation became a move for types that support it. The same cast is how a value is handed into a container without copying, `v.push_back(std::move(str))`, and how ownership passes between smart pointers, `auto q = std::move(p)`.

The rule for when to write it: only on an object whose current value you no longer need. After the move the source is in a valid but unspecified state, so it may be assigned to, cleared, reset, or destroyed, but operations that depend on its contents, such as indexing or `front()`, are not safe without first establishing what it holds. Moving a value out and immediately moving a new value in, without touching the object in between, is a normal and safe pattern. The full moved-from contract is in the [UB catalog](ub_catalog.md).

## Move constructors and move assignment

A copy constructor and copy assignment operator take `const T&` and produce an independent object, which for an owning type means allocating a new resource and copying the contents. A move constructor and move assignment operator take `T&&` and instead take over the source's resource, leaving the source in a state that is safe to destroy. For a pointer-owning class the transfer is a pointer copy followed by nulling the source, which is what makes moving cheap.

```cpp
template <typename T>
class Auto_ptr4
{
    T* m_ptr{};
public:
    Auto_ptr4(T* ptr = nullptr) : m_ptr(ptr) {}
    ~Auto_ptr4() { delete m_ptr; }

    Auto_ptr4(const Auto_ptr4& a)                 // copy: allocate and deep copy
        : m_ptr(a.m_ptr ? new T(*a.m_ptr) : nullptr) {}

    Auto_ptr4(Auto_ptr4&& a) noexcept             // move: steal and null the source
        : m_ptr(a.m_ptr)
    {
        a.m_ptr = nullptr;
    }

    Auto_ptr4& operator=(const Auto_ptr4& a)
    {
        if (&a == this) return *this;
        delete m_ptr;
        m_ptr = a.m_ptr ? new T(*a.m_ptr) : nullptr;
        return *this;
    }

    Auto_ptr4& operator=(Auto_ptr4&& a) noexcept
    {
        if (&a == this) return *this;
        delete m_ptr;                             // release what we held
        m_ptr = a.m_ptr;
        a.m_ptr = nullptr;
        return *this;
    }

    T& operator*() const { return *m_ptr; }
    T* operator->() const { return m_ptr; }
};
```

The move operations are selected when the initializer or right-hand side is an rvalue: a temporary such as a function's return value, or an lvalue the caller has cast with `std::move`. With an lvalue source the copy operations are selected. Overload resolution makes that choice, so `mainres = generateResource();` moves and `mainres = other;` copies, and nothing in the class body needs to test which case it is in.

Nulling the source is not optional. Both objects have destructors, and if the source still pointed at the resource after the transfer, its destructor would delete what the destination now owns. The moved-from object must remain valid enough to be destroyed and assigned to; for this class that means holding null. The self-assignment check matters less for moves than for copies because `x = std::move(x)` is rare, but it costs one comparison and keeps the delete from destroying the very resource about to be stolen.

Mark move operations `noexcept`. The reason is concrete rather than stylistic: `std::vector` must keep its strong exception guarantee when it reallocates, so it moves elements into the new buffer only if their move constructor cannot throw, and otherwise falls back to copying them. The library makes that decision with `std::move_if_noexcept`. A move constructor that is not declared `noexcept` makes every vector of that type copy on growth, silently throwing away the benefit of having written it. A move that only shuffles pointers and integers has nothing to throw, so the declaration is honest.

## When the compiler writes the move operations for you

The compiler generates an implicit move constructor and move assignment operator only when the class declares none of the following: a copy constructor, a copy assignment operator, a move constructor, a move assignment operator, or a destructor. Declaring any one of them, including declaring a destructor that does nothing, suppresses the implicit moves, and the class falls back to copying wherever a move would have been selected. This is a common cause of silently slow code: a class that adds a logging destructor and loses its move operations.

The generated moves are memberwise. Each member is moved if its type has a move operation and copied otherwise. A raw pointer member is copied, not nulled, so a class that owns through a raw pointer cannot rely on the implicit move; it has to write both moves by hand, as `Auto_ptr4` does. A class that owns through members that already move correctly, such as `std::unique_ptr`, `std::string`, or `std::vector`, needs no user-declared special members at all. That is the rule of zero: keep ownership inside members that manage themselves and declare nothing.

The rule of five is the other half. If a class declares or deletes any one of the copy constructor, copy assignment, move constructor, move assignment, or destructor, it should make a deliberate decision about all five, because declaring one changes what the compiler generates for the others. For an owning type that manages a raw resource, that means writing all five. Deleting the copy operations, `T(const T&) = delete;` and `T& operator=(const T&) = delete;`, is how a class states that it is move-only, which is exactly what `std::unique_ptr` does. Deleting the move operations as well makes the class immovable. Deleting only the moves while leaving copies is a trap: a deleted function still participates in overload resolution, so an rvalue source selects the deleted move and fails to compile instead of falling back to the copy.

A local object returned by value is treated as an rvalue in the return statement even though its name is an lvalue, so `return res;` moves rather than copies when copy elision does not remove the operation entirely. Writing `return std::move(res);` is at best redundant and at worst defeats named return value optimization; see [copy elision](functions_scope_lambdas.md) and [value categories](value_categories.md).

One implementation trap: writing move assignment as `std::swap(*this, other)` recurses forever, because `std::swap` is itself implemented with move construction and move assignment of the type. A class that wants swap-based assignment writes its own member swap that exchanges the members directly, then implements move assignment in terms of that.

## std::unique_ptr

`std::unique_ptr<T>`, from `<memory>`, is the move-only owning pointer that `auto_ptr` should have been. It holds one pointer, deletes it in its destructor, and has its copy constructor and copy assignment deleted, so the only way ownership leaves one `unique_ptr` for another is a move. After `auto second = std::move(first);` the source is guaranteed null; that is a stronger promise than the general valid-but-unspecified rule and is specific to this type. The `unique_ptr` itself lives on the stack or inside another object; allocating a `unique_ptr` dynamically defeats the purpose, because then something else has to remember to delete it.

Access looks like a raw pointer. `*p` yields the object, `p->member` reaches into it, and `p` converts to `bool` in a condition, true when it owns something. Three member functions cover the rest. `p.get()` returns the raw pointer without giving up ownership, which is how the object is handed to code that only needs to look at it. `p.reset()` deletes what it owns and becomes null, or with an argument deletes what it owns and takes the new pointer. `p.release()` gives up the raw pointer and becomes null without deleting, which transfers responsibility to the caller and is the one call that can leak if the result is dropped.

Prefer `std::make_unique<T>(args...)`, available since C++14, over `std::unique_ptr<T>{ new T(args...) }`. It states the type once, it never shows a naked `new`, and before C++17 it closed an exception-safety hole. In `f(std::unique_ptr<T>{ new T }, g())`, the pre-C++17 evaluation rules allowed `new T` to run, then `g()` to run and throw, before the `unique_ptr` was constructed around the raw pointer, leaking the `T`. C++17 sequenced function arguments so that cannot interleave, but `make_unique` never had the problem and remains the idiom.

`std::unique_ptr<T[]>` owns an array and calls `delete[]`; `make_unique<T[]>(n)` creates one. It exists for interoperating with APIs that hand out arrays. For anything else `std::vector` or `std::array` is the better choice, since they carry their size and grow.

Returning a `unique_ptr` by value is the normal way to hand ownership out of a function. The return expression is treated as an rvalue, so the caller's variable is move-constructed, or the move is elided entirely. Never return a raw pointer or a reference to the managed object from such a factory; the caller could not tell whether it owns the result.

For parameters, the spelling states the contract. Taking `std::unique_ptr<T>` by value is a sink: the caller must write `std::move(p)` at the call site, which makes the transfer visible, and the callee now owns the object. Taking `T&` or `const T*` borrows: the caller passes `*p` or `p.get()`, keeps ownership, and the callee's signature does not mention smart pointers at all, so it also works with stack objects and other owners. Taking `std::unique_ptr<T>&` is rare and means the function may replace what the caller owns. Taking `const std::unique_ptr<T>&` is almost always wrong; it forces callers to have a `unique_ptr` while giving the callee nothing a `const T*` would not. See [pointers and references](pointers_references.md) for the sink-versus-borrow discussion.

A `unique_ptr` member makes the enclosing class correct by default. The implicit destructor releases the resource, the implicit move operations transfer it, and copying is deleted automatically because a member is non-copyable. That is the rule of zero in practice: the class declares no special members and gets ownership right. Two consequences to know. The class becomes move-only unless a copy constructor is written that clones the resource. And if `T` is an incomplete type at the point where the class's destructor is implicitly defined, the compile fails inside `unique_ptr`'s deleter, which is why the pimpl idiom declares the destructor in the header and defines it in the source file where `T` is complete.

The second template parameter is the deleter, defaulting to `std::default_delete<T>`, which calls `delete`. A custom deleter lets `unique_ptr` own anything with a release function: a `FILE*` closed with `fclose`, memory from `malloc` freed with `free`, a handle from a C library. A stateless deleter such as a lambda or a functor with no members adds no size, so the `unique_ptr` stays pointer-sized. A function-pointer deleter is stored, so it doubles the size to two words. Prefer the functor.

```cpp
struct FileCloser { void operator()(FILE* f) const { if (f) std::fclose(f); } };
std::unique_ptr<FILE, FileCloser> file{ std::fopen("log.txt", "r") };   // still 8 bytes

std::unique_ptr<FILE, int(*)(FILE*)> file2{ std::fopen("x", "r"), &std::fclose }; // 16 bytes
```

The misuses all come from mixing a raw pointer with the owner. Constructing two `unique_ptr`s from the same raw pointer produces a double delete. Deleting the raw pointer yourself while a `unique_ptr` still owns it produces a double delete when the owner is destroyed. Keeping a raw copy of `p.get()` past the owner's lifetime produces a dangling pointer. Using `make_unique` everywhere removes the raw pointer from the picture at the moment of creation, which removes the first two entirely.

## Errors and pitfalls

Constructing two `unique_ptr`s from one raw pointer, or calling `delete` on a pointer a `unique_ptr` owns, double-deletes. `make_unique` prevents both by never exposing the raw pointer.

`p.release()` with the result discarded leaks. It exists to hand ownership to something that is not a `unique_ptr`; store the result.

`std::unique_ptr<T>` with a function-pointer deleter is two words, not one. Use a stateless functor or lambda to keep it pointer-sized.

A user-declared destructor, even an empty one, suppresses the implicit move operations. The class then copies where it would have moved, with no diagnostic. Either remove the destructor or declare the moves as `= default`.

A move constructor without `noexcept` causes `std::vector` to copy elements on reallocation rather than move them.

Forgetting to null the source's pointer in a move leaves two owners and produces a double delete when the source is destroyed.

Deleting the same pointer twice is undefined behavior. It is the natural consequence of two owning objects holding one address, which is why an owning type must decide whether it is copyable or move-only before anything else.

A copy constructor that mutates its source is a design error even when it compiles, because every generic algorithm and container assumes copying is non-destructive. Use move operations for transfers.

Using `std::auto_ptr` in new code is a compile error in C++17 and later. Its replacement for sole ownership is `std::unique_ptr`; replace `auto_ptr<T[]>`-style array ownership with `unique_ptr<T[]>` or a container.

## Interview Q&A

### Why do smart pointers exist?

A raw owning pointer relies on the programmer to arrange cleanup, and an early return or exception can skip a later delete. An owning smart pointer puts that responsibility in its destructor, so normal scope exit and exception unwinding release its ownership automatically. That is RAII applied to heap memory; abrupt program termination does not guarantee destructor calls.

### What goes wrong if you write a naive owning class?

The compiler-generated copy operations copy the pointer, so two objects own the same resource and it is deleted twice. The type needs an explicit ownership policy. unique_ptr forbids copying and transfers ownership through moves; shared_ptr permits copies that share ownership. A value-like owning class could instead copy the resource itself.

### What was wrong with std::auto_ptr?

It transferred ownership through its copy constructor and copy assignment, using copy syntax rather than a separate move operation. That meant passing one by value silently nulled the caller's pointer, `b = a` mutated `a`, containers could not hold it safely, and it always used delete rather than delete[]. It was deprecated in C++11 when rvalue references made real move semantics possible, and removed in C++17. unique_ptr is its successor.

### Why did C++11 need rvalue references to fix this?

Rvalue references let a class provide distinct copy and move overloads. With the usual overloads, a non-const temporary or a non-const object expressed through std::move can select the move operation. std::move only changes how the source expression is treated; the selected constructor or assignment performs the transfer. This lets unique_ptr prohibit copying while allowing ownership transfer.

### What does a move constructor do, and why noexcept?

It takes an rvalue reference to the source, takes over the source's resource, and leaves the source safe to destroy, which for a pointer-owning class means copying the pointer and nulling the original. I mark it noexcept because std::vector only moves elements during reallocation if the move cannot throw; otherwise it copies to preserve its strong exception guarantee. A pointer shuffle has nothing to throw, so the declaration is honest and it keeps vectors of the type fast.

### When does the compiler generate move operations?

Only when the class declares no copy constructor, no copy assignment, no move operations, and no destructor. Declaring any one of them, even an empty destructor, suppresses the implicit moves and the class silently copies instead. The generated moves are memberwise, and a raw pointer member is copied rather than nulled, so a class that owns through a raw pointer has to write its moves by hand. If ownership lives in members like unique_ptr or string, I declare nothing and let the compiler do it, which is the rule of zero.

### What is the rule of five?

If I declare or delete any of the copy constructor, copy assignment, move constructor, move assignment, or destructor, I should decide about all five, because declaring one changes what the compiler generates for the rest. Deleting the two copy operations is how I make a type move-only. Deleting the moves while keeping copies is a trap, because a deleted move still wins overload resolution for an rvalue and the code fails to compile instead of copying.

### Should you write return std::move(local)?

No. A local returned by value is already treated as an rvalue in the return statement, so it moves without the cast, and copy elision may remove the operation entirely. Adding std::move can prevent named return value optimization, so it is redundant at best and slower at worst.

### Why prefer make_unique over unique_ptr with new?

It names the type once, keeps a naked new out of the code, and before C++17 it closed an exception-safety hole: in a call with two arguments, new could run, then another argument could throw, before the unique_ptr wrapped the raw pointer, leaking it. C++17 fixed the sequencing, but make_unique never had the problem and stays the idiom.

### How do you pass a unique_ptr to a function?

By value when the function takes ownership, and the caller writes std::move so the transfer is visible. By T& or const T* when the function only uses the object, passing *p or p.get(), so the signature does not force callers to own through a unique_ptr. By unique_ptr& only if the function may replace what the caller owns. I avoid const unique_ptr&, which constrains the caller for no benefit.

### What does a unique_ptr member do to a class?

It makes the class correct by default: the implicit destructor releases the resource, the implicit moves transfer it, and copying is deleted because the member is non-copyable. The class becomes move-only unless I write a copying constructor that clones the resource. If the pointee is incomplete in the header, I declare the destructor there and define it where the type is complete, which is the pimpl pattern.

### How big is a unique_ptr?

One pointer with the default deleter or any stateless deleter, because an empty deleter takes no storage. A function-pointer deleter has to be stored, so that spelling is two words. I use a functor or a captureless lambda for custom deleters to keep it pointer-sized.

## Practice history

### Reading

- learncpp 22.1 Introduction to smart pointers and move semantics — read 07/09.
- learncpp 22.2 Rvalue references — read 07/09 (binding table and named-is-lvalue rule live in value_categories.md).
- learncpp 22.3 Move constructors and move assignment — read 07/09.
- learncpp 22.4 std::move — read 07/09.
- learncpp 22.5 std::unique_ptr — read 07/09.
