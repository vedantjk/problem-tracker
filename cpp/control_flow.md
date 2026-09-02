# Control Flow (if / switch / loops)

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

### while
- `while (condition) statement;` — condition checked **first**; false on entry → body never runs. Re-checked after each iteration.
- Intentional infinite loop: **`while (true)`** is the idiom (not `for(;;)`, though that's equivalent — omitted for-condition is treated as `true`). Exit via `return` / `break` / `exit` / exception.
- **Loop counters: use signed.** The classic unsigned bug:
  ```cpp
  unsigned int count{ 10 };
  while (count >= 0)   // always true — unsigned can't be negative
      --count;          // 0 → wraps to 4294967295 (defined wrap, but infinite loop)
  ```
  Same bug in for-form: `for (unsigned int i{ 9 }; i >= 0; --i)`. (Ties into size_t underflow loops → types_conversions.)
- Every-Nth-iteration action: `if (count % 10 == 0)` on the counter.
- Nested loops: declare the inner counter **inside** the outer body — it's recreated (and reinitialized) each outer iteration. Smallest scope needed, always.
- Naming: `i/j/k` fine by convention (Fortran heritage); descriptive (`count`, `index`) when it helps.

### do-while
- ```cpp
  do
      statement;
  while (condition);   // semicolon AFTER the (condition)
  ```
- Body runs **first**, condition checked after → always executes at least once. Use case: menu/input validation.
- **Scoping gotcha**: anything declared inside the do-block is dead before the `while (condition)` runs — variables the condition needs must be declared **outside** the loop.
- Best practice: favor plain `while` when it's an equal choice (condition at the bottom obscures the logic).

### for
- `for (init-statement; condition; end-expression) statement;`
- Order: **init once → condition (exit if false) → body → end-expression → back to condition**. End-expression runs *after* the body.
- Desugars to (note the extra scope braces — init variables have loop scope):
  ```cpp
  { init-statement; while (condition) { statement; end-expression; } }
  ```
- Any of the three parts can be omitted; `for (;;)` = infinite (omitted condition = true).
- Multiple counters: define together in init, advance with the comma operator in the end-expression — the one blessed comma-operator use (→ expressions):
  ```cpp
  for (int x{ 0 }, y{ 9 }; x < 10; ++x, --y)
  ```
- **Prefer `<` / `<=` over `!=`** in numeric conditions: if the counter can jump past the target (`i += 2` crossing an odd bound), `!=` spins forever, `<` still terminates.
- Off-by-one: `i < 5` vs `i <= 5` — say the intended count out loud ("runs for i = 1..5, that's <=").
- for vs while: for when there's an obvious loop variable; while when there isn't.

### Range-based for (for-each)
- `for (element_declaration : container) statement;` — element gets each element's **value** (not an index). Works on anything that knows its bounds: std::vector/array, non-decayed C arrays, list/map/set. Empty container → body just doesn't run.
- Element type choice (same legal-binding model as auto notes → initialization_deduction):
  - `auto` — you want to modify a **copy** (or elements are cheap scalars)
  - `auto&` — modify the **originals**
  - `const auto&` — just viewing. **Default to this**: if the element type later changes from `std::string_view` to `std::string`, plain `auto` silently starts deep-copying every element; `const auto&` stays free.
- **Decayed C arrays don't work** — a pointer carries no length, so the loop can't know where to stop → CE. (Array function parameters are always decayed → can't range-for over them.)
- **No index available** — by design: ranges like `std::list` have no indices. Need the index → manual counter or classic for.
- Reverse (C++20 ranges): `for (const auto& w : std::views::reverse(words))`.
- Doesn't iterate enumerations directly (enum is not a range).
- Beyond the page, the dangling trap: pre-C++23, `for (auto x : getObj().vec)` was UB — only the *full* range expression's temporary got lifetime-extended, not `getObj()` when you take `.vec` off it. **C++23 (P2718) fixed it**: all temporaries in the range expression now live for the whole loop. Know both halves for interviews.

### break / continue
- `break` terminates the enclosing loop **or switch**; execution resumes right after it. `return` exits the whole function (skips any code after the loop). Both only affect the **innermost** enclosing construct — C++ has no labeled break (unlike Java); escaping nested loops = flag, function + return, or (rarely) goto.
- `continue` ends the current iteration: jumps to the **bottom of the loop body**.
- **The gotcha**: in a for loop, continue still runs the end-expression (`++i` lives outside the body), so counting stays correct:
  ```cpp
  for (int count{ 0 }; count < 10; ++count)
  {
      if ((count % 4) == 0)
          continue;          // ++count STILL runs
      std::cout << count << ' ';
  }  // 1 2 3 5 6 7 9
  ```
  In a while/do-while, your `++count` is inside the body — continue placed above it **skips the increment → infinite loop**:
  ```cpp
  while (count < 10)
  {
      if (count == 5)
          continue;   // jumps past ++count below → stuck at 5 forever
      std::cout << count;
      ++count;
  }
  ```
  Moral: counted loops → for, so the increment is continue-proof.
- Style consensus (break/continue AND early returns): use them **when they simplify the logic** — trading a non-linear jump for less nesting and fewer flag booleans is usually a win. Middle ground for returns: validation returns at the top, one return after.

### Halts (exiting the program early) — `<cstdlib>`
- A **halt** is a function (not a keyword) that terminates the program. Normal vs abnormal termination: "normal" = expected exit (status code says success/failure, not how clean it was); "abnormal" = runtime error killed it.
- **`std::exit(code)`** — normal termination: destroys **static-duration objects**, flushes/does file cleanup, returns code to the OS. `return` from main implicitly calls it with the return value. **Does NOT run destructors for any local variables**, current function or anywhere up the call stack → breaks RAII. That's the headline gotcha.
- **`std::atexit(fn)`** — registers a callback run on `std::exit` (explicit OR implicit via main returning). `fn` takes nothing, returns nothing; pass the name, not a call. Multiple registrations run in **reverse** order.
- **`std::abort()`** — abnormal termination: **no cleanup at all** (no statics, no atexit, no locals), no status code. Called implicitly by e.g. failed `assert`.
- **`std::terminate()`** — the exception machinery's halt: called implicitly on an unhandled exception; by default it calls `std::abort()`.
- **`std::quick_exit()` / `std::at_quick_exit()`** — normal termination that *skips* destroying static objects. Exists for multithreaded programs: `std::exit` from one thread destroys statics other threads may still be using → crash.
- Cleanup matrix: locals — nobody destroys them; statics — exit yes / quick_exit no / abort no; atexit callbacks — exit only.
- Best practice: **only halt when there's no safe way to return normally from main.** Prefer exceptions for errors (they unwind → local destructors run). And robust programs assume they can die anyway (crash, kill, power loss) → autosave/journal rather than trust clean shutdown.

## Questions (getcracked) / Quiz log
_(none yet — learncpp 4.10 / 8.5 / 8.6 / 8.8-8.12 / 16.8 (range-for) read 01/09/2026)_

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

Loops — mostly logic bugs, not UB:
```cpp
while (count <= 10);   // semicolon = null body → infinite loop; the {} after is a separate block
unsigned int i{ 10 };
while (i >= 0) --i;    // NOT UB (unsigned wrap is defined) — just an infinite loop
```
One real UB: a loop with no observable side effects that never terminates is UB (forward-progress rule) — compilers may assume it exits and delete it. `while (true) {}` with an empty body is the canonical example (→ ub_catalog).

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

// loops
while (true)                       // idiom for intentional infinite loop
{
    char c{};
    std::cin >> c;
    if (c == 'n') break;
}

int selection{};                   // OUTSIDE the do-block — condition needs it
do
{
    std::cin >> selection;
}
while (selection < 1 || selection > 4);   // semicolon here

for (int x{ 0 }, y{ 9 }; x < 10; ++x, --y)   // multi-counter: comma in end-expression
    std::cout << x << ' ' << y << '\n';

std::int64_t pow(int base, int exponent)
{
    std::int64_t total{ 1 };
    for (int i{ 0 }; i < exponent; ++i)      // i < n runs exactly n times
        total *= base;
    return total;
}

// range-based for
std::vector<std::string> words{ "peter", "likes", "frozen", "yogurt" };
for (const auto& word : words)                       // const auto& = view, no copies
    std::cout << word << ' ';
for (const auto& word : std::views::reverse(words))  // C++20 <ranges>
    std::cout << word << ' ';

void print(int arr[])          // decayed to int* — no length
{
    for (int e : arr) {}       // CE: cannot range-for a decayed array
}

// halts
#include <cstdlib>
void cleanup() { std::cout << "cleanup!\n"; }   // no params, no return

int main()
{
    std::atexit(cleanup);   // name, not a call; runs on exit (reverse reg. order)
    std::exit(0);           // statics destroyed + atexit run; LOCALS NOT destroyed
    // std::abort();        // no cleanup at all; what assert failure calls
}
```

## Traps / interview one-liners
- Missing `break` = silent fallthrough into the next case; compilers warn, `[[fallthrough]];` is the "yes I meant it" marker.
- Stacked labels (`case 'a': case 'e': ...`) ≠ fallthrough — idiomatic OR.
- switch beats if-else chain when: one integral/enum expression, equality against a small constant set (evaluated once, jump-table-able). if-else when: ranges, `&&`/`||` of conditions, non-equality compares, floats, bools.
- Case labels share one scope → init in a non-final case is CE; wrap the case body in `{}` to initialize.
- `return cond;` not `if (cond) return true; else return false;`.
- Signed loop counters; `unsigned i >= 0` is forever-true (wrap, not UB).
- `while (cond);` — stray semicolon is a null body; the block below runs once, after the (infinite) loop.
- `<`/`<=` over `!=` in numeric loop conditions — survives the counter jumping past the bound.
- do-while: condition variables live **outside** the block; semicolon after `(condition)`.
- `for (int i{0}; i < n; ++i)` runs exactly n times — the off-by-one anchor.
- Side-effect-free infinite loop = UB (forward progress); `while(true)` with real work is fine.
- No halt runs local destructors — `std::exit` mid-function breaks RAII; exceptions unwind, halts don't.
- Cleanup matrix: statics — exit ✓ / quick_exit ✗ / abort ✗; atexit — exit only; locals — never.
- Unhandled exception → `std::terminate()` → (default) `std::abort()`.
