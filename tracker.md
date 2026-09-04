# LeetCode / CSES Tracker — Snapshot

**This file is the source of truth** (the Google Sheet was retired 2026-08-26). Rows tagged `NC250` in Notes were merged from the NeetCode 250 list on 2026-08-26 (193 problems not already present; 57 overlapped). Nothing was removed.

**Progress:** 116 Solved · most recent: *Car Fleet* (03/09/2026). W2 LC: 6/18.

| Category | Problem | Difficulty | Status | Date Done | Time (min) | Confidence | Notes |
| :-- | :-- | :-: | :-: | :-: | :-: | :-: | :-- |
| Arrays & Hashing | Two Sum | Easy | Solved | 18/06/2026 | 5 | 5 | Simple nested for loop, optimize by using a hashmap |
| Arrays & Hashing | Group Anagrams | Med | Solved | 18/06/2026 | 5 | 5 | Sort the string, store it as key and the value is the list of the strings with the same key |
| Arrays & Hashing | Find the Duplicate Number | Med | Solved | 18/06/2026 | 20 | 3 | Given constraints, only tortoise-and-hare solves it. Find collision point, then collide again at normal pace. Proof: slow walks F+a, fast walks F+a+kC. 2(F+a)=(F+a)+kC ⇒ F+a=kC ⇒ F=kC−a, i.e. k−1 full loops plus C−a steps from collision to entrance. |
| Arrays & Hashing | Count Common Words With One Occurrence | Easy | Solved | 18/06/2026 | 10 | 4 | Use 2 maps, or 1 map with a pair of ints. |
| Arrays & Hashing | Smallest Missing Non-negative Integer After Operations | Med | Solved | 18/06/2026 | 20 | 3 | Store a count of the mod values. Start mex from 0 and keep checking hash[mex % value] > 0; if not, decrement it and increment mex. |
| Arrays & Hashing | Intersection of Two Arrays | Easy | Solved | 22/06/2026 | 5 | 4 | Solved using 2 sets, can be done with a map. |
| Arrays & Hashing | Fizz Buzz | Easy | Solved | 22/06/2026 | 5 | 4 | It's Fizz Buzz. Besides if/else chains, can use a hashmap of mappings + string concatenation. |
| Arrays & Hashing | Concatenation of Array | Easy | Todo | | | | NC250 |
| Arrays & Hashing | Contains Duplicate | Easy | Solved | 27/08/2026 | 3 | 5 | NC250. Hash set: O(n) time/space, early return on first hit. Alt: sort + adjacent compare, O(n log n) time, O(1) extra. |
| Arrays & Hashing | Valid Anagram | Easy | Solved | 27/08/2026 | 3 | 5 | NC250. 26-count array compare. Better: length check, single std::array<int,26>, ++ for s / -- for t with early exit on negative; take const string&. Alt: sort both. Unicode follow-up → unordered_map. |
| Arrays & Hashing | Remove Element | Easy | Todo | | | | NC250 |
| Arrays & Hashing | Majority Element | Easy | Todo | | | | NC250 |
| Arrays & Hashing | Sort an Array | Med | Todo | | | | NC250 |
| Arrays & Hashing | Sort Colors | Med | Todo | | | | NC250 |
| Arrays & Hashing | Top K Frequent Elements | Med | Solved | 28/08/2026 | 15 | 4 | NC250. Heap of all m distinct: O(m log m). Min-heap size k: O(m log k). Bucket sort by count (size n+1), walk from n down: O(n), the intended one. nth_element also O(m) avg. |
| Arrays & Hashing | Encode and Decode Strings | Med | Todo | | | | NC250 |
| Arrays & Hashing | Range Sum Query 2D Immutable | Med | Todo | | | | NC250 |
| Arrays & Hashing | Product of Array Except Self | Med | Solved | 31/08/2026 | 15 | 3 | NC250. Prefix pass into ans, then suffix as a running scalar multiplied in reverse — O(1) extra. Original used int suffix[n] (VLA — not legal C++, gcc extension); rewrote without it. |
| Arrays & Hashing | Valid Sudoku | Med | Todo | | | | NC250 |
| Arrays & Hashing | Longest Consecutive Sequence | Med | Solved | 28/08/2026 | 10 | 4 | NC250. Set; only start a run when x-1 absent. MUST iterate the set not nums, else duplicates re-walk runs → O(n²). Guard INT_MAX+1 overflow. Alt sort+scan O(n log n). |
| Arrays & Hashing | Best Time to Buy And Sell Stock II | Med | Todo | | | | NC250 |
| Arrays & Hashing | Majority Element II | Med | Todo | | | | NC250 |
| Arrays & Hashing | Subarray Sum Equals K | Med | Todo | | | | NC250 |
| Arrays & Hashing | First Missing Positive | Hard | Todo | | | | NC250 |
| Two Pointers & Sliding Window | Max Consecutive Ones III | Med | Solved | 22/06/2026 | 10 | 4 | Classic sliding window; keep count of zeros in the window and advance left when it exceeds range. |
| Two Pointers & Sliding Window | Length of Longest Subarray With at Most K Frequency | Med | Solved | 22/06/2026 | 10 | 4 | Classic sliding window; track frequency of each element and keep it ≤ k by advancing left. |
| Two Pointers & Sliding Window | Sliding Window Maximum | Hard | Solved | 22/06/2026 | 20 | 3 | Use a deque whose front is the window max: pop front when it leaves the window, pop back to drop smaller elements. Linear alt: left/right block maxima in chunks of k; any window [i, i+k−1] straddles ≤1 boundary so answer = max(right[i], left[i+k−1]). |
| Two Pointers & Sliding Window | Pairs of Songs With Total Durations Divisible by 60 | Med | Solved | 22/06/2026 | 10 | 4 | Standard O(n²) that becomes O(n) with a map of frequencies as you walk the array. |
| Two Pointers & Sliding Window | Reverse String | Easy | Todo | | | | NC250 |
| Two Pointers & Sliding Window | Valid Palindrome | Easy | Solved | 28/08/2026 | 5 | 5 | NC250. Cleaned string + two pointers. Follow-up O(1) space: two pointers skipping non-alnum inline. Cast to unsigned char before isalnum/tolower (signed char UB). |
| Two Pointers & Sliding Window | Valid Palindrome II | Easy | Todo | | | | NC250 |
| Two Pointers & Sliding Window | Merge Strings Alternately | Easy | Todo | | | | NC250 |
| Two Pointers & Sliding Window | Merge Sorted Array | Easy | Todo | | | | NC250 |
| Two Pointers & Sliding Window | Remove Duplicates From Sorted Array | Easy | Todo | | | | NC250 |
| Two Pointers & Sliding Window | Two Sum II Input Array Is Sorted | Med | Solved | 03/09/2026 | 5 | 4 | NC250, W2. Two-pointer on sorted: sum>target shrink right, else grow left — each step eliminates one index. static_cast<int> on size() makes empty-input right=-1 safe. Mention int-overflow-proof compare (target - numbers[right]) in interviews. O(n)/O(1). |
| Two Pointers & Sliding Window | 3Sum | Med | Solved | 28/08/2026 | 15 | 4 | NC250. Sort, fix i, two-pointer inside; skip dup i. Only ONE of the x/y dup-skip loops is required for correctness (the other is an optimization), but zero is wrong. Use i+2<n not i<size()-2 (unsigned underflow). O(n²). |
| Two Pointers & Sliding Window | 4Sum | Med | Todo | | | | NC250 |
| Two Pointers & Sliding Window | Rotate Array | Med | Todo | | | | NC250 |
| Two Pointers & Sliding Window | Container With Most Water | Med | Solved | 28/08/2026 | 5 | 4 | NC250. Two pointers, move the shorter side. Proof: moving the taller side shrinks width and can't raise the min, so no candidate is lost. Max area 1e9 fits int. |
| Two Pointers & Sliding Window | Boats to Save People | Med | Todo | | | | NC250 |
| Two Pointers & Sliding Window | Trapping Rain Water | Hard | Solved | 03/09/2026 | 15 | 4 | NC250, W2. Solved with prefix/suffix max arrays (O(n) space) — finds it intuitive. O(1) two-pointer: settle the side with SMALLER known max (`lmax <= rmax` comparison) — min() only needs its smaller arg exact, unexplored middle only raises the losing side. Prefer that form over height[l]<height[r] (needs an inductive proof). |
| Two Pointers & Sliding Window | Contains Duplicate II | Easy | Todo | | | | NC250 |
| Two Pointers & Sliding Window | Longest Substring Without Repeating Characters | Med | Solved | 28/08/2026 | 10 | 4 | NC250. Sliding window with set (shrink left until no dup). Better: array<int,256> last-seen index, left = max(left, last[c]+1); the >= left guard stops stale occurrences moving left backwards. |
| Two Pointers & Sliding Window | Longest Repeating Character Replacement | Med | Solved | 03/09/2026 | 20 | 3 | NC250, W2. Window valid iff len - max_freq <= k. KEY: stale max_freq (never recomputed on shrink) is still correct — ans only improves on a new TRUE max, when window is valid; stale-max windows can't exceed a previously recorded valid one. Verbalize this proof. array<int,26> > unordered_map. O(n)/O(1). |
| Two Pointers & Sliding Window | Permutation In String | Med | Solved | 03/09/2026 | 20 | 3 | NC250, W2. Fixed window = s1.len, elementwise 26-count compare each slide → O(26n). Upgrade: `matches` counter updated for only the 2 letters that change per slide → O(n). array<int,26> over vector. Watch -Wsign-compare on len vs size(). |
| Two Pointers & Sliding Window | Minimum Size Subarray Sum | Med | Solved | 03/09/2026 | 10 | 4 | NC250, W2. Shrink-while-valid window; legal ONLY because all-positive makes sum monotone both ways. Follow-up: O(n log n) via increasing prefix sums + binary search. Negatives would need prefix + deque. |
| Two Pointers & Sliding Window | Find K Closest Elements | Med | Todo | | | | NC250 |
| Two Pointers & Sliding Window | Minimum Window Substring | Hard | Todo | | | | NC250 |
| Stack | Valid Parentheses | Easy | Solved | 22/06/2026 | 10 | 4 | Make sure to check edge cases. |
| Stack | Min Stack | Med | Solved | 22/06/2026 | 10 | 4 | Stack of pair — hold the min value and the regular value. |
| Stack | Evaluate Reverse Polish Notation | Med | Solved | 22/06/2026 | 10 | 4 | Store digits in stack, pop and operate. Be careful about b/a vs a/b. |
| Stack | Number of Orders in the Backlog | Med | Solved | 22/06/2026 | 20 | 4 | Mainly 2 priority queues (pq is max-heap by default); rest is mechanical. Check pops and pushes carefully. |
| Stack | Basic Calculator | Hard | Solved | 22/06/2026 | 30 | 3 | Stack + recursion. Recursive fn has an int stack; sum it at the end and return. Track previous operator: + pushes num, − pushes −num, * and / pop and combine (higher priority). On '(' recurse (returns an int into the current stack). |
| Stack | Basic Calculator II | Med | Solved | 22/06/2026 | 30 | 3 | No parens; just the while loop, a stack, build cur_num, track prev_op. For * and /, pop prev_num, operate, push result. |
| Stack | Basic Calculator III | Hard | Solved | 22/06/2026 | 30 | 3 | Basic Calculator 1 + Basic Calculator 2. |
| Stack | Basic Calculator IV | Hard | Solved | 22/06/2026 | 60 | 2 | Very involved: BC3 minus division, plus polynomials instead of ints. Map for keywords; Poly = struct{ map<multiset<string>, long long> } (variable names → coefficients). Helpers: make_poly, add, subtract, multiply, negate, prune (drop zero-coefficient terms before printing). Main recurse returns Poly; track var, value, prev_op, cur Poly, stack of Poly. |
| Stack | Baseball Game | Easy | Todo | | | | NC250 |
| Stack | Implement Stack Using Queues | Easy | Todo | | | | NC250 |
| Stack | Implement Queue using Stacks | Easy | Todo | | | | NC250 |
| Stack | Asteroid Collision | Med | Todo | | | | NC250 |
| Stack | Daily Temperatures | Med | Solved | 31/08/2026 | 10 | 4 | NC250. Monotonic decreasing stack of indices; pop while warmer, answer = i - popped. Each index pushed/popped once → O(n) amortized. |
| Stack | Online Stock Span | Med | Todo | | | | NC250 |
| Stack | Car Fleet | Med | Solved | 03/09/2026 | 20 | 3 | NC250, W2. Sort by position, reverse sweep on arrival time; strictly-slower-behind starts new fleet, ties merge. It's a monotonic stack keeping only the top. Float-free compare: cross-multiply (target-pi)*sj vs (target-pj)*si in long long. O(n log n). |
| Stack | Simplify Path | Med | Todo | | | | NC250 |
| Stack | Decode String | Med | Todo | | | | NC250 |
| Stack | Maximum Frequency Stack | Hard | Todo | | | | NC250 |
| Stack | Largest Rectangle In Histogram | Hard | Todo | | | | NC250 |
| Binary Search | Find First and Last Position of Element in Sorted Array | Med | Solved | 23/06/2026 | 10 | 3 | lower_bound = first ≥ target, upper_bound = first > target. Check lower_bound; if end or ≠ target return {−1,−1}, else upper_bound−1. equal_range returns both at once. Manual: standard binary search with a first/last flag (first ⇒ right=mid−1, else left=mid+1). |
| Binary Search | Sqrt(x) | Easy | Solved | 23/06/2026 | 10 | 3 | Standard binary search low ≤ high, high=mid−1, low=mid+1. Return high (smallest number whose square ≤ x). At loop end high = low − 1. |
| Binary Search | Koko Eating Bananas | Med | Solved | 23/06/2026 | 5 | 4 | Binary search on a predicate: does this eating rate meet the target? |
| Binary Search | Minimum Time to Make Array Sum At Most x | Hard | Solved | 01/08/2026 | 60 | 2 | Each index is worth zeroing at most once → answer ≤ n or −1. Savings from zeroing i as the j-th op = a_i + j·b_i (the t term cancels, so ONE DP serves all t). Exchange argument: sort by nums2 (b) ascending so larger-b elements get later slots (less regrowth). Knapsack: dp[i][j] = max(dp[i−1][j], dp[i−1][j−1] + a_i + j·b_i). Answer = first t in 0..n with Σa + t·Σb − dp[n][t] ≤ x, else −1 (FIRST hit, not argmin — the sum isn't monotonic in t). O(n²) time, O(n) space iterating j downward. |
| Binary Search | Minimum Operations to Make Numbers Non-positive | Hard | Solved | 23/06/2026 | 30 | 2 | Check if `mid` operations make all ≤ 0. mid ops = mid y-ops + mid x-ops; since y<x, subtract mid*y from every element, remainders must sum to ≤ mid x-ops. Ceil division trick: (r+d−1)/d instead of r/d + (r%d?1:0). |
| Binary Search | Random Pick with Weight | Med | Solved | 23/06/2026 | 15 | 3 | Prefix sums + rand(). Random float = (float)rand()/RAND_MAX; target = rand*total_weight; lower_bound for the answer. |
| Binary Search | Binary Search | Easy | Todo | | | | NC250 |
| Binary Search | Search Insert Position | Easy | Todo | | | | NC250 |
| Binary Search | Guess Number Higher Or Lower | Easy | Todo | | | | NC250 |
| Binary Search | Search a 2D Matrix | Med | Todo | | | | NC250 |
| Binary Search | Capacity to Ship Packages Within D Days | Med | Todo | | | | NC250 |
| Binary Search | Find Minimum In Rotated Sorted Array | Med | Todo | | | | NC250 |
| Binary Search | Search In Rotated Sorted Array | Med | Solved | 31/08/2026 | 20 | 3 | NC250. Binary search: one half is always sorted — check nums[l]<=nums[m] to find it, then range-test target against the sorted half to pick a side. Kept l+(r-l)/2 discussion (constraints make l+r safe here). |
| Binary Search | Search In Rotated Sorted Array II | Med | Todo | | | | NC250 |
| Binary Search | Split Array Largest Sum | Hard | Todo | | | | NC250 |
| Binary Search | Median of Two Sorted Arrays | Hard | Todo | | | | NC250 |
| Binary Search | Find in Mountain Array | Hard | Todo | | | | NC250 |
| Linked List | Add Two Numbers | Med | Solved | 24/06/2026 | 5 | 4 | Linked list with a while loop. |
| Linked List | Merge k Sorted Lists | Hard | Solved | 25/06/2026 | 10 | 3 | Have a queue and merge 2 at a time; check for empty lists. |
| Linked List | Reverse Linked List | Easy | Solved | 31/08/2026 | 5 | 4 | NC250. prev/curr/next pointer walk. Lesson: ListNode* temp in the loop is a stack POINTER, not an allocation — no leak (pointers vs pointees). std::exchange one-liner variant exists. |
| Linked List | Merge Two Sorted Lists | Easy | Todo | | | | NC250 |
| Linked List | Linked List Cycle | Easy | Solved | 28/08/2026 | 3 | 5 | NC250. Floyd slow/fast. Fast gains 1 per step inside the cycle so it can't skip slow. Cycle-start proof already in Find the Duplicate Number. |
| Linked List | Reorder List | Med | Todo | | | | NC250 |
| Linked List | Remove Nth Node From End of List | Med | Todo | | | | NC250 |
| Linked List | Copy List With Random Pointer | Med | Todo | | | | NC250 |
| Linked List | Reverse Linked List II | Med | Todo | | | | NC250 |
| Linked List | Reverse Nodes In K Group | Hard | Todo | | | | NC250 |
| Trees | Binary Tree Maximum Path Sum | Hard | Solved | 29/06/2026 | 10 | 3 | Helper returns max path picking itself + one child. Answer computed each recursion as root->val + left + right; clamp children to 0. |
| Trees | Serialize and Deserialize Binary Tree | Hard | Todo | | | | |
| Trees | Validate Binary Search Tree | Med | Solved | 04/07/2026 | 15 | 4 | Instead of sentinel values, pass TreeNodes and check. Do inorder (more logical, no time savings). |
| Trees | Binary Tree Zigzag Level Order Traversal | Med | Solved | 04/07/2026 | 10 | 4 | Standard BFS with a flag you flip each level. |
| Trees | Subtree of Another Tree | Easy | Solved | 04/07/2026 | 15 | 4 | Check if a node equals the sub-root, then match trees. Better: serialize + KMP/Rabin-Karp string matching. |
| Trees | House Robber III | Med | Solved | 04/07/2026 | 30 | 3 | Linear recurrence / BFS don't work. At each node return max(rob, skip). robThis = node->val + rSkip + lSkip; skip = sum of max(skip, rob) of each child. |
| Trees | Binary Tree Inorder Traversal | Easy | Todo | | | | NC250 |
| Trees | Binary Tree Preorder Traversal | Easy | Todo | | | | NC250 |
| Trees | Binary Tree Postorder Traversal | Easy | Todo | | | | NC250 |
| Trees | Invert Binary Tree | Easy | Todo | | | | NC250 |
| Trees | Maximum Depth of Binary Tree | Easy | Todo | | | | NC250 |
| Trees | Diameter of Binary Tree | Easy | Todo | | | | NC250 |
| Trees | Balanced Binary Tree | Easy | Todo | | | | NC250 |
| Trees | Same Tree | Easy | Todo | | | | NC250 |
| Trees | Lowest Common Ancestor of a Binary Search Tree | Med | Todo | | | | NC250 |
| Trees | Insert into a Binary Search Tree | Med | Todo | | | | NC250 |
| Trees | Delete Node in a BST | Med | Todo | | | | NC250 |
| Trees | Binary Tree Level Order Traversal | Med | Todo | | | | NC250 |
| Trees | Binary Tree Right Side View | Med | Todo | | | | NC250 |
| Trees | Construct Quad Tree | Med | Todo | | | | NC250 |
| Trees | Count Good Nodes In Binary Tree | Med | Todo | | | | NC250 |
| Trees | Kth Smallest Element In a Bst | Med | Todo | | | | NC250 |
| Trees | Construct Binary Tree From Preorder And Inorder Traversal | Med | Todo | | | | NC250 |
| Trees | Delete Leaves With a Given Value | Med | Todo | | | | NC250 |
| Tries | Implement Trie (Prefix Tree) | Med | Solved | 26/07/2026 | 10 | 3 | TrieNode = children pointers + isEnd flag. insert walks/creates nodes down the word, sets isEnd at the end. walk() returns the node where a string ends or null. search = walk && isEnd; startsWith = walk != null. |
| Tries | Search Suggestions System | Med | Solved | 26/07/2026 | 30 | 2 | Trie way: build, walk to the prefix node, DFS to collect ≤3 lexicographically smallest completions. Binary-search way: sort, lower_bound the prefix, take ≤3 if they match. Optimal no-compare: two pointers lo/hi into the sorted array — for the i-th prefix char, advance lo while lo[i]≠char and retract hi similarly; the window shrinks as the prefix grows, no repeated string comparisons. |
| Tries | Word Search II | Hard | Solved | 26/07/2026 | 30 | 2 | Put all words in a trie, then a single grid DFS walking the trie in lockstep — if the current node has no child for the cell's letter, prune and return. Clear a word from its node once found (avoid duplicates). Optimization: after exploring a cell, delete now-empty trie leaves so future branches prune even faster. |
| Tries | Stream of Characters | Hard | Solved | 01/08/2026 | 60 | 2 | Forward matching fails; store the dictionary words REVERSED in the trie and match the stream backward. Keep a history deque of the last L chars (L = longest word); on each query, walk the reversed trie over recent chars — an isEnd hit = a word matched. (Flat-map trie: vector of arrays, node index stored in the cell, parallel isEnd bool vector.) |
| Tries | Longest Common Prefix | Easy | Solved | 01/08/2026 | 20 | 4 | Vertical scan: check each char position across all words, stop when a word ends or chars differ. Trie version: insert all, count how many times each next letter is added; while that count == n, extend the common prefix by one. |
| Tries | Design Add And Search Words Data Structure | Med | Todo | | | | NC250 |
| Tries | Extra Characters in a String | Med | Todo | | | | NC250 |
| Heap / Priority Queue | Find Median from Data Stream | Hard | Solved | 26/07/2026 | 15 | 4 | Two heaps: max-heap for the lower half, min-heap for the upper half. Rebalance so their sizes differ by ≤1. Median = top of the larger heap, or the average of both tops when equal. Handle empty/edge cases in the balance step. |
| Heap / Priority Queue | Find Servers That Handled Most Number of Requests | Hard | Solved | 26/07/2026 | 25 | 3 | Min-heap of (freeTime, serverId) for busy servers + an ordered set of free server ids. Per request: pop the heap to free servers with end ≤ arrival (move them into the set). Wrap-around assignment: lower_bound(i%k) in the free set, else begin(); if the set is empty, drop the request. Track per-server counts, return the max. |
| Heap / Priority Queue | Reorganize String | Med | Solved | 06/07/2026 | | | |
| Heap / Priority Queue | Kth Largest Element In a Stream | Easy | Todo | | | | NC250 |
| Heap / Priority Queue | Last Stone Weight | Easy | Todo | | | | NC250 |
| Heap / Priority Queue | K Closest Points to Origin | Med | Todo | | | | NC250 |
| Heap / Priority Queue | Kth Largest Element In An Array | Med | Solved | 28/08/2026 | 15 | 3 | NC250. Min-heap size k O(n log k) (use greater<int>, not negation: -INT_MIN UB). Real answer: quickselect / nth_element O(n) avg; random pivot + 3-way partition to avoid O(n²) on sorted/duplicate input. nth_element = introselect. Write quickselect by hand. |
| Heap / Priority Queue | Task Scheduler | Med | Todo | | | | NC250 |
| Heap / Priority Queue | Single Threaded CPU | Med | Todo | | | | NC250 |
| Heap / Priority Queue | Longest Happy String | Med | Todo | | | | NC250 |
| Heap / Priority Queue | Car Pooling | Med | Todo | | | | NC250 |
| Heap / Priority Queue | IPO | Hard | Todo | | | | NC250 |
| Backtracking | Combination Sum | Med | Solved | 07/07/2026 | | | |
| Backtracking | Permutations | Med | Solved | 07/07/2026 | | | |
| Backtracking | Word Search | Med | Solved | 13/07/2026 | 15 | 3 | Iterate over all cells; from each, DFS in 4 directions. Mark the current cell visited (or overwrite it) before recursing or you get an infinite loop. |
| Backtracking | Letter Combinations of a Phone Number | Med | Solved | 13/07/2026 | 15 | 2 | Keep a vector<string> mapping digit→chars. For each digit, loop over its chars enumerating all combos; pass down a string capturing the choice so far. |
| Backtracking | Sudoku Solver | Hard | Solved | 18/08/2026 | 30 | 3 | Linear pos 0..80 → i=pos/9, j=pos%9; return true at pos==81. Three [9][10] bool arrays: row, col, box (box=(i/3)*3 + j/3). Preprocess existing digits once. Recurse: if cell filled → backtrack(pos+1); else try 1-9, if unused in row/col/box, mark + place, recurse and RETURN TRUE if it succeeds (propagate up, else you undo a valid solution); on failure unmark and reset to '.'. |
| Backtracking | Permutation Sequence | Hard | Todo | | | | |
| Backtracking | Next Permutation | Med | Solved | 14/07/2026 | 20 | 2 | Find largest k with arr[k] < arr[k+1] (suffix after k is non-increasing); if none, array is the last permutation — reverse and return. In the suffix find the greatest l with arr[l] > arr[k] (smallest suffix value still > arr[k]), swap k and l, then reverse arr[k+1..end] to make it ascending → next permutation. |
| Backtracking | Sum of All Subsets XOR Total | Easy | Todo | | | | NC250 |
| Backtracking | Subsets | Med | Todo | | | | NC250 |
| Backtracking | Combination Sum II | Med | Todo | | | | NC250 |
| Backtracking | Combinations | Med | Todo | | | | NC250 |
| Backtracking | Subsets II | Med | Todo | | | | NC250 |
| Backtracking | Permutations II | Med | Todo | | | | NC250 |
| Backtracking | Generate Parentheses | Med | Todo | | | | NC250 |
| Backtracking | Palindrome Partitioning | Med | Todo | | | | NC250 |
| Backtracking | Matchsticks to Square | Med | Todo | | | | NC250 |
| Backtracking | Partition to K Equal Sum Subsets | Med | Todo | | | | NC250 |
| Backtracking | N Queens | Hard | Todo | | | | NC250 |
| Backtracking | N Queens II | Hard | Todo | | | | NC250 |
| Backtracking | Word Break II | Hard | Todo | | | | NC250 |
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
| Graphs | Island Perimeter | Easy | Todo | | | | NC250 |
| Graphs | Verifying An Alien Dictionary | Easy | Todo | | | | NC250 |
| Graphs | Find the Town Judge | Easy | Todo | | | | NC250 |
| Graphs | Max Area of Island | Med | Todo | | | | NC250 |
| Graphs | Clone Graph | Med | Todo | | | | NC250 |
| Graphs | Walls And Gates | Med | Todo | | | | NC250 |
| Graphs | Rotting Oranges | Med | Todo | | | | NC250 |
| Graphs | Pacific Atlantic Water Flow | Med | Todo | | | | NC250 |
| Graphs | Surrounded Regions | Med | Todo | | | | NC250 |
| Graphs | Open The Lock | Med | Todo | | | | NC250 |
| Graphs | Graph Valid Tree | Med | Todo | | | | NC250 |
| Graphs | Course Schedule IV | Med | Todo | | | | NC250 |
| Graphs | Number of Connected Components In An Undirected Graph | Med | Todo | | | | NC250 |
| Graphs | Redundant Connection | Med | Todo | | | | NC250 |
| Graphs | Accounts Merge | Med | Todo | | | | NC250 |
| Graphs | Minimum Height Trees | Med | Todo | | | | NC250 |
| Graphs | Path with Minimum Effort | Med | Todo | | | | NC250 |
| Graphs | Network Delay Time | Med | Todo | | | | NC250 |
| Graphs | Min Cost to Connect All Points | Med | Todo | | | | NC250 |
| Graphs | Swim In Rising Water | Hard | Todo | | | | NC250 |
| Graphs | Alien Dictionary | Hard | Todo | | | | NC250 |
| Graphs | Cheapest Flights Within K Stops | Med | Todo | | | | NC250 |
| Graphs | Find Critical and Pseudo Critical Edges in Minimum Spanning Tree | Hard | Todo | | | | NC250 |
| Graphs | Build a Matrix With Conditions | Hard | Todo | | | | NC250 |
| Graphs | Greatest Common Divisor Traversal | Hard | Todo | | | | NC250 |
| 1-D DP | Climbing Stairs | Easy | Solved | 20/07/2026 | 5 | 4 | Simplest DP. Recurrence cur = pprev + prev (Fibonacci); keep only the last 2 states → O(1) space. |
| 1-D DP | Perfect Squares | Med | Solved | 20/07/2026 | 15 | 3 | 1-D DP but not a plain loop: for each i, try every perfect square s ≤ i, dp[i] = min(dp[i-s]+1); return dp[n]. Optimal is math via Lagrange's four-square theorem (answer ∈ 1..4): ans=1 if N is a perfect square; ans=4 if N = 4^a(8b+7); ans=2 if some i has N−i² a perfect square; else 3 — O(√N) time, O(1) space. |
| 1-D DP | Maximum Subarray | Med | Solved | 21/07/2026 | 5 | 3 | Kadane's algorithm. Two vars: rolling cur = max(nums[i], cur + nums[i]); ans = max(ans, cur). O(n) time, O(1) space. |
| 1-D DP | Maximum Sum Circular Subarray | Med | Solved | 21/07/2026 | 15 | 2 | Two cases: non-wrapping = normal Kadane; wrapping = totalSum − minSubarraySum. Answer = max(maxKadane, total − minKadane). Guard the all-negative case: if maxKadane < 0, return maxKadane (the wrap formula would give an empty subarray). |
| 1-D DP | Maximum Subarray Sum with One Deletion | Med | Solved | 22/07/2026 | 10 | 3 | Extend Kadane to two rolling states: curNoDel = max(nums[i], curNoDel + nums[i]) (standard); curWithDel = max(curNoDel [delete current], curWithDel + nums[i] [keep current]). ans = max over both. Init both to arr[0], loop from index 1. |
| 1-D DP | Paint House | Med | Solved | 22/07/2026 | 5 | 3 | 3 rolling vars, one per colour: cur[c] = costs[i][c] + min(prev two other colours). Each var = min cost if house i is painted colour c; answer = min of the three at the end. |
| 1-D DP | Longest String Chain | Med | Solved | 23/07/2026 | 15 | 3 | Sort words by length; for each word, delete each letter and check if that predecessor exists, dp[word] = max(dp[pred] + 1). Use a hash-map dp table (word→best) so the "does predecessor exist" lookup is O(1). |
| 1-D DP | Maximum Total Damage With Spell Casting | Med | Solved | 23/07/2026 | 25 | 2 | Trick: reshape so the DP only looks backward. Freq-count + extract unique powers, sort. Take/skip DP over unique values: take = val*freq[val] + dp[j] where j is the last index with unique[j] ≤ val−3 (find via upper_bound(val−3)−1, or a monotone two-pointer since sorted); skip = dp[i−1]. dp[i] = max(take, skip); watch out-of-bounds. |
| 1-D DP | Minimum Costs Using the Train Line | Hard | Todo | | | | |
| 1-D DP | Min Cost Climbing Stairs | Easy | Todo | | | | NC250 |
| 1-D DP | N-th Tribonacci Number | Easy | Todo | | | | NC250 |
| 1-D DP | House Robber | Med | Todo | | | | NC250 |
| 1-D DP | House Robber II | Med | Todo | | | | NC250 |
| 1-D DP | Decode Ways | Med | Todo | | | | NC250 |
| 1-D DP | Coin Change | Med | Todo | | | | NC250 |
| 1-D DP | Maximum Product Subarray | Med | Todo | | | | NC250 |
| 1-D DP | Word Break | Med | Todo | | | | NC250 |
| 1-D DP | Longest Increasing Subsequence | Med | Todo | | | | NC250 |
| 1-D DP | Partition Equal Subset Sum | Med | Todo | | | | NC250 |
| 1-D DP | Combination Sum IV | Med | Todo | | | | NC250 |
| 1-D DP | Integer Break | Med | Todo | | | | NC250 |
| 1-D DP | Stone Game III | Hard | Todo | | | | NC250 |
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
| Greedy | Lemonade Change | Easy | Todo | | | | NC250 |
| Greedy | Longest Turbulent Subarray | Med | Todo | | | | NC250 |
| Greedy | Jump Game | Med | Todo | | | | NC250 |
| Greedy | Jump Game II | Med | Todo | | | | NC250 |
| Greedy | Jump Game VII | Med | Todo | | | | NC250 |
| Greedy | Gas Station | Med | Todo | | | | NC250 |
| Greedy | Hand of Straights | Med | Todo | | | | NC250 |
| Greedy | Dota2 Senate | Med | Todo | | | | NC250 |
| Greedy | Merge Triplets to Form Target Triplet | Med | Todo | | | | NC250 |
| Greedy | Partition Labels | Med | Todo | | | | NC250 |
| Greedy | Valid Parenthesis String | Med | Todo | | | | NC250 |
| Greedy | Candy | Hard | Todo | | | | NC250 |
| 2-D DP / Stock | Unique Paths | Med | Todo | | | | NC250 |
| 2-D DP / Stock | Unique Paths II | Med | Todo | | | | NC250 |
| 2-D DP / Stock | Minimum Path Sum | Med | Todo | | | | NC250 |
| 2-D DP / Stock | Longest Common Subsequence | Med | Todo | | | | NC250 |
| 2-D DP / Stock | Last Stone Weight II | Med | Todo | | | | NC250 |
| 2-D DP / Stock | Best Time to Buy And Sell Stock With Cooldown | Med | Todo | | | | NC250 |
| 2-D DP / Stock | Coin Change II | Med | Todo | | | | NC250 |
| 2-D DP / Stock | Target Sum | Med | Todo | | | | NC250 |
| 2-D DP / Stock | Interleaving String | Med | Todo | | | | NC250 |
| 2-D DP / Stock | Stone Game | Med | Todo | | | | NC250 |
| 2-D DP / Stock | Stone Game II | Med | Todo | | | | NC250 |
| 2-D DP / Stock | Longest Increasing Path In a Matrix | Hard | Todo | | | | NC250 |
| 2-D DP / Stock | Distinct Subsequences | Hard | Todo | | | | NC250 |
| 2-D DP / Stock | Edit Distance | Med | Todo | | | | NC250 |
| 2-D DP / Stock | Burst Balloons | Hard | Todo | | | | NC250 |
| 2-D DP / Stock | Regular Expression Matching | Hard | Todo | | | | NC250 |
| Intervals | Merge Intervals | Med | Solved | 25/07/2026 | 10 | 3 | Sort by start. Track current [a,b]; for each interval, if its start ≤ b merge (b = max(b, end)), else push [a,b] and start a new one. Push the final [a,b] after the loop. |
| Intervals | Meeting Rooms II | Med | Solved | 25/07/2026 | 15 | 3 | Sort by start. Min-heap of end times (C++ default is max-heap → use greater). For each meeting, pop tops whose end ≤ its start (rooms freed), then push its end. Answer = max heap size ever reached = rooms needed. |
| Intervals | Employee Free Time | Hard | Todo | | | | |
| Intervals | Meeting Scheduler | Med | Solved | 25/07/2026 | 15 | 3 | Sort both lists; two pointers. start = max(the two starts), end = min(the two ends); if end − start ≥ duration return [start, start+duration]. Advance whichever interval has the smaller end (it can't overlap anything further). |
| Intervals | Teemo Attacking | Easy | Solved | 25/07/2026 | 5 | 3 | Sum over i ≥ 1 of min(duration, t[i] − t[i−1]), then add one full duration for the last attack. |
| Intervals | Insert Interval | Med | Todo | | | | NC250 |
| Intervals | Non Overlapping Intervals | Med | Todo | | | | NC250 |
| Intervals | Meeting Rooms | Easy | Todo | | | | NC250 |
| Intervals | Meeting Rooms III | Hard | Todo | | | | NC250 |
| Intervals | Minimum Interval to Include Each Query | Hard | Todo | | | | NC250 |
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
| Math & Geometry | Excel Sheet Column Title | Easy | Todo | | | | NC250 |
| Math & Geometry | Greatest Common Divisor of Strings | Easy | Todo | | | | NC250 |
| Math & Geometry | Insert Greatest Common Divisors in Linked List | Med | Todo | | | | NC250 |
| Math & Geometry | Transpose Matrix | Easy | Todo | | | | NC250 |
| Math & Geometry | Rotate Image | Med | Todo | | | | NC250 |
| Math & Geometry | Spiral Matrix | Med | Todo | | | | NC250 |
| Math & Geometry | Set Matrix Zeroes | Med | Todo | | | | NC250 |
| Math & Geometry | Plus One | Easy | Todo | | | | NC250 |
| Math & Geometry | Roman to Integer | Easy | Todo | | | | NC250 |
| Math & Geometry | Detect Squares | Med | Todo | | | | NC250 |
| Bit Manipulation | Count Number of Maximum Bitwise-OR Subsets | Med | Todo | | | | |
| Bit Manipulation | Largest Combination With Bitwise AND Greater Than Zero | Med | Todo | | | | |
| Bit Manipulation | Power of Four | Easy | Todo | | | | |
| Bit Manipulation | Single Number | Easy | Solved | 01/08/2026 | 5 | 4 | XOR all elements — equal values cancel (a^a=0), leaving the unique number. |
| Bit Manipulation | Single Number II | Med | Todo | | | | |
| Bit Manipulation | Single Number III | Med | Todo | | | | |
| Bit Manipulation | Number of 1 Bits | Easy | Solved | 01/08/2026 | 5 | 4 | __builtin_popcount, or loop: while n, count++ and n &= (n−1) — clears the lowest set bit each step (runs once per set bit). |
| Bit Manipulation | Counting Bits | Easy | Todo | | | | |
| Bit Manipulation | Reverse Bits | Easy | Todo | | | | |
| Bit Manipulation | Missing Number | Easy | Solved | 29/07/2026 | 5 | 3 | XOR all indices 0..n with all elements — equal values cancel (a^a=0), leaving the missing number. Alt: Gauss sum n(n+1)/2 minus the array sum. |
| Bit Manipulation | Bitwise AND of Numbers Range | Med | Todo | | | | |
| Bit Manipulation | Sum of Two Integers | Med | Todo | | | | |
| Bit Manipulation | Add Binary | Easy | Todo | | | | NC250 |
| Bit Manipulation | Reverse Integer | Med | Todo | | | | NC250 |
| Bit Manipulation | Minimum Array End | Med | Todo | | | | NC250 |
| Design | LRU Cache | Med | Solved | 03/08/2026 | 10 | 4 | std::list<pair<key,val>> + unordered_map<key, list-iterator>. get: move that node to the front (splice), return val. put: update+move to front, or insert at front; if over capacity, evict the back node and erase its map entry. |
| Design | LFU Cache | Hard | Todo | | | | |
| Design | Insert Delete GetRandom O(1) | Med | Solved | 03/08/2026 | 15 | 3 | vector for O(1) random access (rand() % size) + unordered_map value→index for O(1) exists/lookup. O(1) delete: overwrite the target index with the last element, fix that element's index in the map, pop_back the vector, erase the key from the map. |
| Design | Design Circular Queue | Med | Solved | 03/08/2026 | 20 | 3 | Array ring-buffer: keep head index + size; enqueue writes at (head+size)%cap, dequeue does head=(head+1)%cap, front=buf[head], rear=buf[(head+size−1)%cap], full when size==cap. (Alt: linked list with head/tail pointers.) The array/modulo version is what interviewers want. |
| Design | Design Front Middle Back Queue | Med | Solved | 03/08/2026 | 20 | 3 | Split into two deques (front half a, back half b). Maintain the invariant via a resize()/rebalance — b.size() at most 1 more than a, a never exceeds b — called after every op. Then push/pop at front/middle/back just read/write the ends and rebalance. |
| Design | Moving Average from Data Stream | Easy | Solved | 04/08/2026 | 5 | 4 | Fixed-size sliding window with a deque: push the new value, pop the front when over size, keep a running sum, return sum/size. |
| Design | Time Based Key-Value Store | Med | Solved | 04/08/2026 | 10 | 3 | unordered_map<string, map<int,string>> (key → timestamp → value). get: if key absent return ""; else upper_bound(timestamp) — if it's begin() return "", else prev(it)->second. Note: upper_bound then prev = "largest key ≤ target" (lower_bound is ≥, upper_bound is >). |
| Design | Design A Leaderboard | Med | Solved | 10/08/2026 | 20 | 3 | unordered_map<id,score> + multiset<int> of scores. multiset defaults to ascending — use greater<int> for descending (top-K). Gotcha: multiset.erase(value) removes ALL instances; erase an iterator (from find) to drop a single score. |
| Design | Design Tic-Tac-Toe | Med | Solved | 10/08/2026 | 20 | 3 | Brute force: O(n²) space, O(n) check (watch the diag flag reset). Optimal: rows[] + cols[] arrays + two ints diag/antiDiag; each move adds +1 (or −1 per player) to its row, col, and diag/antiDiag if on them — magnitude n = win. antiDiag when col == n−1−row. O(1) check, O(n) space. |
| Design | Design Memory Allocator | Med | Solved | 17/08/2026 | 30 | 3 | Simple (fits constraints): vector<int> size n; allocate = scan for a free run ≥ size, fill with mID; free = zero all cells of mID. Better: map<start,len> of free blocks + unordered_map<mID, vector<(start,len)>> of allocations. Allocate: scan free map for first block ≥ size, carve + update both. Free: for each of mID's intervals, coalesce with neighbors — lower_bound to find insert spot, merge prev (prev.start+len==s) and next (s+size==it->first). lower_bound because the freed interval isn't in the map yet ("where this key would go"). |
| Design | Design Excel Sum Formula | Hard | Todo | | | | |
| Design | Design Spreadsheet | Med | Solved | 17/08/2026 | 20 | 3 | unordered_map<string,int> of cells. Watch the operator[] trap — it auto-creates a cell on read; use insert_or_assign() to set and find()+end() check to read, so you don't accidentally spawn empty cells. |
| Design | Design In-Memory File System | Hard | Todo | | | | |
| Design | Design a Text Editor | Hard | Todo | | | | |
| Design | Design Search Autocomplete System | Hard | Todo | | | | |
| Design | Design Skiplist | Hard | Todo | | | | |
| Design | Design HashSet | Easy | Solved | 04/08/2026 | 10 | 3 | Same as Design HashMap but store presence only — bucket array + chaining, and on add/contains just check whether the key exists in its bucket. |
| Design | Design HashMap | Easy | Solved | 04/08/2026 | 10 | 3 | Emulate a real hash map: vector<vector<pair<int,int>>> — outer vector is the bucket table, inner vector is the chain for collisions. Hash key→bucket, linear-scan the chain for get/put/remove. |
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
