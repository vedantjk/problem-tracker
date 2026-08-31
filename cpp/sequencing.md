# Sequencing / Evaluation Order

## Core model
- UB rule: two unsequenced modifications of the same scalar, or an unsequenced modification + read, in one expression → UB. `++x * x++` — both sides modify and read x, `*` sequences nothing → UB. Parentheses group, never sequence.
- Sequencing operators (left fully before right): `&&`, `||`, `,`, `?:`. So `++x && x++` and `(++x, x--)` are defined.
- C++17 additions: `<<`/`>>` sequence left-to-right (`cout << x++ << x++` = unspecified values, not UB); assignment evaluates RHS fully before LHS (`i = i++ + 1` defined); `[]`, `->*` sequenced; function arguments indeterminately sequenced (each completes before another starts, order unspecified — `f(i++, i++)` no longer UB, still unpredictable).
- Arithmetic (`*`, `+`, `-`, `/`) never sequences — the classic UB lives there.

## Questions (getcracked)
- [ ] One after the other — 30/08 — MISSED: `++x * x++` — didn't flag the unsequenced modification+read as UB.

## Traps / interview one-liners
- "Mental shortcut: same scalar modified twice (or modified+read) in one full expression with no sequencing operator between → UB."
- "C++17 defined evaluation order for <<, =, [], and made function args indeterminately sequenced — many old 'UB!' interview answers are now just 'unspecified order'. Know which standard the interviewer means."
- "Prefix ++ returns the lvalue (so ++++x and ++x = 5 compile); postfix returns an rvalue copy (x++++ is CE). Prefer ++it for class types — postfix constructs a real temporary; for ints the optimizer erases the difference."
- "Unspecified ≠ UB: `f(g(), h())` picks an order; `++x * x++` may do anything."
