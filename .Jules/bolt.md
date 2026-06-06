# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-06-06 - Optimize Dashboard Subject Analytics Loop
**Learning:** Making separate queries per subject inside a loop in `get_subject_wise` created an N+1 bottleneck. Grouped bulk queries using `IN` clauses significantly improve performance when dashboard data relies on multiple modules.
**Action:** Use a single grouped bulk query (`get_all_subject_performances`) using `GROUP BY` and `IN` for dashboard aggregations to fetch all subject metrics efficiently.
## 2024-06-06 - Fixing pyq and flashcards in bulk query
**Learning:** Initial implementation of `get_all_subject_performances` was missing the `pyq_attempted` and `flashcard_mastered` values, resulting in data loss for these metrics. When grouping multiple queries by subject, all values present in the result dict should be queried and updated to prevent missing metrics. Also the `user_id` was missing from `syllabus_topics` in the initial implementation.
**Action:** Implemented queries to bulk update `pyq_attempted` and `flashcard_mastered`. Ensure all dictionary keys are fully populated when transitioning from a per-subject loop to a bulk-fetch dictionary.
