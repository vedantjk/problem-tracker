# Scope

## Core model
- Three separate properties of a name/object:
  - **Scope**: where the identifier is visible (compile-time). Local vars: block scope.
  - **Storage duration**: when the object is created/destroyed. Local vars: automatic (created at definition, destroyed at end of block). Duration usually = lifetime.
  - **Linkage**: whether the same identifier declared elsewhere refers to the same entity. Local vars: none. (Internal/external come with globals.)
- Return by value: conceptually returns a temporary copy. In practice: C++17 guarantees elision for prvalues, NRVO for named locals.
- Shadowing: inner-block variable with the same name hides the outer one for the overlap. Global can still be reached with `::name`; a shadowed local can't.

## Questions (getcracked)
- [x] I am the shadows. — 29/08 — ok

## Traps / interview one-liners
- "Scope is about names, duration is about objects, linkage is about identity across scopes/TUs."
- "`-Wshadow` catches shadowing; it's a real bug source in constructors (`x = x;`)."
- "Returning by value is free in modern C++: guaranteed elision for prvalues, NRVO otherwise."
