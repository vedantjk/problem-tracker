# Namespaces

## Core model
- Declarations/definitions only; no executable statements inside a namespace.
- Alias: `namespace Active = Foo::Goo;`.

## Questions (getcracked)
- (node has no questions)

## Compile errors
- Executable statement at namespace scope: `namespace N { std::cout << 1; }` — CE. (A variable definition with a side-effectful initializer is the legal workaround.)
- Ambiguous name after two `using namespace` pulls in the same name → CE at the *use*, not the using.

## Traps / interview one-liners
- "Anonymous namespace = internal linkage for everything inside, the C++ replacement for file-`static`."
