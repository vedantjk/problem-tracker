# Expressions: Sequencing, Munch, Comma/Ternary, Operators

## Sequencing / evaluation order
- UB rule: two unsequenced modifications of one scalar, or unsequenced modification + read, in one full expression. `++x * x++` UB; parens group, never sequence.
- Sequencing operators (left fully first): `&&`, `||`, `,`, `?:`.
- C++17: `<<`/`>>` left-to-right (`cout << x++ << x++` unspecified values, NOT UB); assignment RHS-before-LHS (`i = i++ + 1`, `arr[i] = i++` defined); `[]`, `->*`; function args indeterminately sequenced (`f(i++, i++)` unpredictable, not UB).
- Arithmetic `* + - /` never sequences: `x + x++` still UB.

## Prefix / postfix
- Prefix returns the lvalue (`++++x`, `++x = 5` compile); postfix returns rvalue copy (`x++++` CE). Postfix overload = dummy int param `T operator++(int)`. Prefer `++it` for class types (real temporary); ints identical after optimization.

## Maximal munch (lexing)
- Longest token first, left to right: `x+++++y` → `x ++ ++ + y` → `(x++)++` on rvalue → CE. Spaces break tokens: `x++ + ++y` = fine. `a+++b` = `a++ + b`. Pre-C++11 `vector<vector<int>>` `>>` bug = same principle.

## Comma
- `a, b`: evaluate a, discard, yield b. Fully sequenced. LOWEST precedence (below `=`): `z = (a, b)` → z=b; `z = a, b` → (z=a), b.
- For-loop multi-update is the legit use. In call parens, comma = separator; `f((a, b))` = one arg. `return a, b;` returns b. `arr[i,j]`: deprecated C++20, multidim subscript C++23.

## Conditional ?:
- Near-lowest precedence: `cout << (x<0) ? "a" : "b"` prints the bool → parenthesize the whole ternary in compound expressions.
- Branches unify via usual arithmetic conversions: `true ? -1 : 2u` → 4294967295. Non-convertible branches CE.
- Lvalue when both branches same-type lvalues: `(c ? a : b) = 5;` (C++ only).
- Condition sequenced before the taken branch; only that branch evaluates: `x ? ++y : ++z` safe.

## Operator overloading
- Can't overload: `?: sizeof :: . .* typeid` casts. Need ≥1 program-defined operand. Arity/precedence/associativity fixed forever (`^` for pow parses wrong).
- Overloaded `&&`/`||` LOSE short-circuit (function calls evaluate both sides). Don't.
- Homes: member (required for `= [] () ->`); friend non-member (symmetric ops needing privates — both operands convert, `6 + Cents{4}` works); plain non-member (preferred when public API suffices; don't add getters to avoid friend).
- Mixed types: both orders, delegate one to the other. Friend defined in-class = still non-member, found only via ADL.
- Returns: arithmetic by value; `+=` returns `T&`, build `+` on `+=`; C++20 `<=>` (+`==`) gives all six comparisons.
- CE: temporary can't bind non-const `T&` param (`Fraction{1,2} * Fraction{2,3}` with non-const operands). Take `const T&`.

## Questions (getcracked)
- [ ] One after the other — 30/08 — MISSED: `++x * x++` — didn't flag unsequenced mod+read UB.
- [ ] Munch munch munch! — 30/08 — MISSED: `x+++++y` — knew the principle, mis-split the greedy scan.

## Quiz log (Claude)
- 31/08: `a+++b` (a=2,b=2,c=3) — ok, munch miss not repeated.

## Syntax anchors
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

## Traps / interview one-liners
- "Same scalar modified twice (or mod+read) with no sequencing operator between → UB."
- "C++17 sequenced <<, =, [], and args — many old 'UB!' answers are now 'unspecified order'. Know the standard."
- "Unspecified ≠ UB: `f(g(), h())` picks an order; `++x * x++` may do anything."
- "Precedence is unchangeable — why << streams work and ^ pow doesn't."
- "Overloaded && evaluates both sides."
- "= [] () -> must be members; symmetric binaries non-member; params by const&."
