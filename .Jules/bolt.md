# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-05 - [Optimized Seer year trends to eliminate N+1 queries]
**Learning:** The `get_year_trends` function in `backend/app/routes/seer.py` iteratively fetched `pyq_questions` data `N` times (via `SELECT COUNT(*)` queries inside a `for year_row in years:` loop, where `N` is the number of distinct years). This pattern severely degraded database performance.
**Action:** Combine repeated iterative database fetches into a single query using `GROUP BY year, subject`, and offload the aggregation step to Python code utilizing dictionaries. This converts an O(N) database query scenario into O(1).
