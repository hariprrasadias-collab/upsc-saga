# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-22 - Optimized seer trends to eliminate N+1 queries
**Learning:** The `get_year_trends` function iterated over years and ran individual queries (`1 + N`) to get subjective counts per year, which is unnecessary since the database can `GROUP BY` both year and subject in a single pass.
**Action:** Always prefer `GROUP BY` across multiple dimensions mapping to an in-memory dictionary rather than a loop executing repeated single-parameter aggregations.
