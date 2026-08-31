# Operator Overloading

## Core model
- Can't overload: `?:`, `sizeof`, `::`, `.`, `.*`, `typeid`, the casts. Everything else mostly can.
- At least one operand must be a program-defined type (no redefining int + double).
- Fixed forever: arity, precedence, associativity. Overloading `^` for pow fails because `x^y + z` still parses as `x ^ (y + z)`.
- Overloaded `&&`/`||` LOSE short-circuiting (both sides always evaluate — they become normal function calls). Don't overload them.
- Three homes for an operator:
  1. **Member** — required for `=`, `[]`, `()`, `->`; natural when left operand is your type.
  2. **Friend non-member** — symmetric binary ops needing private access; both operands convert equally, so `6 + Cents{4}` works via `operator+(int, Cents)` (a member version can never convert its left operand).
  3. **Plain non-member** — preferred when the public interface suffices ("fewest functions touching internals wins"); don't add getters just to avoid friend.
- Mixed types need both orders; implement one by delegating: `operator+(int a, Cents b) { return b + a; }`.
- Friend defined inside the class body is still a non-member (found only by ADL — a quiz favorite).
- Return conventions: arithmetic → by value; compound assignment (`+=`) → `T&` (return *this); implement `+` in terms of `+=`. Comparison → bool; C++20: define `operator<=>` (+ `==`) and get all six for free.

## Compile errors vs gotchas
- CE: `Fraction{1,2} * Fraction{2,3}` when the operator takes non-const `Fraction&` — temporaries can't bind to non-const refs. Take `const T&`.
- CE: overloading with zero program-defined operands.
- Gotcha: member `operator+` makes `c + 6` work but `6 + c` fail — asymmetric conversions; that's the friend/non-member argument.

## Traps / interview one-liners
- "Precedence is unchangeable — that's why << for streams works (low precedence, left-assoc) and ^ for pow doesn't."
- "Overloaded && evaluates both sides: short-circuit is a property of the built-in only."
- "Rule of thumb: = [] () -> must be members; symmetric binaries as non-members; everything by const& ."
- "C++20 <=> collapses six comparison overloads into one (plus ==)."
