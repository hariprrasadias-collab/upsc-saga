# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-03-03 - [Optimized seer year trends to eliminate N+1 queries]
**Learning:** The `get_year_trends` function in `backend/app/routes/seer.py` iteratively fetched `pyq_questions` data via a loop over distinct years, leading to an N+1 query problem. For a large dataset (e.g. 225,000 rows), this caused ~1.0 second execution time due to multiple database roundtrips.
**Action:** Replace the iterative queries with a single query that groups by both `year` and `subject` (transforming N+1 roundtrips into a single roundtrip), and then process the grouping in-memory.
