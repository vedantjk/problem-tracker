# Control Flow: Conditions, Loops & Program Termination

## if, else, and early returns

An if statement conditionally executes one statement, which can be a block enclosed in braces. Its condition is contextually converted to bool. For arithmetic values, zero is false and nonzero is true; pointers and suitable class types have their own boolean conversion behavior.

An else-if chain tests alternatives in order, and the final else handles the remaining cases. Use braces to make the controlled statements clear. If a bool result is already available, `return condition;` is clearer than returning true and false in separate branches. For a non-bool expression with only an explicit bool conversion, an explicit conversion may be needed in a return expression.

Early returns are useful for invalid input and base cases because they reduce nesting. Choose them when they simplify the function's control flow and keep resource management in RAII objects whose destructors run on ordinary scope exit.

## switch and case labels

A switch evaluates its condition once and transfers control to a matching constant case label. It supports integral and enumeration conditions, including class values with a suitable contextual conversion. It does not directly switch on strings or floating-point values.

Use a switch when one value is compared for equality against a set of constants. Use if/else for ranges, unrelated conditions, and more general predicates. A compiler may implement a switch as a jump table, comparisons, or another strategy. The language's type restriction does not guarantee a jump table or constant-time dispatch.

Case values must be valid converted constant expressions and must be unique after conversion. On an ASCII-compatible system, `case 54:` and `case '6':` collide. Default is optional and appears at most once. If nothing matches and there is no default, execution skips the switch body.

Case labels are entry points, not boundaries that stop execution. After entering, statements continue until control leaves through a break, return, throw, another transfer, or the end of the switch. Missing a break can therefore execute the following case's statements.

```cpp
switch (kind) {
case Kind::first:
    handle_first();
    break;
case Kind::second:
    prepare_second();
    [[fallthrough]];           // Intentional fallthrough, since C++17.
default:
    handle_remaining();
    break;
}
```

The `[[fallthrough]];` attribute documents an intentional transition to a following case or default label and can suppress warnings. Consecutive labels such as `case 'a': case 'e':` share a statement group and need no intervening attribute. A final break is a useful convention even where reaching the end already exits.

## Case scope and initialization

Case labels do not introduce scopes. A variable's name is in scope from its declaration onward within the surrounding block, potentially including later cases. A switch transfer can therefore jump into that scope.

The language rejects jumps that bypass disallowed initialization. A declaration such as `int x;` is a permitted trivial scalar case, but `int x = 4;` is not. Merely omitting `=` does not make every declaration safe: `std::string s;` still runs a constructor and cannot be bypassed in the same way.

```cpp
switch (choice) {
case 1: {
    std::string message = "ready";
    use(message);
    break;
}
case 2:
    break;
}
```

The explicit block limits the variable's scope to that case, so later labels cannot jump into it. If a permitted scalar declaration is bypassed and a later case reads the scalar before assignment, that is an uninitialized-read problem, not a dependable “garbage value.”

## while and do-while

A while loop checks its condition before each iteration, so its body may never run. A do-while loop runs the body first and checks afterward, so it executes at least once. The do-while syntax requires a semicolon after the final condition.

A variable declared inside a do-block is out of scope at the following while condition. Declare state needed there in an enclosing scope. In either loop, a stray semicolon can create an empty body: `while (condition);` does not control the block that visually follows it.

Both `while (true)` and `for (;;)` are common ways to spell an intentional endless loop. Its correctness still depends on the exit and progress behavior, described below. A loop that repeatedly checks unsigned `i >= 0` has an always-true condition; unsigned wrap will not make it negative.

## for loops and continue

A for loop runs its initializer once, checks its condition before the body, executes the body, and then evaluates its iteration expression. Omitting the condition means true. Variables declared in the initializer have loop scope.

A while-loop expansion can illustrate the order, but it is not equivalent if it mishandles continue. In a for loop, continue still executes the iteration expression before checking the condition again. In a while or do-while loop, continue skips the remaining body, including an increment written there.

```cpp
for (int i = 0; i < 5; ++i) {
    if (i == 2) continue;
    std::cout << i;            // Prints 0134; ++i still runs after continue.
}
```

For multiple counters, declare compatible variables together and use a comma expression in the update, such as `for (int x = 0, y = 9; x < 10; ++x, --y)`. Each inner loop should normally declare its counter inside the outer loop body so it is reset on each pass.

For numeric counters, a condition such as `< limit` tolerates stepping past the limit better than `!= limit`. This is a numerical-loop guideline, not a reason to replace ordinary iterator comparisons. State the intended bounds explicitly to avoid off-by-one errors. Use signed counters when negative values are meaningful, and make sure their type can represent the required range.

## Range-based for

A range-based for obtains a beginning and an end from a range and initializes its element declaration from each dereferenced iterator. It works with bounded arrays and suitable range types, not just standard containers. A bare pointer has no bound, and an array parameter written `int arr[]` is adjusted to a pointer, so it cannot supply one by itself.

For ordinary containers, choose the element declaration deliberately:

- `auto value` makes a value from the element, usually a copy.
- `auto& value` binds to the element and allows modification when its type permits it.
- `const auto& value` avoids copying and provides read-only access.

Proxy references, such as some bit containers use, can make plain auto behave differently from a simple independent element copy. In generic range code, consider `auto&&` when binding to the iterator's reference result.

The basic loop does not provide a numeric index. Use an explicit counter or classic indexed loop when needed. An enum type by itself is not an iterable collection of enumerators.

## Range temporaries and reverse traversal

The hidden range reference can extend a temporary range's lifetime. Even before C++23, direct member access such as `makeOwner().items` can extend the owning temporary's lifetime when items is an ordinary non-reference data member. A member function returning a reference, such as `makeOwner().items()`, is a different case.

C++23 extends additional temporaries in the range initializer, fixing many of those member-function cases. It does not rescue a reference returned to a destroyed by-value function parameter. An explicit owner in a C++20 for-init statement makes the lifetime clear: `for (auto owner = makeOwner(); const auto& x : owner.items())`. See the [range-for rules](https://timsong-cpp.github.io/cppwp/n4950/stmt.ranged).

For reverse iteration, `std::views::reverse` in C++20 works directly in a range-based loop. Alternatively, use `rbegin()` and `rend()` in an iterator loop, or wrap them in a suitable `std::ranges::subrange`. `crbegin()` and `crend()` provide const access. `std::reverse` instead mutates the sequence's order.

A reverse iterator's `base()` points one position after the element it denotes in forward traversal. Do not dereference that base blindly; it can be the end iterator. For a valid reverse iterator into a suitable container, an erase expression such as `v.erase(std::next(it).base())` accounts for the offset. Normal iterator-invalidation rules still apply.

For index-based reverse iteration, a sufficiently wide signed index is straightforward. An unsigned alternative is `for (std::size_t i = v.size(); i-- > 0;)`. The decrement wraps on the final failed check, but the loop body never uses that wrapped value. Account for it if the counter is declared outside the loop and inspected afterward.

## break, continue, and forward progress

Break leaves the innermost enclosing loop or switch. Continue targets the innermost enclosing loop, even if a switch is nested inside it. Return leaves the entire function, including all enclosing loops. C++ has no labeled break; extracting work into a function can make an early return a clear way to leave nested loops.

Through C++23, a nonterminating loop without the required observable or progress operations can violate the forward-progress rules. C++26 makes a specific exception for trivial infinite loops, such as eligible empty constant-true loops. This is not a blanket permission for every computational loop that never terminates. See [P2809R3](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2809r3.html).

## Program termination and cleanup

Returning from main first performs ordinary cleanup of its local objects, then initiates program termination. Calling `std::exit` directly does not unwind the active call stack, so it skips those automatic local destructors.

| Mechanism | Active automatic locals | Static objects | Registered callbacks |
|---|---|---|---|
| Returning from main | Main's locals are destroyed normally. | Normal termination destroys initialized statics. | Normal termination runs atexit callbacks. |
| `std::exit(code)` | The call stack is not unwound. | Initialized statics are destroyed; current-thread thread-local cleanup also applies. | atexit callbacks run. |
| `std::quick_exit(code)` | The call stack is not unwound. | Static destructors are skipped. | at_quick_exit callbacks run. |
| `std::abort()` | The call stack is not unwound. | Static destructors are skipped. | Neither callback family is run. |
| `std::terminate()` | Do not rely on stack unwinding. | Cleanup depends on the handler; the default calls abort. | The default does not run either family. |

`std::atexit` registers a no-argument callback for normal termination. Callbacks run in reverse registration order, with specified ordering interactions involving static destruction. Exit also performs standard stream/file cleanup. Quick_exit uses its own callback list and is not a general guarantee of safe shutdown in a multithreaded program.

Abort requests abnormal termination; it takes no user-supplied exit code, but the host can still report a termination status or signal. A failed enabled assert commonly calls it. Terminate invokes the installed terminate handler, whose default behavior is abort.

Prefer normal scope exit when cleanup is required. Exceptions can unwind toward a handler, while termination paths offer different guarantees. An uncaught exception does not guarantee unwinding before terminate. Programs needing crash resilience must also tolerate termination that performs no application cleanup.

## Errors and pitfalls

Duplicate cases, invalid switch condition types, and jumps over disallowed initialization require diagnostics. Reading a bypassed uninitialized scalar is a separate runtime language violation. Missing breaks and unsigned-counter wrap can be logical errors even when the individual operations are defined. Check both the language contract and the intended control flow.

## Additional syntax examples

These are independent syntax sketches, including deliberately invalid examples marked `CE` (compile error). They are not one compilable program.

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
        return -x;  // This sketch requires x != INT_MIN to avoid signed overflow.
    return x;
}

// loops
while (true)                       // idiom for intentional infinite loop
{
    char c{};
    if (!(std::cin >> c) || c == 'n') break;
}

int selection{};                   // OUTSIDE the do-block — condition needs it
do
{
    if (!(std::cin >> selection)) break; // Handle failed input in the surrounding function.
}
while (selection < 1 || selection > 4);   // semicolon here

for (int x{ 0 }, y{ 9 }; x < 10; ++x, --y)   // multi-counter: comma in end-expression
    std::cout << x << ' ' << y << '\n';

// Requires exponent >= 0 and every intermediate product to fit int64_t.
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

## Interview Q&A

### When would you use a switch instead of if/else?

I use a switch when I am comparing one integral or enum value against several constants. It makes that structure clear and lets the compiler choose a dispatch strategy. For ranges or unrelated predicates, if/else fits better. A switch does not guarantee a jump table.

### Why can declaring a variable inside a case cause a compile error?

Cases share the switch's scope unless I add blocks. Another label could jump past the variable's initialization into its scope, which is forbidden for many initializations. Giving that case its own block prevents the jump from entering the variable's scope.

### What happens to continue in a for loop?

It skips the rest of the body, then executes the loop's iteration expression before checking the condition. In a while loop, an increment inside the skipped body would not run. That is one reason a for loop is convenient for counted iteration.

### How do you choose auto versus auto-reference in a range loop?

For an ordinary container, auto usually copies each element. A reference lets me work with the original, and a const reference avoids copying while preventing writes through it. I also consider proxy-reference behavior when writing generic range code.

### Is returning from main equivalent to calling exit immediately?

There is a crucial cleanup difference. Returning from main destroys its automatic locals before normal termination. Calling exit directly skips unwinding the active stack, so those local destructors do not run. Both then use normal-termination facilities for static objects and atexit callbacks.

### Is an empty infinite loop always undefined behavior?

That answer depends on the language version and exact loop. C++26 permits eligible trivial infinite loops, while other nonterminating loops still need to respect forward-progress rules. I would state the version rather than use an unconditional rule.

### Are temporary ranges always safe in range-based for?

No. I need to know what owns the range and how the reference is obtained. Direct member access can extend an owner's lifetime, and C++23 fixes additional temporary cases. A reference to an already destroyed function parameter still dangles. Naming the owner explicitly often makes the code easier to verify.

## Practice history

The entries below preserve the original practice record. Use the explanations above for the current rules and qualifications.

### Questions (getcracked) / Quiz log

_(none yet — learncpp 4.10 / 8.5 / 8.6 / 8.8-8.12 / 16.8 (range-for) read 01/09/2026)_
