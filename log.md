# Daily LeetCode Log

The routine appends one row per weekday check. **Target = 2 problems** solved on the prior weekday.
Streak = consecutive weekday checks where the target was met.

| Check date (PT) | Weekday checked | Solved that day | Hit target? | Streak | Notes |
|---|---|---|---|---|---|
| 2026-07-12 | (baseline) | — | — | 0 | Tracker initialized. Last logged problems in sheet: Combination Sum + Permutations on 2026-07-07. |
| 2026-07-12 | Sunday | ? | No | 0 | First real cron fire ✅ (scheduler works). Drive connector offline → degraded, no live sheet read. Last known solve 07/07; no evidence of activity since. |
| 2026-07-13 | Monday | 2 | Yes | 1 | Word Search + Letter Combinations of a Phone Number (both Med, Backtracking), solved 13/07. Grid DFS w/ visited-marking; per-digit choice enumeration. Streak on the board. |
| 2026-07-14 | Tuesday | 2 | Yes | 2 | Next Permutation (Med) + Number of Islands (Med), solved 14/07. NP: find pivot, swap with next-greater in suffix, reverse suffix; Islands: grid DFS + visited. Streak → 2. |
| 2026-07-15 | Wednesday | 2 | Yes | 3 | Course Schedule + Course Schedule II (both Med, Graphs), solved 15/07. Topological sort — Kahn's BFS (in-degrees) or DFS 3-color cycle detection. Streak → 3. |
| 2026-07-16 | Thursday | 2 | Yes | 4 | (backfilled — silent victory) Number of Provinces + Evaluate Division (both Med, Graphs), solved 16/07. Provinces: DFS + visited (disconnected graph); Evaluate Division: weighted DSU w/ path compression. Streak → 4. |
| 2026-07-17 | Friday | 2 | Yes | 5 | Game of Life + First Completely Painted Row or Column (both Med), solved 17/07. GoL: in-place with 2 transient states; FCP: value→coord hash + row/col freq counters. Streak → 5 — perfect week. |
| 2026-07-20 | Monday | 2 | Yes | 6 | Climbing Stairs (Easy) + Perfect Squares (Med), solved 20/07 — first 1-D DP. Stairs: Fibonacci recurrence, 2 rolling states; Perfect Squares: min-coins DP, or Lagrange 4-square math for O(√N). No weekend work (no penalty). Streak → 6. |
| 2026-07-21 | Tuesday | 2 | Yes | 7 | Maximum Subarray + Maximum Sum Circular Subarray (both Med, 1-D DP), solved 21/07. Kadane's rolling max; circular = max(Kadane, total − minKadane), guarding the all-negative case. Streak → 7. |
| 2026-07-22 | Wednesday | 2 | Yes | 8 | Maximum Subarray Sum with One Deletion + Paint House (both Med, 1-D DP), solved 22/07 — 50th solved overall 🎉. One-deletion: two rolling states (with/without a deletion); Paint House: 3 rolling colour costs. Streak → 8. |
