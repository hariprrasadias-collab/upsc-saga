# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-05-18 - [Optimized Seer trends query to eliminate N+1 loop]
**Learning:** The `get_year_trends` function performed an independent query for each year to get subject counts, which became a bottleneck as the dataset grew.
**Action:** Always fetch grouped aggregates in a single bulk query (e.g. `GROUP BY year, subject`) and build a local nested mapping instead of executing database queries inside application logic loops.
