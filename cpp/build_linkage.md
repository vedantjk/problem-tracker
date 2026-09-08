# Build Pipeline, Linkage & the Preprocessor

## Build pipeline

A typical C++ build has three main stages. The preprocessor handles directives such as `#include` and `#define`. The compiler translates each resulting translation unit into an object file. The linker combines object files and libraries, resolves references between them, and produces the executable.

A translation unit is roughly a source file together with the contents included into it, after preprocessing. An object file can contain compiled code and references to functions or variables whose definitions will be supplied during linking.

The standard describes finer translation phases: character processing, line splicing, tokenization, preprocessing, string-literal processing and concatenation, translation, template instantiation, and linking. These are a language model; a toolchain does not need a separate executable for every phase.

A compiler diagnostic usually concerns a language rule within a translation unit. An “undefined reference” from a linker usually means a needed definition was not supplied. Multiple definitions can also be diagnosed by the linker, although not every violation requires a diagnostic.

## Declarations, definitions, and the One Definition Rule

A declaration introduces or redeclares an entity and its properties. A definition supplies the function body or defines the object or type. Every definition is a declaration, but a declaration such as `int add(int, int);` does not define the function.

Forward declarations let code refer to an entity before its definition, including when the definition lives in another translation unit. Parameter names are optional in a function declaration and can differ from those in the definition. Ordinary functions cannot be overloaded solely by return type; parameter types distinguish the common overload cases.

The One Definition Rule (ODR) has two useful levels:

- A translation unit cannot contain multiple definitions of the same definable item.
- Across translation units, certain entities, such as classes, templates, and eligible inline functions and variables, can have multiple definitions under strict conditions. Several source files commonly receive these definitions by including the same header. The definitions must use the same sequence of tokens, meaning the individual names, keywords, operators, and other pieces of source text. Names inside the definitions generally need to refer to the same entities as well.

Calling an ordinary non-inline function is a common case that requires one definition somewhere in the program. The formal term for a use that requires an entity's definition is odr-use. A non-inline function or variable that is odr-used normally needs exactly one definition in the program; the detailed odr-use rules cover more than function calls.

Cross-file ODR violations can be ill-formed with no diagnostic required. A successful link therefore does not establish that the definitions are consistent.

## inline and headers

The most useful meaning of `inline` is its effect on the ODR. It allows an eligible definition to appear in multiple translation units, usually through a header. It does not force the compiler to substitute the function body at a call site, and a compiler can inline a function that lacks the keyword.

Putting implementation in a header also has costs: every including translation unit processes it, and changing it can trigger widespread recompilation. Keep ordinary declarations in headers and ordinary non-inline definitions in a source file. Templates, class definitions, and inline entities often need their definitions in headers.

Header guards prevent repeated inclusion within a translation unit. They do not make an ordinary global variable definition safe across different translation units.

```cpp
// counter.h
#ifndef COUNTER_H
#define COUNTER_H
extern int counter;             // This declares the shared object.
#endif

// counter.cpp
int counter = 0;                // This defines it once.
```

An `inline int counter = 0;` definition in a header is another option in C++17 and later. `#pragma once` is widely supported but is not standard C++; its behavior depends on the toolchain's recognition of file identity.

## Preprocessor and macros

Macros operate on preprocessing tokens and do not obey C++ block scope. A macro defined inside a function remains defined later in the file until it is undefined or the translation unit ends. It reaches another source file only through that file's preprocessing, such as an included header.

A function-like macro substitutes its arguments without adding parentheses. For example, `#define SQUARE(x) x * x` turns `SQUARE(2 + 3)` into `2 + 3 * 2 + 3`, which evaluates to 11. Writing `((x) * (x))` fixes the grouping but still evaluates an argument twice. An inline or `constexpr` function avoids that repeated evaluation.

Use `#ifdef`, `#ifndef`, and `#if` for conditional compilation. Block comments do not nest, so `#if 0` is often useful for temporarily disabling a block that contains comments. Disabled text must still satisfy the preprocessing rules, including valid comment and string tokenization.

## Names, namespaces, and main

Identifiers are case-sensitive and cannot begin with a digit. Keywords are reserved; identifiers such as `override` and `final` have special meanings in particular contexts. The keyword set changes with the language version, so recognizing their roles is more useful than memorizing a count.

Names containing a double underscore, or beginning with an underscore followed by an uppercase letter, are reserved to the implementation. Names beginning with an underscore are also reserved in the global namespace. Avoid these patterns for your own names.

Namespaces contain declarations and definitions, rather than standalone executable statements. A namespace alias, such as `namespace Active = Foo::Goo;`, provides a shorter name. An anonymous namespace is a common way to keep implementation details local to a translation unit. Bringing two namespaces into scope can make a later unqualified use ambiguous; the `using` directives themselves need not be erroneous.

In a hosted C++ program, `main` returns `int`. Reaching its end returns zero, and the program cannot call `main` itself. Static initialization and some dynamic initialization happen before its body starts. Cross-file initialization dependencies need particular care; see [initialization and deduction](initialization_deduction.md).

Use zero or `EXIT_SUCCESS` for successful termination and `EXIT_FAILURE` for failure. `std::endl` inserts a newline and flushes the stream. Prefer `'\n'` when a flush is unnecessary; a stream flush is not a portable promise of exactly one system call.

## Errors and pitfalls

An undeclared name, a call to `main`, or an overload distinguished only by return type requires a diagnostic. A missing used function definition commonly produces a linker error. Conflicting inline definitions across translation units may link successfully while still violating the ODR.

## Additional syntax examples

These are independent syntax sketches, including deliberately invalid examples marked `CE` (compile error). They are not one compilable program.

```cpp
#define PRINT_JOE
#ifdef PRINT_JOE
    std::cout << "Joe\n";   // compiled
#endif
#ifdef PRINT_BOB
    std::cout << "Bob\n";   // stripped
#endif
#if 0
    std::cout << "Steve\n";  /* nested comments fine here */
#endif

void foo() {
#define MY_NAME "Alex"   // no scope! top-of-file-from-here-down
}
int main() { std::cout << MY_NAME; } // works

#ifndef XYZ_H   // classic guard
#define XYZ_H
#endif

#define SQUARE(x) x * x
SQUARE(2 + 3)   // 2 + 3 * 2 + 3 = 11, not 25
```

## Interview Q&A

### What happens when you build a C++ program?

The preprocessor expands includes and macros. The compiler then compiles each translation unit into an object file, which may still refer to definitions elsewhere. The linker combines those files with libraries and resolves the references to produce the executable.

### How is a declaration different from a definition?

A declaration tells the compiler that an entity exists and describes it. A definition supplies the function body or defines the object or type. I can declare a function in a header and define it in a source file so other files can call it without containing its implementation.

### Does inline make a function faster?

It does not guarantee that. The keyword mainly lets an eligible definition appear in multiple translation units under the ODR. Whether a call is actually inlined is an optimization decision, so I would measure performance rather than infer it from the keyword.

### Why do header guards not prevent multiple-definition linker errors?

A guard prevents duplicate inclusion within one translation unit. Separate source files each have their own preprocessing, so each can still receive the same definition. I would use a declaration plus one source-file definition, or an appropriate inline definition.

### Why prefer a function over a function-like macro?

A function follows the type and scope rules and evaluates each argument once before entering the body. A macro substitutes tokens, which can change grouping or evaluate an expression multiple times. Parentheses solve the grouping issue but do not solve repeated evaluation.

## Practice history

The entries below preserve the original practice record. Use the explanations above for the current rules and qualifications.

### Quiz log

- 29/08 oral (7 Q): missed build stages (forgot preprocessor + object files), "copy assignment" vs copy-initialization, comment nesting (neither `//` nor `/* */` nests — `#if 0` for blocks).
- 30/08 getcracked "Bodyguard" — ok.
- 31/08 Claude quiz: MISSED `SQUARE(2+3)` = 11 — assumed the preprocessor parenthesizes; it pastes. Sibling of the double-eval trap.
- 31/08 Claude quiz: inline-identical-across-TUs = legal (ODR 3) — ok.

<!-- gc-questions:start -->

## Related getcracked questions

Pulled from the Beginner C++ progress tree. ✓ answered correctly, ✗ attempted and missed, ○ not attempted yet. Regenerate with `python3 cpp/tools/gc_links.py` after re-scraping.

### What, Why, and When?
- ✓ [C++ is a…](https://getcracked.io/question/1210) — Easy

### The Preprocessor and Header Guards
- ✓ [Bodyguard](https://getcracked.io/question/1291) — Easy

<!-- gc-questions:end -->
