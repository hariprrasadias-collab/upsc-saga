# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-22 - Optimized Arena Boss Stats Generation
**Learning:** The `get_available_bosses` function originally executed an N+1 query pattern by making a separate `SELECT COUNT(*)` database call for every single year and subject dynamically generated.
**Action:** When generating dynamic lists that require counts, use SQL `GROUP BY` and `COUNT(*) as count` to fetch all necessary totals in a single bulk query, and modify the target function to optionally accept pre-calculated values to bypass redundant database lookups.
