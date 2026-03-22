# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-22 - [Optimized subject-wise analytics to eliminate N+1 queries]
**Learning:** The `get_subject_wise` route in `backend/app/routes/analytics.py` was fetching performance metrics iteratively in a `for subject in subjects` loop by calling `get_subject_performance`, generating 3 queries per subject (18 total for 6 subjects). This is a classic N+1 query problem that scales poorly.
**Action:** Replace iterative, single-item SQL queries inside loops with batched queries using the `IN (...)` clause and `GROUP BY`, transforming $O(N)$ operations into $O(1)$ operations with significant execution time reduction (~3x faster). Wrap each table's query in its own granular `try...except` block to ensure graceful degradation if any single table is missing or fails.
