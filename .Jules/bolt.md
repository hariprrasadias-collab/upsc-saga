# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2026-11-01 - [Batch subject performance metrics to eliminate N+1 queries]
**Learning:** The get_subject_wise route in analytics called get_subject_performance in a loop, resulting in an N+1 query problem (3 queries per subject * 6 subjects = 18 queries).
**Action:** Replace looped individual queries with batched aggregate queries grouped by subject to fetch all needed metrics in O(1) queries instead of O(N).
