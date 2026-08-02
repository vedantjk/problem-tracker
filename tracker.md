# LeetCode / CSES Tracker — Snapshot

Snapshot of my practice sheet as of **2026-07-12**. Source of truth remains the Google Sheet; this file is a committed mirror.

**Progress:** 81 Solved · most recent: *Stream of Characters* + *Minimum Time to Make Array Sum At Most x* (both Hard) + *Longest Common Prefix* (01/08/2026).

| Category | Problem | Difficulty | Status | Date Done | Time (min) | Confidence | Notes |
| :-- | :-- | :-: | :-: | :-: | :-: | :-: | :-- |
| Arrays & Hashing | Two Sum | Easy | Solved | 18/06/2026 | 5 | 5 | Simple nested for loop, optimize by using a hashmap |
| Arrays & Hashing | Group Anagrams | Med | Solved | 18/06/2026 | 5 | 5 | Sort the string, store it as key and the value is the list of the strings with the same key |
| Arrays & Hashing | Find the Duplicate Number | Med | Solved | 18/06/2026 | 20 | 3 | Given constraints, only tortoise-and-hare solves it. Find collision point, then collide again at normal pace. Proof: slow walks F+a, fast walks F+a+kC. 2(F+a)=(F+a)+kC ⇒ F+a=kC ⇒ F=kC−a, i.e. k−1 full loops plus C−a steps from collision to entrance. |
| Arrays & Hashing | Count Common Words With One Occurrence | Easy | Solved | 18/06/2026 | 10 | 4 | Use 2 maps, or 1 map with a pair of ints. |
| Arrays & Hashing | Smallest Missing Non-negative Integer After Operations | Med | Solved | 18/06/2026 | 20 | 3 | Store a count of the mod values. Start mex from 0 and keep checking hash[mex % value] > 0; if not, decrement it and increment mex. |
| Arrays & Hashing | Intersection of Two Arrays | Easy | Solved | 22/06/2026 | 5 | 4 | Solved using 2 sets, can be done with a map. |
| Arrays & Hashing | Fizz Buzz | Easy | Solved | 22/06/2026 | 5 | 4 | It's Fizz Buzz. Besides if/else chains, can use a hashmap of mappings + string concatenation. |
| Two Pointers & Sliding Window | Max Consecutive Ones III | Med | Solved | 22/06/2026 | 10 | 4 | Classic sliding window; keep count of zeros in the window and advance left when it exceeds range. |
| Two Pointers & Sliding Window | Length of Longest Subarray With at Most K Frequency | Med | Solved | 22/06/2026 | 10 | 4 | Classic sliding window; track frequency of each element and keep it ≤ k by advancing left. |
| Two Pointers & Sliding Window | Sliding Window Maximum | Hard | Solved | 22/06/2026 | 20 | 3 | Use a deque whose front is the window max: pop front when it leaves the window, pop back to drop smaller elements. Linear alt: left/right block maxima in chunks of k; any window [i, i+k−1] straddles ≤1 boundary so answer = max(right[i], left[i+k−1]). |
| Two Pointers & Sliding Window | Pairs of Songs With Total Durations Divisible by 60 | Med | Solved | 22/06/2026 | 10 | 4 | Standard O(n²) that becomes O(n) with a map of frequencies as you walk the array. |
| Stack | Valid Parentheses | Easy | Solved | 22/06/2026 | 10 | 4 | Make sure to check edge cases. |
| Stack | Min Stack | Med | Solved | 22/06/2026 | 10 | 4 | Stack of pair — hold the min value and the regular value. |
| Stack | Evaluate Reverse Polish Notation | Med | Solved | 22/06/2026 | 10 | 4 | Store digits in stack, pop and operate. Be careful about b/a vs a/b. |
| Stack | Number of Orders in the Backlog | Med | Solved | 22/06/2026 | 20 | 4 | Mainly 2 priority queues (pq is max-heap by default); rest is mechanical. Check pops and pushes carefully. |
| Stack | Basic Calculator | Hard | Solved | 22/06/2026 | 30 | 3 | Stack + recursion. Recursive fn has an int stack; sum it at the end and return. Track previous operator: + pushes num, − pushes −num, * and / pop and combine (higher priority). On '(' recurse (returns an int into the current stack). |
| Stack | Basic Calculator II | Med | Solved | 22/06/2026 | 30 | 3 | No parens; just the while loop, a stack, build cur_num, track prev_op. For * and /, pop prev_num, operate, push result. |
| Stack | Basic Calculator III | Hard | Solved | 22/06/2026 | 30 | 3 | Basic Calculator 1 + Basic Calculator 2. |
| Stack | Basic Calculator IV | Hard | Solved | 22/06/2026 | 60 | 2 | Very involved: BC3 minus division, plus polynomials instead of ints. Map for keywords; Poly = struct{ map<multiset<string>, long long> } (variable names → coefficients). Helpers: make_poly, add, subtract, multiply, negate, prune (drop zero-coefficient terms before printing). Main recurse returns Poly; track var, value, prev_op, cur Poly, stack of Poly. |
| Binary Search | Find First and Last Position of Element in Sorted Array | Med | Solved | 23/06/2026 | 10 | 3 | lower_bound = first ≥ target, upper_bound = first > target. Check lower_bound; if end or ≠ target return {−1,−1}, else upper_bound−1. equal_range returns both at once. Manual: standard binary search with a first/last flag (first ⇒ right=mid−1, else left=mid+1). |
| Binary Search | Sqrt(x) | Easy | Solved | 23/06/2026 | 10 | 3 | Standard binary search low ≤ high, high=mid−1, low=mid+1. Return high (smallest number whose square ≤ x). At loop end high = low − 1. |
| Binary Search | Koko Eating Bananas | Med | Solved | 23/06/2026 | 5 | 4 | Binary search on a predicate: does this eating rate meet the target? |
| Binary Search | Minimum Time to Make Array Sum At Most x | Hard | Solved | 01/08/2026 | 60 | 2 | Each index is worth zeroing at most once → answer ≤ n or −1. Savings from zeroing i as the j-th op = a_i + j·b_i (the t term cancels, so ONE DP serves all t). Exchange argument: sort by nums2 (b) ascending so larger-b elements get later slots (less regrowth). Knapsack: dp[i][j] = max(dp[i−1][j], dp[i−1][j−1] + a_i + j·b_i). Answer = first t in 0..n with Σa + t·Σb − dp[n][t] ≤ x, else −1 (FIRST hit, not argmin — the sum isn't monotonic in t). O(n²) time, O(n) space iterating j downward. |
| Binary Search | Minimum Operations to Make Numbers Non-positive | Hard | Solved | 23/06/2026 | 30 | 2 | Check if `mid` operations make all ≤ 0. mid ops = mid y-ops + mid x-ops; since y<x, subtract mid*y from every element, remainders must sum to ≤ mid x-ops. Ceil division trick: (r+d−1)/d instead of r/d + (r%d?1:0). |
| Binary Search | Random Pick with Weight | Med | Solved | 23/06/2026 | 15 | 3 | Prefix sums + rand(). Random float = (float)rand()/RAND_MAX; target = rand*total_weight; lower_bound for the answer. |
| Linked List | Add Two Numbers | Med | Solved | 24/06/2026 | 5 | 4 | Linked list with a while loop. |
| Linked List | Merge k Sorted Lists | Hard | Solved | 25/06/2026 | 10 | 3 | Have a queue and merge 2 at a time; check for empty lists. |
| Trees | Binary Tree Maximum Path Sum | Hard | Solved | 29/06/2026 | 10 | 3 | Helper returns max path picking itself + one child. Answer computed each recursion as root->val + left + right; clamp children to 0. |
| Trees | Serialize and Deserialize Binary Tree | Hard | Todo | | | | |
| Trees | Validate Binary Search Tree | Med | Solved | 04/07/2026 | 15 | 4 | Instead of sentinel values, pass TreeNodes and check. Do inorder (more logical, no time savings). |
| Trees | Binary Tree Zigzag Level Order Traversal | Med | Solved | 04/07/2026 | 10 | 4 | Standard BFS with a flag you flip each level. |
| Trees | Subtree of Another Tree | Easy | Solved | 04/07/2026 | 15 | 4 | Check if a node equals the sub-root, then match trees. Better: serialize + KMP/Rabin-Karp string matching. |
| Trees | House Robber III | Med | Solved | 04/07/2026 | 30 | 3 | Linear recurrence / BFS don't work. At each node return max(rob, skip). robThis = node->val + rSkip + lSkip; skip = sum of max(skip, rob) of each child. |
| Tries | Implement Trie (Prefix Tree) | Med | Solved | 26/07/2026 | 10 | 3 | TrieNode = children pointers + isEnd flag. insert walks/creates nodes down the word, sets isEnd at the end. walk() returns the node where a string ends or null. search = walk && isEnd; startsWith = walk != null. |
| Tries | Search Suggestions System | Med | Solved | 26/07/2026 | 30 | 2 | Trie way: build, walk to the prefix node, DFS to collect ≤3 lexicographically smallest completions. Binary-search way: sort, lower_bound the prefix, take ≤3 if they match. Optimal no-compare: two pointers lo/hi into the sorted array — for the i-th prefix char, advance lo while lo[i]≠char and retract hi similarly; the window shrinks as the prefix grows, no repeated string comparisons. |
| Tries | Word Search II | Hard | Solved | 26/07/2026 | 30 | 2 | Put all words in a trie, then a single grid DFS walking the trie in lockstep — if the current node has no child for the cell's letter, prune and return. Clear a word from its node once found (avoid duplicates). Optimization: after exploring a cell, delete now-empty trie leaves so future branches prune even faster. |
| Tries | Stream of Characters | Hard | Solved | 01/08/2026 | 60 | 2 | Forward matching fails; store the dictionary words REVERSED in the trie and match the stream backward. Keep a history deque of the last L chars (L = longest word); on each query, walk the reversed trie over recent chars — an isEnd hit = a word matched. (Flat-map trie: vector of arrays, node index stored in the cell, parallel isEnd bool vector.) |
| Tries | Longest Common Prefix | Easy | Solved | 01/08/2026 | 20 | 4 | Vertical scan: check each char position across all words, stop when a word ends or chars differ. Trie version: insert all, count how many times each next letter is added; while that count == n, extend the common prefix by one. |
| Heap / Priority Queue | Find Median from Data Stream | Hard | Solved | 26/07/2026 | 15 | 4 | Two heaps: max-heap for the lower half, min-heap for the upper half. Rebalance so their sizes differ by ≤1. Median = top of the larger heap, or the average of both tops when equal. Handle empty/edge cases in the balance step. |
| Heap / Priority Queue | Find Servers That Handled Most Number of Requests | Hard | Solved | 26/07/2026 | 25 | 3 | Min-heap of (freeTime, serverId) for busy servers + an ordered set of free server ids. Per request: pop the heap to free servers with end ≤ arrival (move them into the set). Wrap-around assignment: lower_bound(i%k) in the free set, else begin(); if the set is empty, drop the request. Track per-server counts, return the max. |
| Heap / Priority Queue | Reorganize String | Med | Solved | 06/07/2026 | | | |
| Backtracking | Combination Sum | Med | Solved | 07/07/2026 | | | |
| Backtracking | Permutations | Med | Solved | 07/07/2026 | | | |
| Backtracking | Word Search | Med | Solved | 13/07/2026 | 15 | 3 | Iterate over all cells; from each, DFS in 4 directions. Mark the current cell visited (or overwrite it) before recursing or you get an infinite loop. |
| Backtracking | Letter Combinations of a Phone Number | Med | Solved | 13/07/2026 | 15 | 2 | Keep a vector<string> mapping digit→chars. For each digit, loop over its chars enumerating all combos; pass down a string capturing the choice so far. |
| Backtracking | Sudoku Solver | Hard | Todo | | | | |
| Backtracking | Permutation Sequence | Hard | Todo | | | | |
| Backtracking | Next Permutation | Med | Solved | 14/07/2026 | 20 | 2 | Find largest k with arr[k] < arr[k+1] (suffix after k is non-increasing); if none, array is the last permutation — reverse and return. In the suffix find the greatest l with arr[l] > arr[k] (smallest suffix value still > arr[k]), swap k and l, then reverse arr[k+1..end] to make it ascending → next permutation. |
| Graphs | Number of Islands | Med | Solved | 14/07/2026 | 10 | 4 | DFS from each unvisited land cell, flooding its component. Use a visited array, or modify the input in place — depends whether mutating input is allowed. |
| Graphs | Course Schedule | Med | Solved | 15/07/2026 | 15 | 3 | Topological sort. BFS (Kahn): compute in-degrees, queue all 0-in-degree nodes, pop and decrement neighbors; if every node gets processed (valid ordering) → true. DFS: cycle detection with 3 colors (white=unprocessed, gray=processing, black=done); a gray hit = cycle → false. Loop DFS over ALL nodes (graph may be disconnected); push a node once fully processed — topo order comes out reversed. |
| Graphs | Course Schedule II | Med | Solved | 15/07/2026 | 15 | 3 | Slight modification of Course Schedule — return the actual topological ordering (empty array if a cycle exists). |
| Graphs | Number of Provinces | Med | Solved | 16/07/2026 | 15 | 3 | DFS with a visited array to avoid infinite loops; start from every unvisited node since the graph may be disconnected — each DFS launch = one province. |
| Graphs | Word Ladder | Hard | Todo | | | | |
| Graphs | Word Ladder II | Hard | Todo | | | | |
| Graphs | Reconstruct Itinerary | Hard | Todo | | | | |
| Graphs | Evaluate Division | Med | Solved | 16/07/2026 | 30 | 2 | Brute force: build a weighted graph and BFS each query. Optimal: weighted Union-Find storing the ratio to each node's parent — needs path compression to be near-O(1); without it, it degrades to plain graph traversal. |
| Graphs | Couples Holding Hands | Hard | Todo | | | | |
| Graphs | Sort Items by Groups Respecting Dependencies | Hard | Todo | | | | |
| Graphs | Parallel Courses III | Hard | Todo | | | | |
| Graphs | Game of Life | Med | Solved | 17/07/2026 | 15 | 3 | Trivial except the in-place follow-up: use 2 transient states (2 = live→dead, 3 = dead→live) so one pass can read the original and encode the next; count both 1 and 2 as currently-live neighbors, then map 2→0, 3→1. |
| Graphs | First Completely Painted Row or Column | Med | Solved | 17/07/2026 | 20 | 3 | Works because m*n ≤ 1e5 and values are unique: build a value→(row,col) hash for O(1) lookup, keep per-row and per-col fill counters; when a row's count == #cols (or a col's count == #rows) that line is complete — return that step. |
| Graphs | Optimal Account Balancing | Hard | Todo | | | | |
| 1-D DP | Climbing Stairs | Easy | Solved | 20/07/2026 | 5 | 4 | Simplest DP. Recurrence cur = pprev + prev (Fibonacci); keep only the last 2 states → O(1) space. |
| 1-D DP | Perfect Squares | Med | Solved | 20/07/2026 | 15 | 3 | 1-D DP but not a plain loop: for each i, try every perfect square s ≤ i, dp[i] = min(dp[i-s]+1); return dp[n]. Optimal is math via Lagrange's four-square theorem (answer ∈ 1..4): ans=1 if N is a perfect square; ans=4 if N = 4^a(8b+7); ans=2 if some i has N−i² a perfect square; else 3 — O(√N) time, O(1) space. |
| 1-D DP | Maximum Subarray | Med | Solved | 21/07/2026 | 5 | 3 | Kadane's algorithm. Two vars: rolling cur = max(nums[i], cur + nums[i]); ans = max(ans, cur). O(n) time, O(1) space. |
| 1-D DP | Maximum Sum Circular Subarray | Med | Solved | 21/07/2026 | 15 | 2 | Two cases: non-wrapping = normal Kadane; wrapping = totalSum − minSubarraySum. Answer = max(maxKadane, total − minKadane). Guard the all-negative case: if maxKadane < 0, return maxKadane (the wrap formula would give an empty subarray). |
| 1-D DP | Maximum Subarray Sum with One Deletion | Med | Solved | 22/07/2026 | 10 | 3 | Extend Kadane to two rolling states: curNoDel = max(nums[i], curNoDel + nums[i]) (standard); curWithDel = max(curNoDel [delete current], curWithDel + nums[i] [keep current]). ans = max over both. Init both to arr[0], loop from index 1. |
| 1-D DP | Paint House | Med | Solved | 22/07/2026 | 5 | 3 | 3 rolling vars, one per colour: cur[c] = costs[i][c] + min(prev two other colours). Each var = min cost if house i is painted colour c; answer = min of the three at the end. |
| 1-D DP | Longest String Chain | Med | Solved | 23/07/2026 | 15 | 3 | Sort words by length; for each word, delete each letter and check if that predecessor exists, dp[word] = max(dp[pred] + 1). Use a hash-map dp table (word→best) so the "does predecessor exist" lookup is O(1). |
| 1-D DP | Maximum Total Damage With Spell Casting | Med | Solved | 23/07/2026 | 25 | 2 | Trick: reshape so the DP only looks backward. Freq-count + extract unique powers, sort. Take/skip DP over unique values: take = val*freq[val] + dp[j] where j is the last index with unique[j] ≤ val−3 (find via upper_bound(val−3)−1, or a monotone two-pointer since sorted); skip = dp[i−1]. dp[i] = max(take, skip); watch out-of-bounds. |
| 1-D DP | Minimum Costs Using the Train Line | Hard | Todo | | | | |
| 2-D DP / Stock | Best Time to Buy and Sell Stock | Easy | Solved | 23/07/2026 | 5 | 4 | Two vars: minBuy = min(minBuy, prices[i]); profit = max(profit, prices[i] − minBuy). |
| 2-D DP / Stock | Best Time to Buy and Sell Stock III | Hard | Todo | | | | |
| 2-D DP / Stock | Best Time to Buy and Sell Stock IV | Hard | Todo | | | | |
| 2-D DP / Stock | Best Time to Buy and Sell Stock with Transaction Fee | Med | Solved | 23/07/2026 | 10 | 3 | State machine, bottom-up: hold = max(hold, free − prices[i]); free = max(free, hold + prices[i] − fee); init hold = −prices[0], free = 0, loop from 1, return free. (Fun fact: top-down with a max({...}) initializer-list TLE'd — LeetCode's AddressSanitizer redzones/poisons the materialized stack array every call; bottom-up sidesteps it.) |
| 2-D DP / Stock | Maximal Square | Med | Solved | 23/07/2026 | 10 | 3 | dp[i][j] = side of the largest all-1 square with (i,j) as bottom-right. If grid[i][j]==1, dp[i][j] = min(dp[i−1][j], dp[i][j−1], dp[i−1][j−1]) + 1. Track the max side; answer = side². |
| 2-D DP / Stock | Maximum Length of Repeated Subarray | Med | Solved | 23/07/2026 | 15 | 3 | Longest common sub-ARRAY (contiguous). dp[i][j] = length of common run ending exactly at nums1[i], nums2[j]; if equal dp[i][j] = dp[i−1][j−1] + 1, else 0. Track the global max. A padded matrix removes any special init beyond 0. |
| 2-D DP / Stock | Number of Dice Rolls With Target Sum | Med | Solved | 24/07/2026 | 20 | 3 | Count ways for n dice to sum to target. DP over (die index, sum): dp[i][j] = Σ_{m=1..k} dp[i−1][j−m] (guard j−m ≥ 0), mod. Choices are (die, target) not k → O(n·k·target). Optimization: cur[j] = prev[j−1]+…+prev[j−k] is a sliding-window sum over prev, so keep a running window (add prev[j−1], drop prev[j−k−1]) → O(n·target). |
| 2-D DP / Stock | Palindromic Substrings | Med | Solved | 24/07/2026 | 20 | 3 | Expand-around-center: for each index expand outward while chars match, counting palindromes. Run two centers per index — odd (i, i) and even (i, i+1). O(n²). |
| 2-D DP / Stock | Longest Palindromic Substring | Med | Solved | 24/07/2026 | 5 | 3 | Same expand-around-center as Palindromic Substrings; instead of counting, track start + len of the longest palindrome seen so you can slice it out at the end. |
| 2-D DP / Stock | Count Palindromic Subsequences | Hard | Todo | | | | |
| 2-D DP / Stock | Wildcard Matching | Hard | Todo | | | | |
| 2-D DP / Stock | Knight Probability in Chessboard | Med | Solved | 25/07/2026 | 15 | 3 | dp[cell] = probability of being on that cell after m moves. Two rolling n×n arrays; start cell init 1, rest 0. Each move: new[cell] = Σ over the 8 knight-source cells of prev[source]/8 (in-bounds only). Answer = sum of all probabilities after k moves (prob still on board). |
| Intervals | Merge Intervals | Med | Solved | 25/07/2026 | 10 | 3 | Sort by start. Track current [a,b]; for each interval, if its start ≤ b merge (b = max(b, end)), else push [a,b] and start a new one. Push the final [a,b] after the loop. |
| Intervals | Meeting Rooms II | Med | Solved | 25/07/2026 | 15 | 3 | Sort by start. Min-heap of end times (C++ default is max-heap → use greater). For each meeting, pop tops whose end ≤ its start (rooms freed), then push its end. Answer = max heap size ever reached = rooms needed. |
| Intervals | Employee Free Time | Hard | Todo | | | | |
| Intervals | Meeting Scheduler | Med | Solved | 25/07/2026 | 15 | 3 | Sort both lists; two pointers. start = max(the two starts), end = min(the two ends); if end − start ≥ duration return [start, start+duration]. Advance whichever interval has the smaller end (it can't overlap anything further). |
| Intervals | Teemo Attacking | Easy | Solved | 25/07/2026 | 5 | 3 | Sum over i ≥ 1 of min(duration, t[i] − t[i−1]), then add one full duration for the last attack. |
| Math & Geometry | Pow(x, n) | Med | Solved | 27/07/2026 | 15 | 3 | Binary exponentiation (fast pow). While n > 0: if n even → x *= x, n /= 2; if odd → ans *= x, n -= 1. Handle negative n (invert x to 1/x; cast n to long long first to avoid INT_MIN overflow on negation). |
| Math & Geometry | Count Primes | Med | Solved | 27/07/2026 | 20 | 3 | Sieve of Eratosthenes. bool array all-true; mark 0 and 1 false; for each prime p from 2, mark p², p²+p, p²+2p, … up to n as non-prime. O(n log log n). |
| Math & Geometry | Max Points on a Line | Hard | Todo | | | | |
| Math & Geometry | Best Position for a Service Centre | Hard | Todo | | | | |
| Math & Geometry | Happy Number | Easy | Solved | 27/07/2026 | 20 | 3 | Simulate sum-of-squares-of-digits repeatedly; detect a cycle (hash set of seen values, or Floyd's tortoise/hare). Reaching 1 = happy, a cycle = not. |
| Math & Geometry | Multiply Strings | Med | Solved | 28/07/2026 | 20 | 3 | Grade-school multiplication: each digit pair prod of a[i]*b[j] lands at result index i+j (carry to i+j−1... i.e. propagate). Helper for string addition. Karatsuba is the faster divide-and-conquer alternative (not done yet). |
| Math & Geometry | Add Strings | Easy | Solved | 28/07/2026 | 1 | 3 | Two pointers from the back, add digit by digit with carry; don't forget the final carry. |
| Math & Geometry | Add Two Integers | Easy | Solved | 28/07/2026 | 0 | 4 | Return a + b. No bignum, no trick — just the sum. |
| Math & Geometry | Reverse Words in a String | Med | Solved | 29/07/2026 | 10 | 3 | Split on spaces into a vector of words, reverse the order, join with single spaces (handle multiple/leading/trailing spaces). In-place O(1)-space alt: reverse the whole string, then reverse each word. |
| Math & Geometry | Walking Robot Simulation | Med | Solved | 29/07/2026 | 10 | 3 | Direction index into a [N,E,S,W] delta vector; turn right = (d+1)&3, left = (d+3)&3 (or ((d±1)%4+4)%4). Step while the next cell isn't an obstacle (store obstacles in a hash set of coords), track max distance². For unordered_set of coordinate pairs you need a custom hash. |
| Math & Geometry | Rank Transform of a Matrix | Hard | Todo | | | | |
| Math & Geometry | Transform to Chessboard | Hard | Todo | | | | |
| Bit Manipulation | Count Number of Maximum Bitwise-OR Subsets | Med | Todo | | | | |
| Bit Manipulation | Largest Combination With Bitwise AND Greater Than Zero | Med | Todo | | | | |
| Bit Manipulation | Power of Four | Easy | Todo | | | | |
| Bit Manipulation | Single Number | Easy | Todo | | | | |
| Bit Manipulation | Single Number II | Med | Todo | | | | |
| Bit Manipulation | Single Number III | Med | Todo | | | | |
| Bit Manipulation | Number of 1 Bits | Easy | Todo | | | | |
| Bit Manipulation | Counting Bits | Easy | Todo | | | | |
| Bit Manipulation | Reverse Bits | Easy | Todo | | | | |
| Bit Manipulation | Missing Number | Easy | Solved | 29/07/2026 | 5 | 3 | XOR all indices 0..n with all elements — equal values cancel (a^a=0), leaving the missing number. Alt: Gauss sum n(n+1)/2 minus the array sum. |
| Bit Manipulation | Bitwise AND of Numbers Range | Med | Todo | | | | |
| Bit Manipulation | Sum of Two Integers | Med | Todo | | | | |
| Design | LRU Cache | Med | Todo | | | | |
| Design | LFU Cache | Hard | Todo | | | | |
| Design | Insert Delete GetRandom O(1) | Med | Todo | | | | |
| Design | Design Circular Queue | Med | Todo | | | | |
| Design | Design Front Middle Back Queue | Med | Todo | | | | |
| Design | Moving Average from Data Stream | Easy | Todo | | | | |
| Design | Time Based Key-Value Store | Med | Todo | | | | |
| Design | Design A Leaderboard | Med | Todo | | | | |
| Design | Design Tic-Tac-Toe | Med | Todo | | | | |
| Design | Design Memory Allocator | Med | Todo | | | | |
| Design | Design Excel Sum Formula | Hard | Todo | | | | |
| Design | Design Spreadsheet | Med | Todo | | | | |
| Design | Design In-Memory File System | Hard | Todo | | | | |
| Design | Design a Text Editor | Hard | Todo | | | | |
| Design | Design Search Autocomplete System | Hard | Todo | | | | |
| Design | Design Skiplist | Hard | Todo | | | | |
| Design | Design HashSet | Easy | Todo | | | | |
| Design | Design HashMap | Easy | Todo | | | | |
| Design | Design Twitter | Med | Todo | | | | |
| CSES: Introductory | Weird Algorithm | Easy | Todo | | | | |
| CSES: Introductory | Missing Number | Easy | Todo | | | | |
| CSES: Introductory | Repetitions | Easy | Todo | | | | |
| CSES: Introductory | Increasing Array | Easy | Todo | | | | |
| CSES: Introductory | Permutations | Easy | Todo | | | | |
| CSES: Introductory | Number Spiral | Med | Todo | | | | |
| CSES: Introductory | Two Knights | Med | Todo | | | | |
| CSES: Introductory | Two Sets | Med | Todo | | | | |
| CSES: Introductory | Bit Strings | Easy | Todo | | | | |
| CSES: Introductory | Trailing Zeros | Easy | Todo | | | | |
| CSES: Introductory | Coin Piles | Easy | Todo | | | | |
| CSES: Introductory | Palindrome Reorder | Easy | Todo | | | | |
| CSES: Introductory | Gray Code | Med | Todo | | | | |
| CSES: Introductory | Tower of Hanoi | Med | Todo | | | | |
| CSES: Introductory | Creating Strings | Med | Todo | | | | |
| CSES: Introductory | Apple Division | Med | Todo | | | | |
| CSES: Introductory | Chessboard and Queens | Med | Todo | | | | |
| CSES: Introductory | Grid Paths | Hard | Todo | | | | |
| CSES: Sorting & Searching | Distinct Numbers | Easy | Todo | | | | |
| CSES: Sorting & Searching | Apartments | Easy | Todo | | | | |
| CSES: Sorting & Searching | Ferris Wheel | Easy | Todo | | | | |
| CSES: Sorting & Searching | Concert Tickets | Med | Todo | | | | |
| CSES: Sorting & Searching | Restaurant Customers | Easy | Todo | | | | |
| CSES: Sorting & Searching | Movie Festival | Easy | Todo | | | | |
| CSES: Sorting & Searching | Sum of Two Values | Easy | Todo | | | | |
| CSES: Sorting & Searching | Maximum Subarray Sum | Easy | Todo | | | | |
| CSES: Sorting & Searching | Stick Lengths | Med | Todo | | | | |
| CSES: Sorting & Searching | Missing Coin Sum | Med | Todo | | | | |
| CSES: Sorting & Searching | Collecting Numbers | Med | Todo | | | | |
| CSES: Sorting & Searching | Collecting Numbers II | Med | Todo | | | | |
| CSES: Sorting & Searching | Playlist | Med | Todo | | | | |
| CSES: Sorting & Searching | Towers | Med | Todo | | | | |
| CSES: Sorting & Searching | Traffic Lights | Med | Todo | | | | |
| CSES: Sorting & Searching | Josephus Problem I | Med | Todo | | | | |
| CSES: Sorting & Searching | Josephus Problem II | Med | Todo | | | | |
| CSES: Sorting & Searching | Nested Ranges Check | Med | Todo | | | | |
| CSES: Sorting & Searching | Nested Ranges Count | Med | Todo | | | | |
| CSES: Sorting & Searching | Room Allocation | Med | Todo | | | | |
| CSES: Sorting & Searching | Factory Machines | Med | Todo | | | | |
| CSES: Sorting & Searching | Tasks and Deadlines | Easy | Todo | | | | |
| CSES: Sorting & Searching | Reading Books | Med | Todo | | | | |
| CSES: Sorting & Searching | Sum of Three Values | Med | Todo | | | | |
| CSES: Sorting & Searching | Sum of Four Values | Med | Todo | | | | |
| CSES: Sorting & Searching | Nearest Smaller Values | Med | Todo | | | | |
| CSES: Sorting & Searching | Subarray Sums I | Easy | Todo | | | | |
| CSES: Sorting & Searching | Subarray Sums II | Med | Todo | | | | |
| CSES: Sorting & Searching | Subarray Divisibility | Med | Todo | | | | |
| CSES: Sorting & Searching | Distinct Values Subarrays | Med | Todo | | | | |
| CSES: Sorting & Searching | Array Division | Med | Todo | | | | |
| CSES: Sorting & Searching | Sliding Median | Med | Todo | | | | |
| CSES: Sorting & Searching | Sliding Cost | Med | Todo | | | | |
| CSES: Sorting & Searching | Movie Festival II | Med | Todo | | | | |
| CSES: Sorting & Searching | Maximum Subarray Sum II | Med | Todo | | | | |
| CSES: Dynamic Programming | Dice Combinations | Easy | Todo | | | | |
| CSES: Dynamic Programming | Minimizing Coins | Easy | Todo | | | | |
| CSES: Dynamic Programming | Coin Combinations I | Med | Todo | | | | |
| CSES: Dynamic Programming | Coin Combinations II | Med | Todo | | | | |
| CSES: Dynamic Programming | Removing Digits | Easy | Todo | | | | |
| CSES: Dynamic Programming | Grid Paths (DP) | Med | Todo | | | | |
| CSES: Dynamic Programming | Book Shop | Med | Todo | | | | |
| CSES: Dynamic Programming | Array Description | Med | Todo | | | | |
| CSES: Dynamic Programming | Counting Towers | Hard | Todo | | | | |
| CSES: Dynamic Programming | Edit Distance | Med | Todo | | | | |
| CSES: Dynamic Programming | Rectangle Cutting | Med | Todo | | | | |
| CSES: Dynamic Programming | Money Sums | Med | Todo | | | | |
| CSES: Dynamic Programming | Removal Game | Med | Todo | | | | |
| CSES: Dynamic Programming | Two Sets II | Med | Todo | | | | |
| CSES: Dynamic Programming | Increasing Subsequence | Med | Todo | | | | |
| CSES: Dynamic Programming | Projects | Hard | Todo | | | | |
| CSES: Dynamic Programming | Elevator Rides | Hard | Todo | | | | |
| CSES: Dynamic Programming | Counting Tilings | Hard | Todo | | | | |
| CSES: Dynamic Programming | Counting Numbers | Hard | Todo | | | | |
| CSES: Graph | Counting Rooms | Easy | Todo | | | | |
| CSES: Graph | Labyrinth | Med | Todo | | | | |
| CSES: Graph | Building Roads | Easy | Todo | | | | |
| CSES: Graph | Message Route | Med | Todo | | | | |
| CSES: Graph | Building Teams | Med | Todo | | | | |
| CSES: Graph | Round Trip | Med | Todo | | | | |
| CSES: Graph | Monsters | Med | Todo | | | | |
| CSES: Graph | Shortest Routes I | Med | Todo | | | | |
| CSES: Graph | Shortest Routes II | Med | Todo | | | | |
| CSES: Graph | High Score | Med | Todo | | | | |
| CSES: Graph | Flight Discount | Med | Todo | | | | |
| CSES: Graph | Cycle Finding | Med | Todo | | | | |
| CSES: Graph | Flight Routes | Med | Todo | | | | |
| CSES: Graph | Round Trip II | Med | Todo | | | | |
| CSES: Graph | Course Schedule (Topo) | Med | Todo | | | | |
| CSES: Graph | Longest Flight Route | Med | Todo | | | | |
| CSES: Graph | Game Routes | Med | Todo | | | | |
| CSES: Graph | Investigation | Med | Todo | | | | |
