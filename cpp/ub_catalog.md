# Undefined Behavior & Behavior Taxonomy

## The behavior categories

The first task in a tricky C++ example is to identify the language contract. Calculating a likely machine result comes afterward. A program that compiles and runs can still violate a rule.

| Category | Meaning | Example |
|---|---|---|
| Ill-formed with a required diagnostic | The implementation must diagnose a violation; it need not refuse to emit a binary afterward. | Initializing int from a string literal is invalid. |
| Ill-formed, no diagnostic required | The program is invalid, but the implementation is not required to detect it. | Conflicting inline definitions across translation units can violate the ODR. |
| Implementation-defined behavior | The implementation selects and documents a permitted behavior. | The signedness of plain char is implementation-defined. |
| Unspecified behavior | The implementation can choose among permitted possibilities without documenting which one occurs. | Function argument evaluation order has unspecified choices. |
| Undefined behavior | The standard places no requirements on the behavior of the execution. | Signed arithmetic overflow is undefined behavior. |
| Erroneous behavior, introduced in C++26 | The standard identifies incorrect behavior that implementations are recommended to diagnose. | Certain uses of erroneous uninitialized values fall into this category. |

“Compile error” is convenient shorthand in these notes for a rule requiring a diagnostic. “No diagnostic required” is abbreviated NDR, and undefined behavior is abbreviated UB. They are distinct categories, not interchangeable labels for something undesirable.

## Why undefined behavior matters to optimization

The compiler can assume a well-defined execution does not perform an operation with undefined behavior. For example, after a dereference that requires a non-null pointer, a later null check may be redundant under that assumption. The result is not merely a random number at the offending line; optimization can change surrounding code.

Undefined behavior also permits implementations to use different hardware without specifying an expensive common outcome for every invalid operation. A processor's observed wrap or masked shift count does not override the C++ contract.

Some rules change by language version. C++20 defined additional integer conversions and shifts, while C++26 distinguishes indeterminate and erroneous uninitialized values and makes a specific exception for trivial infinite loops. Always state the standard version for these questions.

## Uninitialized reads in C++26

An ordinary local declaration such as `int x;` leaves `x` uninitialized. Allocating an integer with `new int` also leaves its value uninitialized. Through C++23, an ordinary read of either uninitialized integer has undefined behavior.

C++26 distinguishes these storage cases. Ordinary local variables have automatic storage, whose bytes can begin with erroneous values. Storage obtained with `new` is dynamic storage, whose bytes generally begin with indeterminate values. These are two different classifications of uninitialized data, not usable initial values.

```cpp
int local;
int* allocated = new int;
// In C++26, evaluating local's value here has erroneous behavior.
// Evaluating *allocated's value here has undefined behavior.
delete allocated; // Deallocation does not read the uninitialized integer.
```

Special declarations and a few permitted operations on character and byte types add qualifications. For an ordinary integer read, however, an indeterminate value still leads to undefined behavior, while an erroneous value leads to erroneous behavior. C++26 therefore does not make all uninitialized reads erroneous instead of undefined, and neither classification makes these reads safe. Initialize objects before reading their values. See the [current indeterminate/erroneous-value rules](https://eel.is/c++draft/basic.indet).

## Catalog of common violations

Each item links to the file that explains its mechanism and safe alternatives:

- [Initialization](initialization_deduction.md) covers reads of uninitialized scalars and the version-dependent classification.
- [Integer arithmetic](types_conversions.md) covers signed overflow, including INT_MAX + 1, negating INT_MIN, and INT_MIN / -1.
- [Shifts](types_conversions.md) covers negative counts and counts at least as large as the promoted left operand's width.
- [Floating point](floating_point.md) covers conversions whose truncated value is outside the destination integer range.
- [Expressions](expressions.md) covers unsequenced modifications, or a modification and read, of the same scalar.
- [Functions](functions_scope_lambdas.md) covers reaching the end of an ordinary non-void function without returning a result.
- [Pointers and references](pointers_references.md) covers invalid dereferences, null function-pointer calls, dangling results, and pointer arithmetic outside its permitted range.
- [Lambdas](functions_scope_lambdas.md) covers using reference captures after the referenced local has died.
- [Type punning](bits_punning.md) covers invalid typed access, misalignment, and modification of originally const objects through a cast.
- [Bits](bits_punning.md) covers unchecked bitset access outside its bounds, with language/library version qualifications.
- [Types](types_conversions.md) covers invalid bool representations and out-of-range conversions into enums without a fixed underlying type.
- [Error handling](error_handling.md) covers optional and expected access without satisfying the corresponding state precondition.
- [Memory management](memory_layout.md) covers buffer overflow, use-after-free, double free, invalid free, and mismatched allocation/deallocation families.
- A data race involving conflicting unsynchronized accesses, at least one a write, can cause undefined behavior. A const access path or thread-safe static initialization does not synchronize later mutation.

A memory leak is a resource-management bug, but leaking an allocation is not by itself undefined behavior. It matters especially in long-running programs, even though the OS ordinarily reclaims a process's address space on termination.

## Related cases that are not the same category

Conflicting inline definitions across translation units are an ODR issue with no diagnostic required; see [build and linkage](build_linkage.md). Reserved identifier misuse has its own library/language restrictions and is not a useful way to test whether a compiler catches every invalid program.

Padding can make bytewise comparisons unsuitable for semantic equality. That is not a blanket claim that every memcmp of structs is undefined behavior. See [memory layout](memory_layout.md) for why member comparisons express the intended equality.

Unspecified order still constrains execution to permitted possibilities. For example, C++17 parameter initializations do not interleave, even though their order is unspecified. Implementation-defined behavior adds a documentation obligation; it is not another spelling of unspecified.

## Moved-from objects

Unless otherwise specified, moved-from standard-library objects are in a valid but unspecified state. Valid means the object's invariants still hold and operations are usable when their preconditions are satisfied. Unspecified means the prior content is not generally promised to be preserved or emptied.

For a moved-from string or vector, querying size or assigning a new value is fine. Accessing front, back, or an indexed element still requires a suitable size. Moving did not create a special exception to the normal bounds requirements.

Some types specify a stronger postcondition. Moving ownership into a distinct unique_ptr leaves the source null; a moved-from shared_ptr is empty. Do not extend those guarantees to every container or to self-move assignment without checking its separate contract.

Small-string optimization may cause character bytes to be copied internally during a move. It does not imply that the source string must retain its original logical contents. A user-defined type's moved-from behavior follows its own contract; design it so destruction and intended reuse remain safe.

`std::move` is a cast that enables move-aware overload resolution. It does not itself transfer resources. The receiving constructor or assignment operator performs the transfer, if one is selected.

## Checking a suspicious example

First identify the types and the language version. Then check lifetime, initialization, bounds, arithmetic range, sequencing, and synchronization. Only after those checks should you predict an output.

Warnings such as `-Wall -Wextra -Wconversion`, AddressSanitizer, UndefinedBehaviorSanitizer, and alignment checks help find mistakes that are exercised. Ordinary UBSan is not a complete strict-aliasing detector. Type-focused tools and compiler flags have their own limitations. A clean sanitizer run cannot prove that every execution is valid.

Flags such as `-fwrapv` and `-fno-strict-aliasing` change particular compiler assumptions. They do not fix unrelated lifetime, bounds, or synchronization violations, and the resulting implementation contract must be understood explicitly.

## Interview Q&A

### What does undefined behavior mean?

It means the standard imposes no requirements on that execution. I cannot promise a crash, a wrapped number, or even that the surrounding checks behave as they appear in source. I identify the violated rule before trying to predict a machine result.

### How are unspecified and implementation-defined behavior different?

Both allow choices within the language contract. Implementation-defined behavior requires the implementation to document its choice. Unspecified behavior does not. Neither gives the unrestricted outcome of undefined behavior.

### If the program compiled and passed sanitizers, is it valid?

That is useful evidence, but not a proof. Some invalid programs require no diagnostic, and sanitizers only detect supported errors along exercised paths. I still need to reason about the contracts, especially lifetimes, aliasing, bounds, and concurrency.

### Can I use an object after moving from it?

For standard-library types, it is generally valid but its value may be unspecified unless the type promises more. I can destroy it or assign a new value, and other operations need their usual preconditions. I would not call front on a moved-from container without first establishing that it is nonempty.

### Does std::move move anything by itself?

No. It casts its argument so a move-aware overload can be selected. The selected constructor or assignment operator performs the actual work, and a copy can still occur if the available overloads or const qualification require it.

### Did C++26 make uninitialized reads safe?

No. It introduced erroneous behavior for some uninitialized-value uses while retaining undefined behavior for others. The classification depends on the value and context. The programming rule remains to initialize a value before reading it.

## Practice history

The entries below preserve the original practice record. Use the explanations above for the current rules and qualifications.

### Questions (getcracked)

- [x] _global_variable — 29/08 — ok
