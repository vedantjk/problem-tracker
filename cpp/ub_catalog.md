# UB Catalog & Behavior Taxonomy

## The taxonomy
| Category | Meaning | Example |
|---|---|---|
| Compile error | rule violation, diagnostic required | `int x = "hi";` |
| Ill-formed NDR | invalid program, no diagnostic owed | `int __x;`, mismatched inline defs across TUs |
| Implementation-defined | must pick & document | `sizeof(long)`, char signedness |
| Unspecified | one of several, needn't document | arg evaluation order, static-init order across TUs |
| UB | anything may happen | `INT_MAX+1`, dangling deref, OOB, data race |

- UB is a CONTRACT property, audited statically — "it ran fine" proves nothing; behavior changes with compiler/flags/inlining.
- The optimizer assumes UB never happens and deletes dependent branches (null check after a deref: gone).
- Why UB persists: optimizer latitude (signed overflow → loop vectorization) + hardware divergence (shift-count masking). Where hardware converged, definitions follow: C++20 two's complement; C++26 "erroneous behavior" for uninitialized reads.
- Tools: -fsanitize=undefined,address; -fsanitize=alignment; -Wall -Wextra; -Wstrict-aliasing=2 (UBSan does NOT catch aliasing; TySan new/slow). -fwrapv / -fno-strict-aliasing = opt-in dialects.

## Master UB list (→ home file)
- Uninitialized automatic scalar read → initialization_deduction
- Signed arithmetic overflow: INT_MAX+1, -INT_MIN, INT_MIN/-1 → types_conversions
- Shift count >= width or negative → types_conversions
- Float→integral out of range at runtime → floating_point
- Unsequenced modification (+read) of a scalar → expressions
- Off-the-end return, non-void function → functions_scope_lambdas
- Dangling: return ref to local; use-after-scope; by-ref capture outliving variable; const auto& through temporary's member → functions_scope_lambdas / initialization_deduction
- Strict-aliasing violation; misaligned deref; const-stripped write → bits_punning
- bitset operator[] out of range → bits_punning
- Bool holding a non-0/1 byte → types_conversions
- Out-of-range cast into unscoped enum w/o fixed underlying type → types_conversions
- Reserved identifiers (NDR) → build_linkage
- ODR rule-3 mismatch (NDR) → build_linkage
- Padding bytes via memcmp (unspecified, not UB) → memory_layout
- **Moved-from std-library objects: "valid but unspecified state"** (gc "Unspecified behavior", 02/09):
  - **Valid** = class invariants hold; every operation WITHOUT preconditions is safe: `.size()`, `.clear()`, `.empty()`, assignment, destruction. **Unspecified** = the value could be anything — empty, or even the ORIGINAL contents (a small string under SSO can't have its buffer stolen; the move degrades to a copy and may leave the source untouched).
  - Precondition-carrying ops are the danger: `front()`, `back()`, `v[0]`, `*it` on a moved-from container — if it happens to be empty, that's the usual UB, not something new.
  - "Unless otherwise specified" is load-bearing: `std::unique_ptr` is GUARANTEED null after move, `std::shared_ptr` guaranteed empty — smart pointers are specified, containers aren't.
  - Applies to *std* types by that clause; YOUR types' moved-from state is whatever your move ctor leaves — make it at least destructible + assignable (dtor always runs on the source).
  - Reuse is fine: `s = "new";` or `s.clear();` puts it back in a known state. And remember `std::move` moves nothing — it's a cast to rvalue-ref; the move happens in the receiving ctor/assignment.

## Questions (getcracked)
- [x] _global_variable — 29/08 — ok

## Traps / interview one-liners
- "UB isn't random — the optimizer deletes branches that could only run after UB."
- "Check the operation's contract before simulating the machine" (the Down-shift lesson).
- "Unspecified ≠ implementation-defined ≠ NDR ≠ UB — four different promises."
