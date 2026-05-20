# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-05-19 - Optimized Subject Analytics Endpoint
**Learning:** The `get_subject_wise` endpoint in `backend/app/routes/analytics.py` had an N+1 query bottleneck because it looped over subjects and called `get_subject_performance` for each, executing multiple database queries sequentially per subject.
**Action:** Replaced the loop with a single call to `get_all_subject_performances`, which fetches metrics (mocks, answers, syllabus) for multiple subjects simultaneously using bulk `GROUP BY` queries and `IN` clauses.
