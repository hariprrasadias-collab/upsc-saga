# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-03-15 - [Optimized year trends to eliminate N+1 queries using GROUP BY]
**Learning:** The `get_year_trends` endpoint in `backend/app/routes/seer.py` previously executed a database query to count subjects for each distinct year (an O(N) operation inside a loop). This was inefficient and could be solved by running a single query grouping by both year and subject.
**Action:** When aggregating data across multiple dimensions (e.g., year and subject), use a single `GROUP BY` SQL query and process the results into a nested Python dictionary (e.g., `collections.defaultdict`) instead of executing queries inside a loop. This prevents N+1 query inefficiencies.
