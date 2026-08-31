# Comma and Conditional Operators

## Comma
- `a, b`: evaluate a, discard, evaluate b, return b's result. Fully sequenced (left before right).
- Lowest precedence of ALL operators, below assignment: `z = (a, b)` assigns b; `z = a, b` parses `(z = a), b` — assigns a, discards b.
- Legit uses: for-loop multi-update `for (i=0, j=n; i<j; ++i, --j)`; everything else is usually obfuscation.
- An overloaded operator, was unsequenced pre-C++17; C++17 sequenced it like the builtin.
- Inside brackets, comma means argument/element separation, not the operator: `f(a, b)` is two args; `f((a, b))` is one.

## Conditional (?:)
- Near-lowest precedence: `cout << (x<0) ? "a" : "b"` parses `(cout << (x<0)) ? ...` → prints 0. Parenthesize the whole ternary inside compound expressions.
- Branches unify to one type via usual arithmetic conversions: `true ? -1 : 2u` → 4294967295. Non-convertible branches → CE.
- Can be an lvalue when both branches are same-type lvalues: `(c ? a : b) = 5;` (C++ only, not C).
- Sequenced: condition first, then only the taken branch — `x ? ++y : ++z` is safe.
- Usable where statements can't go: initializers, constexpr expressions, member-init lists.

## Traps / interview one-liners
- "return a, b; returns b — a classic bug when someone 'returns two values'."
- "Comma in a subscript `arr[i, j]` was deprecated in C++20 and repurposed in C++23 for multidimensional operator[]."
