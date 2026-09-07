# Smart Pointers and Move Semantics

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

The fix is to give ownership to an object that has a destructor. A local object of class type is destroyed when its scope ends, on every path, including exceptional ones, which is Resource Acquisition Is Initialization applied to memory. A smart pointer is exactly that: a class that holds a raw pointer, deletes it in its destructor, and overloads `*` and `->` so it reads like a pointer.

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

The same thing happens through any copy, including passing an `Auto_ptr1` by value or returning one from a function, so a copyable smart pointer is unusable as written. There are only two coherent answers. Either copying is forbidden and ownership is transferred instead, or copying is allowed and the copies share the resource with a count that decides who deletes last. Those two answers become `std::unique_ptr` and `std::shared_ptr`.

## Transferring ownership before C++11: std::auto_ptr

Before C++11 there was no language mechanism to distinguish "copy this" from "move this," so the only way to transfer ownership was to make the copy operations do it. The copy constructor takes a non-const reference, steals the pointer, and nulls the source.

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

The lesson C++11 drew from `auto_ptr` is that copying and moving are different operations and need different syntax. C++11 added rvalue references, written `T&&`, which bind to temporaries and to objects the programmer has explicitly marked as movable. A class can now provide a move constructor and move assignment operator that take `T&&`, alongside ordinary copy operations that take `const T&`. Overload resolution picks the move operations when the source is an rvalue and the copy operations when it is an lvalue, so `b = a` copies and `b = std::move(a)` moves, and the difference is visible at the call site.

With that distinction available, a smart pointer can delete its copy operations outright and provide only move operations. That is `std::unique_ptr`: sole ownership, no copying, transfer only through an explicit move. `std::shared_ptr` takes the other branch, copyable with a reference count, and `std::weak_ptr` observes a `shared_ptr` without owning. The mechanics of rvalue references, move constructors, and `std::move` follow in later sections. For the parameter-passing conventions, sink by value versus borrow by reference, see [pointers and references](pointers_references.md). For the state of a moved-from object, see the [UB catalog](ub_catalog.md).

## Errors and pitfalls

Deleting the same pointer twice is undefined behavior. It is the natural consequence of two owning objects holding one address, which is why an owning type must decide whether it is copyable or move-only before anything else.

A copy constructor that mutates its source is a design error even when it compiles, because every generic algorithm and container assumes copying is non-destructive. Use move operations for transfers.

Using `std::auto_ptr` in new code is a compile error in C++17 and later. Its replacement for sole ownership is `std::unique_ptr`; replace `auto_ptr<T[]>`-style array ownership with `unique_ptr<T[]>` or a container.

## Interview Q&A

### Why do smart pointers exist?

Because a raw owning pointer relies on the programmer to write delete on every exit path, and early returns and exceptions skip it. A smart pointer moves the delete into a destructor, so cleanup runs automatically on scope exit regardless of how the scope is left. It is RAII applied to heap memory.

### What goes wrong if you write a naive owning class?

The compiler-generated copy operations copy the pointer, so two objects own the same resource and it is deleted twice. An owning type has to choose: forbid copying and transfer ownership with a move, which is unique_ptr, or allow copying with shared ownership and a count, which is shared_ptr.

### What was wrong with std::auto_ptr?

It transferred ownership through its copy constructor and copy assignment, because C++98 had no way to express a move. That meant passing one by value silently nulled the caller's pointer, `b = a` mutated `a`, containers could not hold it safely, and it always used delete rather than delete[]. It was deprecated in C++11 when rvalue references made real move semantics possible, and removed in C++17. unique_ptr is its successor.

### Why did C++11 need rvalue references to fix this?

Before C++11, copy syntax was the only way to construct one object from another, so a class had to choose one meaning for it. Rvalue references let a class provide separate copy and move operations, and overload resolution selects the move when the source is a temporary or has been explicitly marked with std::move. Ownership transfer becomes visible at the call site and copying stays non-destructive.

## Practice history

### Reading

- learncpp 22.1 Introduction to smart pointers and move semantics — read 07/09.
