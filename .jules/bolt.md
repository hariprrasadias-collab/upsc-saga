## 2025-02-04 - [Analytics N+1 Queries]
**Learning:** Found `get_progress_trend` executing redundant SQL queries inside a date loop (O(N) behavior), relying on current state rather than historical data.
**Action:** When implementing trend endpoints, always pre-calculate aggregates or use `GROUP BY` outside loops. If history is missing, calculate current state once and project it.
