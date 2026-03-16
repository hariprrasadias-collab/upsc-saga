# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-03-16 - [Optimized analytics queries using UNION ALL]
**Learning:** When fetching date time series across isolated tables (like test attempts, reviews, answers), making separate `SELECT` queries and aggregating them in Python creates a significant N+1-like performance bottleneck due to multiple database roundtrips.
**Action:** Use `UNION` or `UNION ALL` in a single SQL query to offload the aggregation and distinct operations to the database level, drastically reducing execution time and memory overhead.
