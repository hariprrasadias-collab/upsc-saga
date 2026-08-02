# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-08-02 - [Bulk Query Optimization in Analytics]
**Learning:** The /api/analytics/subject-wise route was suffering from an N+1 query problem, making 3 distinct database queries per subject sequentially.
**Action:** Refactored iterative queries into bulk GROUP BY and IN queries wrapped in isolated try-except blocks, dropping the query count from 18 to 3 while maintaining fault tolerance across independent tables.
