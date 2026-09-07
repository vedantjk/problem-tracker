# Expressions: Sequencing, Parsing & Operators

For the meanings of lvalue, xvalue, and prvalue, and how they affect reference binding and moving, see [value categories](value_categories.md).

## Precedence and sequencing answer different questions

Precedence and associativity determine how an expression groups. Sequencing determines which evaluations must happen before others. Parentheses can change grouping, but they do not generally impose an evaluation order.

Two unsequenced modifications of the same scalar, or an unsequenced modification and value computation using that scalar, cause undefined behavior. For example, `++x * x++` and `x + x++` are invalid for this reason. Multiplication and addition do not sequence their operands.

Built-in `&&` and `||` evaluate the left operand first and short-circuit when it determines the result. The built-in comma operator evaluates the left operand before the right. The conditional operator evaluates the condition first and then exactly one branch.

## Changes in C++17

C++17 added sequencing guarantees that matter when reading older interview questions:

- In shift expressions, the left operand is sequenced before the right operand. Consequently, `std::cout << x++ << x++` prints the original value followed by the incremented value, assuming valid arithmetic and ordinary stream behavior.
- Assignment evaluates the right operand before the left. Expressions such as `i = i++ + 1` and `arr[i] = i++` therefore have defined sequencing, although bounds and overflow must still be valid.
- Function parameter initializations are indeterminately sequenced relative to each other. In `f(i++, i++)`, one completes before the other, but the order is unspecified. This is different from unsequenced evaluations.
- Subscript expressions and pointer-to-member `->*` expressions also gained left-before-right guarantees.

```cpp
int i = 0;
std::cout << i++ << i++;      // Since C++17, this prints 01.
// f(i++, i++);               // Either argument may get the earlier value.
// int bad = i + i++;         // This still has undefined behavior.
```

Do not generalize these changes to arithmetic operators. The language version and the particular operator both matter. The [shift sequencing rule](https://eel.is/c++draft/expr.shift) and [function-call rules](https://timsong-cpp.github.io/cppwp/n4950/expr.call) describe the distinction.

## Prefix, postfix, and maximal munch

For built-in increment, prefix `++x` yields an lvalue referring to the updated object. Postfix `x++` yields the previous value as a prvalue. This explains why `++++x` can compile but `x++++` cannot. User-defined operators can choose other return types, although conventional overloads follow the same pattern.

A postfix increment overload uses a dummy `int` parameter, such as `T operator++(int)`. Prefer prefix increment for an iterator when the old value is not needed; postfix may require a temporary. For ordinary integers, optimization usually removes any unnecessary distinction.

Tokenization normally takes the longest available token, a rule called maximal munch. Thus `x+++++y` becomes `x ++ ++ + y`, leading to an invalid increment of the postfix result. Writing `x++ + ++y` makes the intended tokens clear. Similarly, `a+++b` becomes `a++ + b`. C++11 added special parsing support for closing nested templates with `>>`.

## Comma and the conditional operator

The built-in comma operator evaluates its left operand, discards that value, and yields the right operand. It has lower precedence than assignment. Therefore `z = (a, b)` assigns `b`, while `z = a, b` assigns `a` and then evaluates `b`. Commas separating function arguments are not comma operators; `f((a, b))` passes a single argument.

Comma expressions are useful in a for-loop update with multiple counters. `return a, b;` returns `b`, but this is usually less clear than an explicit statement. Comma expressions in subscripts were deprecated in C++20, and C++23 introduced multidimensional overloaded subscripts; do not rely on the old `arr[i, j]` spelling.

The conditional operator selects one of two expressions. Arithmetic branches use a common type, so `true ? -1 : 2u` produces an unsigned result. Its type rules also cover class types, pointers, and void expressions; they are broader than arithmetic conversion alone.

When both branches are same-type lvalues, the conditional result can itself be an lvalue: `(condition ? a : b) = 5` writes to the selected object. Parenthesize a conditional used with stream insertion, because `std::cout << condition ? "yes" : "no"` does not group as intended.

## Operator overloading

An overloaded operator must involve a class or enumeration type. Overloading cannot change precedence, associativity, or the number of operands. Operators such as `?:`, `sizeof`, `::`, `.`, `.*`, and `typeid` cannot be overloaded, nor can cast syntax.

Operators `=`, `[]`, `()`, and `->` have member-only forms. Symmetric binary operations often fit non-member functions so conversions can apply to either operand. Use a friend when access to private state is needed.

A friend function defined inside a class is still a non-member function. In an expression such as `a + b`, the compiler also searches for operators associated with the operand types; this is called argument-dependent lookup. That lets it find a friend operator defined inside their class, even when ordinary name lookup would not find it. This is often called the hidden-friend pattern.

Arithmetic operators conventionally return a new value. Compound assignment conventionally returns `T&`, and `operator+` can reuse `operator+=`. In C++20, `<=>` supplies ordering support; equality still needs attention. A defaulted comparison setup can provide the usual family of comparisons, but writing a custom `<=>` alone does not automatically define `==`.

Overloaded `&&` and `||` evaluate both operands; they do not provide built-in short-circuit behavior. Operand sequencing and short-circuiting are separate properties. For input operands, a `const T&` often accepts both existing objects and temporaries, unlike a non-const `T&`.

## Errors and pitfalls

First check tokenization and types, then check sequencing, then calculate the result. Keep “undefined behavior” separate from “unspecified order.” A program with unspecified argument order still has language constraints; a program with undefined behavior has no required outcome.

## Additional syntax examples

These are independent syntax sketches, including deliberately invalid examples marked `CE` (compile error). They are not one compilable program.

```cpp
int y = ++x * x++;    // UB: * sequences nothing (parens don't help)
++x && x++;           // ok: && sequences
(++x, x--);           // ok: comma sequences
arr[i] = i++;         // ok since C++17 (= sequences RHS first)
x + x++;              // still UB
std::cout << x+++++y; // CE: (x++)++ + y — rvalue++

z = (a, b);  // z = b
z = a, b;    // (z = a), b — comma below assignment
std::cout << (x < 0) ? "neg" : "pos";  // prints the bool!
true ? -1 : 2u;                        // 4294967295
(c ? a : b) = 5;                       // legal: same-type lvalue branches
```

## Interview Q&A

### Do parentheses fix an evaluation-order problem?

Usually not. Parentheses control how the expression groups, while sequencing rules control evaluation order. If an addition contains an unsequenced read and modification of the same variable, adding parentheses around the operands does not make it safe.

### Is f(i++, i++) undefined behavior?

Since C++17, the parameter initializations are indeterminately sequenced, so this alone is not undefined behavior. Either argument can receive the earlier value. Before C++17 it was undefined behavior. I would still avoid writing it because the unspecified order makes it hard to read.

### What does cout << x++ << x++ do in C++17 and later?

The left insertion is sequenced before evaluation of the later right operand. Starting from zero, it prints zero followed by one and leaves x equal to two. That guarantee comes from the shift-expression sequencing rules; it does not apply to ordinary addition.

### Why can postfix increment be more expensive for an iterator?

It needs to produce the old value, which can require copying the iterator before advancing it. Prefix returns the updated iterator directly in conventional implementations. If I do not need the old value, prefix expresses that intent and avoids a potentially unnecessary copy.

### Why avoid overloading logical AND?

Both operands are evaluated before the overloaded operation runs, so it cannot preserve built-in short-circuit behavior. Code that expects the left side to guard the right side can then become incorrect.

## Practice history

The entries below preserve the original practice record. Use the explanations above for the current rules and qualifications.

### Questions (getcracked)

- [ ] One after the other — 30/08 — MISSED: `++x * x++` — didn't flag unsequenced mod+read UB.
- [ ] Munch munch munch! — 30/08 — MISSED: `x+++++y` — knew the principle, mis-split the greedy scan.

### Quiz log (Claude)

- 31/08: `a+++b` (a=2,b=2,c=3) — ok, munch miss not repeated.
