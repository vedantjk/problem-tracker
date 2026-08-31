# Keywords and Identifiers

## Core model
- 92 keywords as of C++23. `override`, `final`, `import`, `module` are identifiers with special meaning, not keywords (you can still name a variable `final`, don't).
- Identifier rules: letters, digits, underscore; can't start with a digit; case-sensitive; can't be a keyword.
- Reserved by the implementation (don't use, even though it compiles): anything with `__` anywhere, anything starting with `_` + uppercase, and `_`-prefixed names at global scope.

## Questions
- (node has no questions)

## Compile errors vs NDR
Compile error:
- `int class = 5;` — identifier can't be a keyword. `int 2fast;` — can't start with a digit.

Ill-formed, no diagnostic required (compiles silently, still wrong):
- `int _Reserved;` `int foo__bar;` at any scope, `int _global;` at global scope — reserved for the implementation.

## Traps / interview one-liners
- "`_Foo` and `foo__bar` compile but are reserved for the implementation; that's why std headers use `__x` internally."
