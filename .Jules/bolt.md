# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-13 - [Combine multi-table date aggregations into a single UNION ALL query]
**Learning:** Sequential queries against different database tables to extract dates for a unified calculation (like a daily activity streak) create multiple network roundtrips and significantly increase database latency.
**Action:** When aggregating similar data points (like timestamps) from multiple disparate tables to construct a unified view (such as activity streaks), always batch the queries into a single `UNION ALL` SQL statement to minimize database roundtrips and drastically improve performance.
