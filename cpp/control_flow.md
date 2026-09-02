# Control Flow (if / switch)

## Core model

### if / else
- `if (condition) statement;` — conditionally executes **one statement**. Want more than one → block `{}`.
- Condition is any expression convertible to `bool`: non-zero → `true`, zero → `false`. So `if (x)` reads "if x is non-zero".
- Chain with `else if`; final `else` is the catch-all.
- **Early return** is fine (modern style): bail out at the top for error/base cases instead of nesting.
- Anti-pattern: `if (cond) return true; else return false;` → just `return cond;` (the condition already IS the bool).

### switch — what it is
- Evaluates the condition expression **once**, then tests it for **equality** against constant case labels. Alternative to an `==` if-else chain: more readable, and makes it obvious the same expression is being tested every time.
- Condition must be an **integral or enum type** (or convertible to one). No floating point, no strings. `bool` technically compiles (it's integral) but use `if` for bools.
- Why integral only: compilers historically lower switch to a **jump table** — an array indexed by the value that jumps straight to the matching case. O(1) dispatch instead of sequential compares. (Same reason case labels must be compile-time constants.)

### switch — labels
- `case <constant-expression>:` — must be a constant, must match/convert to the condition's type. **All case values must be unique** (after conversion: `case 54:` and `case '6':` collide, since `'6'` == 54).
- `default:` — optional, at most one, conventionally last.
- Execution: matching case → run from its first statement **sequentially onward**; no match + default → run from default; no match + no default → skip the whole switch.
- Convention: don't indent labels relative to the switch block — they don't open scopes.

### Fallthrough
- A case label is **not** a terminator. Execution only stops at: end of switch block, `break`, or `return`. Otherwise it falls through into the next case's statements. `switch(2)` over cases 2/3/4/default with no breaks prints 2 3 4 5.
- `break` → exits the switch, continue after its `}`. `return` → exits the whole function.
- Rule: **every** label's statement group ends in `break` or `return` — including the last one.
- Intentional fallthrough (C++17): `[[fallthrough]];` — attribute on a null statement (semicolon required), documents intent + silences the compiler warning.
- **Sequential (stacked) case labels are NOT fallthrough** — no statements between labels means nothing to fall through; no attribute needed:
  ```cpp
  case 'a': case 'e': case 'i': case 'o': case 'u':
      return true; // vowel — replaces a chain of ||
  ```

### switch scoping
- Case labels **don't create blocks**: all statements after all labels live in the single switch-block scope. A variable declared under `case 1:` is in scope under `case 2:`.
- **Declaration** (no initializer) inside a case: allowed (declarations aren't executed — the variable exists in the whole switch scope). **Initialization** in a non-final case: **compile error**, because the switch could jump past the initializer into a later case where the variable is in scope but never initialized.
- Fix: give the case its own explicit block:
  ```cpp
  case 1:
  {
      int x{ 4 }; // OK — scope ends at the brace, can't be jumped into
      std::cout << x;
      break;
  }
  ```

## Questions (getcracked) / Quiz log
_(none yet — learncpp 4.10 / 8.5 / 8.6 read 01/09/2026)_

## Compile errors vs UB
Compile errors:
```cpp
switch (x)
{
case 54:
case 54:   // CE: duplicate case value
case '6':  // CE: '6' is 54 — duplicate after conversion
}

switch (1.5) {}          // CE: condition must be integral/enum, not floating point
case y:                  // CE: case label must be a constant expression

switch (x)
{
case 1:
    int z{ 4 };          // CE: initialization jumped over if x != 1 (later labels exist)
    break;
case 2:
    break;
}
```
UB:
```cpp
switch (x)
{
case 1:
    int y;   // declaration OK, in scope for the whole switch
    y = 5;
    break;
case 2:
    std::cout << y;  // x==2: jumped straight here, y never assigned → UB (uninitialized read)
    break;
}
```
The CE-vs-UB line: the compiler rejects a jump over an *initialization*, but a jump over a bare *declaration + later assignment* compiles, and reading it on the path that skipped the assignment is UB.

## Syntax anchors
```cpp
void printDigitName(int x)
{
    switch (x)              // evaluated once; integral/enum only
    {
    case 1:
        std::cout << "One";
        return;             // exits the function
    case 2:
        std::cout << 2 << '\n';
        [[fallthrough]];    // C++17: intentional — attribute on a null statement
    case 3:
        std::cout << "Three";
        break;              // exits the switch
    default:
        std::cout << "Unknown";
        break;              // last label still gets one
    }
    std::cout << " Ah-Ah-Ah!";  // break lands here
}

int abs(int x)
{
    if (x < 0)
        return -x;  // early return
    return x;
}
```

## Traps / interview one-liners
- Missing `break` = silent fallthrough into the next case; compilers warn, `[[fallthrough]];` is the "yes I meant it" marker.
- Stacked labels (`case 'a': case 'e': ...`) ≠ fallthrough — idiomatic OR.
- switch beats if-else chain when: one integral/enum expression, equality against a small constant set (evaluated once, jump-table-able). if-else when: ranges, `&&`/`||` of conditions, non-equality compares, floats, bools.
- Case labels share one scope → init in a non-final case is CE; wrap the case body in `{}` to initialize.
- `return cond;` not `if (cond) return true; else return false;`.
