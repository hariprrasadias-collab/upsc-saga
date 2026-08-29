# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2023-11-20 - [Eliminated N+1 query loop when fetching mock test weak areas]
**Learning:** `identify_weak_areas` iteratively fetched historical scores for bottom-performing subjects, generating an N+1 database query loop that scaled linearly with `limit`. Grouping results in memory drastically cut execution times.
**Action:** When mapping list metrics via database queries in a loop, pre-fetch using a dynamic parameterized `IN` clause (e.g. `IN (?, ?, ...)`) to compile the dataset into a dictionary or `collections.defaultdict(list)`, shifting the mapping overhead from the database to Python.
