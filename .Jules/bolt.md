# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-03-03 - [Optimized seer endpoints to eliminate N+1 queries]
**Learning:** Functions like `consult_the_seer` and `get_year_trends` used iterative loops over dates or years, triggering multiple database queries (N+1 bottleneck). This severely degraded performance as the dataset and iterations scaled.
**Action:** Always replace application-level query loops with single aggregated queries utilizing `BETWEEN` or composite `GROUP BY` clauses, and map the aggregated data locally via Python dictionaries.
