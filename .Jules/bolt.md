# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-03-03 - [Optimized seer routes to eliminate N+1 queries]
**Learning:** `consult_the_seer` looped to fetch XP history, causing 7 queries, and `get_year_trends` looped over years, querying counts for each, leading to N+1 performance bottlenecks.
**Action:** Replace iterative database queries with single bounded/aggregated queries (e.g., using `GROUP BY`) mapped to Python dictionaries to achieve O(1) performance and eliminate N+1 bottlenecks.
