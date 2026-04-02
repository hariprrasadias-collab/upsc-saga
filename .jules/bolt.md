
## 2025-03-01 - [Arena Bosses N+1 Queries Optimization]
**Learning:** Found a severe N+1 problem in `arena.py` where listing active bosses dynamically calculated `COUNT(*)` per row iteratively instead of using `GROUP BY`.
**Action:** Always inspect loops containing `SELECT COUNT(*)` or fetching related models. Refactor logic to accept `pre_count` and `pre_row` optionally so backend functions remain safely backwards compatible when optimizations introduce batch pre-fetching.
