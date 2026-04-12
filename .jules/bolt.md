## 2026-04-12 - [Optimized seer XP history query]
**Learning:** The `consult_the_seer` endpoint executed iterative `SELECT SUM()` queries in a Python loop to calculate 7 days of XP history, leading to an N+1 bottleneck.
**Action:** Replaced the loop with a single aggregate SQL query (`GROUP BY due_date`) mapped to a Python dictionary, dropping execution from O(N) database calls to O(1) local lookup per day. Always handle `NULL` edge cases returned by `SUM()` when using Python dictionary lookups.
