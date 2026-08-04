# Daily LeetCode Log

The routine appends one row per check. **Target = 3 problems** on weekdays, **5/day** on weekends (raised from 2 on 2026-07-23 for the 8-week plan).
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
| 2026-07-23 | Thursday | 6 | Yes | 9 | 🔥 SIX (target 3, first day at new bar). Finished 1-D DP: Longest String Chain, Maximum Total Damage With Spell Casting. Opened 2-D DP/Stock: Best Time to Buy/Sell Stock, w/ Transaction Fee, Maximal Square, Max Length of Repeated Subarray. Streak → 9. |
| 2026-07-24 | Friday | 3 | Yes | 10 | 🎉 DOUBLE DIGITS — 2nd perfect week. Number of Dice Rolls With Target Sum (sliding-window DP optimization), Palindromic Substrings + Longest Palindromic Substring (expand-around-center). All 2-D DP/Stock, Med. Streak → 10. |
| 2026-07-25 | Saturday | 5 | Yes | 10 | WEEKEND (bonus, streak unchanged): Knight Probability (2-D DP) + cleared Intervals — Merge Intervals, Meeting Rooms II, Meeting Scheduler, Teemo Attacking. Hit 5 ✅. No HARDs this weekend (all Med/Easy) and no revision pass reported — both carry to Sunday. |
| 2026-07-26 | Sunday | 5 | Yes | 10 | WEEKEND (bonus): hit 5 ✅. 2 Heap/PQ hards (Find Median from Data Stream, Find Servers That Handled Most) + 3 Tries after a primer (Implement Trie, Search Suggestions System, Word Search II — the hard). Revision (Evaluate Division, Max Total Damage, Circular Subarray, Next Permutation) still pending. |
| 2026-07-27 | Monday | 3 | Yes | 11 | Math & Geometry opened: Pow(x, n) (binary exponentiation), Count Primes (Sieve of Eratosthenes), Happy Number (cycle detection). Revision planned later this week. Streak → 11. |
| 2026-07-28 | Tuesday | 3 | Yes | 12 | Math & Geometry string-arithmetic: Multiply Strings (grade-school mult, digits i+j), Add Strings (two-pointer + carry), Add Two Integers (trivial). Streak → 12. |
| 2026-07-29 | Wednesday | 3 | Yes | 13 | 💪 CLUTCH — pushed out a 3rd while tired to save the chain. Reverse Words in a String, Walking Robot Simulation (Math & Geo) + Missing Number (Bit Manip — XOR cancel / Gauss-sum). Chain held. Streak → 13. |
| 2026-07-30 | Thursday | — | — | — | Not reported (low-capacity day). |
| 2026-07-31 | Friday | — | — | — | Not reported. |
| 2026-08-01 | Saturday | 5 | Yes | 13 | WEEKEND (bonus): hit 5 ✅. 2 HARDs — Stream of Characters (reversed-word trie) + Minimum Time to Make Array Sum At Most x (exchange-argument knapsack); Longest Common Prefix (Tries section done); + Bit Manip easies Number of 1 Bits, Single Number. Sunday = pure revision day. |
| 2026-08-03 | Monday | 4 | Yes | — | Design (4): LRU Cache, Insert Delete GetRandom O(1), Design Circular Queue, Design Front Middle Back Queue (two-deque split + rebalance invariant). LeetCode recovered — got the 4th. Hit the 4/day target. Sunday revision still pending. |
