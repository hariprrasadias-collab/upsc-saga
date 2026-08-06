# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-05-22 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `identify_weak_areas` function in `backend/app/services/analytics_service.py` contained an N+1 query loop when fetching mock test scores over time for multiple subjects. Because each subject had multiple scores over time, this was transformed into a single bulk query fetching all scores across multiple subjects using an `IN` clause, returning records that can easily be grouped by subject in-memory.
**Action:** Replace iterative `SELECT` database queries with `IN` clause bulk queries combined with in-memory grouping, dropping N+1 database operations to O(1) bulk fetch and minimizing connection latency.
