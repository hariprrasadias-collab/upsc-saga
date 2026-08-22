# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-02-18 - Batch query to replace N+1 loop in identify_weak_areas
**Learning:** The `identify_weak_areas` analytics service had an N+1 query issue, running a new database query for each subject that had a low score. It also suffered from a column name mismatch `name` vs `topic`.
**Action:** Querying data in a loop is an anti-pattern. Instead, gather all required subject filters and execute one query utilizing the `IN` clause with dynamically bound parameters. This batches operations and significantly lowers execution time. Also double check schemas before writing code.
