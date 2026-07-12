# problem-tracker

Accountability memory for my weekday LeetCode habit.

A scheduled Claude routine runs every weekday morning (9 AM PT). On each run it:

1. Checks how many problems I marked **Solved** on the previous weekday.
   Source of truth for *what* I solved: my LeetCode tracker Google Sheet.
2. Appends the outcome to [`log.md`](./log.md) — this repo is the routine's durable memory (streaks, misses).
3. Sends me a drill-sergeant notification: props if I hit 2+, a roast if I didn't.

`log.md` is maintained by the routine. Avoid hand-editing except to correct a mistake.
