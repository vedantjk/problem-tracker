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

## Compile errors vs UB
Compile error:
- Using a name before/outside its scope: `{ int x; } x = 5;`.
- Accessing a shadowed local (there's no `::` for locals — the outer one is simply unreachable; not an error to shadow, error to try to reach it).

UB:
- Returning a reference/pointer to a local: `int& f(){ int x=10; return x; }` — dangling on first use.
- Any use-after-scope through a saved pointer: `int* p; { int y=1; p=&y; } *p;`.

## Traps / interview one-liners
- "Scope is about names, duration is about objects, linkage is about identity across scopes/TUs."
- "`-Wshadow` catches shadowing; it's a real bug source in constructors (`x = x;`)."
- "Returning by value is free in modern C++: guaranteed elision for prvalues, NRVO otherwise."
