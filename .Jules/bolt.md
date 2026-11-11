# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Eliminated N+1 queries in Weak Area Analyzer]
**Learning:** The `analyze_all_performance` function iteratively analyzed topics by querying the database 2 times and executing an `INSERT` for each distinct topic. Iterative looping DB queries cause severe performance bottlenecks, especially in cron-like aggregated tasks, taking O(N) queries where N is the number of distinct categories.
**Action:** Replace looped `SELECT` and `INSERT` queries with single aggregated statements. Utilize `GROUP BY` to retrieve aggregated statistics for all groups at once, then compute updates in memory, and finally save updates efficiently using `cursor.executemany`.
