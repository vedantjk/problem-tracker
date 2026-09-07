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

## Errors and pitfalls

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

## Practice history

### Reading

- learncpp 22.1 Introduction to smart pointers and move semantics — read 07/09.
