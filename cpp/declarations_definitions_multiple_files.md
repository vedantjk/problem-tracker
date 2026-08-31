# Declarations, Definitions, and Multiple Code Files

## Core model
- Compiler reads a file top to bottom; calling a function defined later is a compile error. Forward declaration fixes it: `int add(int, int);` (parameter names optional, preferred; may differ from the definition's).
- Real reason forward declarations exist: the definition lives in another file (or is a mutually recursive function). Declared, called, never defined → linker error.
- Declaration = tells the compiler an identifier exists and its type. Definition = a declaration that also implements/instantiates it. Every definition is a declaration.
- Signature = name + parameter types (not return type). Return type alone can't distinguish overloads.
- ODR:
  1. Per file, per scope: one definition of each function/variable/type/template → compiler error.
  2. Per program: one definition of each non-inline function/variable → linker error ("multiple definition").
  3. Types, templates, inline functions/variables may be defined in multiple files iff identical → violation is ill-formed NDR, linker silently picks one.

## Questions (getcracked)
- (node has no questions)

## Compile errors vs link errors vs NDR
Compile error:
- Same TU, two definitions: `int f(){return 1;} int f(){return 2;}` (ODR rule 1).
- Overload on return type only: `int f(int); double f(int);` — redeclaration conflict.

Link error:
- Declared + used, never defined: `undefined reference` (ODR rule 2a).
- Non-inline defined in a header included by two .cpp: `multiple definition` (ODR rule 2b).

Ill-formed NDR:
- `inline int f(){return 1;}` in a.cpp and `inline int f(){return 2;}` in b.cpp — linker silently picks one (ODR rule 3). Worst failure mode of the three.

## Traps / interview one-liners
- "Header contains declarations, .cpp contains definitions: that's ODR rule 2 in practice. `inline` is what lets a definition live in a header."
- "Undefined reference vs multiple definition: both linker, opposite ODR failures."
- "Two functions differing only in return type: redeclaration error, not overload."
