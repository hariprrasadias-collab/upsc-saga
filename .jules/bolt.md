## 2025-05-03 - N+1 DB Queries in `get_available_bosses`
**Learning:** Found an N+1 query pattern where the `arena.py` routes iterate over uniquely retrieved items (e.g., years and subjects) to call another database-querying function `get_boss_stats` (which uses `COUNT(*)`). This causes significant unbatched requests for each item, directly harming performance.
**Action:** When mapping over aggregations, favor single SQL queries returning grouped metrics (e.g., `GROUP BY` and `COUNT(*)`) that directly format the UI dict logic, avoiding loop-nested sequential DB queries.
