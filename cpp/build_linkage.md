# Build Pipeline, Linkage & the Preprocessor

## Build pipeline
- **preprocessor** (handles `#include`/`#define`, strips comments, ensures trailing newline, emits a translation unit) → **compiler** (TU → object file `.o`, unresolved references) → **linker** (all `.o` + std lib → executable).
- Translation phases: map source chars → splice lines → lex → preprocess → string literal encoding → concatenate adjacent literals → compile → instantiate templates → link.
- Compile error = language rule broken inside one TU. Linker error = compiler accepted a declaration, definition missing ("undefined reference") or found twice ("multiple definition").
- Every program has exactly one `int main()`: implicit `return 0`, can't be called from code, not always first to run (global initializers run before it; cross-TU order unspecified → static initialization order fiasco).
- Status codes: `0` / `EXIT_SUCCESS` / `EXIT_FAILURE` (<cstdlib>), returned to the OS.

## Declarations, definitions, ODR
- Declaration = identifier + type exists. Definition = declaration that implements/instantiates. Every definition is a declaration.
- Forward declaration `int add(int, int);` — param names optional, may differ from definition. Real purpose: definition lives in another TU.
- Signature = name + parameter types (NOT return type); return type alone can't overload.
- ODR: (1) one definition per TU per scope → CE; (2) one per program for non-inline functions/variables → link error; (3) types/templates/inline may repeat across TUs iff identical → violation is ill-formed NDR, linker silently picks one (worst failure mode).
- `inline` today = "multiple definitions allowed" (ODR rule 3), NOT a speed hint (-O2 inlines regardless). Definition must be visible in every using TU, once per TU, all identical. Why not inline everything: recompile cascade (every includer) + N compiles of the body.

## Preprocessor
- Macros: textual paste, NO scope (`#define` inside a function = top-of-file-from-here-down), no cross-file leak unless #included. SCREAMING_CASE to avoid collisions.
- Function-like macros paste args verbatim: `foo(a++, b++)` double-evaluates b (→ 121 quiz Q); `#define SQUARE(x) x * x` then `SQUARE(2+3)` = 2+3*2+3 = **11** (no parens added, ever). Armor: `((x)*(x))`; real fix: constexpr function.
- Conditional compilation: `#ifdef` / `#ifndef` / `#if 0` (the way to disable code containing `/* */`).
- Header guards `#ifndef X_H/#define X_H/#endif`: dedupe within one TU (ODR rule 1). Do NOTHING across TUs — non-inline definition in a guarded header still hits "multiple definition"; fix with `inline` or extern-declare + define in one .cpp.
- `#pragma once`: non-standard, universally supported, mainstream. Fails only on duplicated header files at two paths; classic guards survive that.
- Standard headers never break: guarded + contain only declarations/types/templates/inline.

## Keywords & identifiers
- 92 keywords (C++23); `override final import module` are special identifiers, not keywords.
- Identifiers: letters/digits/underscore, no leading digit, case-sensitive, not a keyword.
- Reserved (ill-formed NDR, compiles silently): `__` anywhere, `_X` (underscore+upper) anywhere, `_x` at global scope.

## Namespaces
- Declarations/definitions only; no executable statements at namespace scope.
- Alias: `namespace Active = Foo::Goo;`. Anonymous namespace = internal linkage (C++ file-`static`).
- Two `using namespace` pulling the same name → CE at the USE, not the using.

## Compile vs link vs NDR (examples)
- CE: undeclared `x = 5;`; `void main()`; calling `main()`; two definitions in one TU; overload on return type only; `int class = 5;`.
- Link: `int foo();` used, never defined → undefined reference. `int x = 1;` in two .cpp → multiple definition.
- NDR: `inline int f(){return 1;}` vs `{return 2;}` in two TUs; reserved identifiers.

## Quiz log
- 29/08 oral (7 Q): missed build stages (forgot preprocessor + object files), "copy assignment" vs copy-initialization, comment nesting (neither `//` nor `/* */` nests — `#if 0` for blocks).
- 30/08 getcracked "Bodyguard" — ok.
- 31/08 Claude quiz: MISSED `SQUARE(2+3)` = 11 — assumed the preprocessor parenthesizes; it pastes. Sibling of the double-eval trap.
- 31/08 Claude quiz: inline-identical-across-TUs = legal (ODR 3) — ok.

## Syntax anchors
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

## Traps / interview one-liners
- "Undefined reference is a linker error: the compiler saw a declaration and trusted you."
- "Guards solve within-TU duplication; inline/extern solve across-TU duplication."
- "`inline` is about linkage/ODR, not performance."
- "Header = declarations, .cpp = definitions; inline is what lets a definition live in a header."
- "`endl` = '\n' + flush (syscall per line in a hot loop). Use '\n'."
- "`/* */` doesn't nest."
- "Initialization constructs; assignment modifies. Ctor vs operator= for class types."
