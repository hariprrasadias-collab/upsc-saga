# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Refactored get_subject_performance into a bulk query to eliminate N+1 queries]
**Learning:** In the `get_subject_wise_analytics` route, the application iterated over 6 subjects, running 3 queries for each (mock tests, answers, syllabus completion). This resulted in an N+1 query problem, creating 18 separate database calls.
**Action:** Batch multiple identical queries into a single query using the `IN` clause and `GROUP BY`, pulling the iterative loop out of the SQL execution. This optimizes an O(N) database query sequence down to O(1) bulk fetch operations.
