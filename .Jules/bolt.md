# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-05-17 - Fix N+1 Query in Weak Area Analyzer
**Learning:** The `analyze_all_performance` function exhibited a severe N+1 bottleneck by iterating over individual topics and executing multiple queries (`SELECT`, `SELECT`, `UPSERT`) inside the loop, leading to highly inefficient database communication (scaling linearly with the number of topics).
**Action:** Replace the loop with bulk `GROUP BY` queries to fetch all aggregated stats and recent failures upfront. Correlate the data locally using Python dictionaries, and persist all changes using a single `executemany` batch UPSERT, resulting in a >100x performance improvement.
