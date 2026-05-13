# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-05-18 - Optimized Weak Area Analyzer N+1 Query
**Learning:** The `analyze_all_performance` function was querying the database once to get all topics, and then running an expensive query in a loop for every topic. This classic N+1 problem drastically slowed down performance.
**Action:** Used bulk `GROUP BY` queries and locally cached Python dictionaries instead of looping to make database queries, reducing query count and avoiding performance issues. Batch updates were performed using `cursor.executemany` which minimizes overhead.
