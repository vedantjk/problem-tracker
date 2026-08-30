# Keywords and Identifiers

## Core model
- 92 keywords as of C++23. `override`, `final`, `import`, `module` are identifiers with special meaning, not keywords (you can still name a variable `final`, don't).
- Identifier rules: letters, digits, underscore; can't start with a digit; case-sensitive; can't be a keyword.
- Reserved by the implementation (don't use, even though it compiles): anything with `__` anywhere, anything starting with `_` + uppercase, and `_`-prefixed names at global scope.

## Questions
- (node has no questions)

## Traps / interview one-liners
- "`_Foo` and `foo__bar` compile but are reserved for the implementation; that's why std headers use `__x` internally."
