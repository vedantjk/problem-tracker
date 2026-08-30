# C++ notes (getcracked Beginner C++ roadmap)

One file per roadmap node. Written **after** answering the node's questions, from memory.
Missed questions → Anki card (front = question, back = the one-line reason).

| Node | File | Q done | Missed | Core model written? | Cold-tested |
|---|---|---|---|---|---|
| Compiler basics + program structure | [compiler_and_program_structure.md](compiler_and_program_structure.md) | 0/0 | quiz 4/7 | yes | 29/08 |
| Variables, Objects, Initialization | [variables_objects_initialization.md](variables_objects_initialization.md) | 3/3 | 0 | yes | no |
| Undefined Behavior | [undefined_behavior.md](undefined_behavior.md) | 1/1 | 0 | yes | no |
| Declarations/Definitions/Multiple files | [declarations_definitions_multiple_files.md](declarations_definitions_multiple_files.md) | 0/0 | - | yes | no |
| Preprocessor + header guards | [preprocessor_header_guards.md](preprocessor_header_guards.md) | 1/1 | 0 | yes | no |
| Functions | [functions.md](functions.md) | 1/1 | 0 | yes | no |
| Scope | [scope.md](scope.md) | 1/1 | 0 | yes | no |
| Namespaces | [namespaces.md](namespaces.md) | 0/0 | - | yes | no |
| Lambdas | [lambdas.md](lambdas.md) | 3/3 | 0 | yes | no |
| Object Sizes | [object_sizes.md](object_sizes.md) | 0/? | ? | yes | no |
| Signed vs Unsigned | [signed_unsigned.md](signed_unsigned.md) | 0/? | ? | yes | no |
| Keywords and Identifiers | [keywords_identifiers.md](keywords_identifiers.md) | 0/0 | - | yes | no |

## Quizzes

| Date | Quiz | Score | Time | Percentile | Notes |
|---|---|---|---|---|---|
| 29/08/2026 | Beginner C++ (getcracked) | 11/20 | 18:11 | top 9.7% of 248 ("Cracked") | Baseline, cold. 2 coding questions skipped. Missed: full-specialization member def (no `template<>`), fold `sum(2,0.5,..)` is double (arith conversions per `+`), macro arg double-eval `121`, `delete` on `malloc` memory, `const alias` = top-level const (`int* const`), `class A; struct A{}` same entity. Priority nodes: Templates, Pointers/const, new/delete, Classes. Retake after tree is done. |

## Template

```
# <Node name>

## Core model
<5-15 lines, your words. If you can't write this from memory you haven't learned the node.>

## Questions
- [x] <question title> — DD/MM — ok
- [ ] <question title> — DD/MM — MISSED: <one-line reason>

## Traps / interview one-liners
- <thing you'd say out loud>
```
