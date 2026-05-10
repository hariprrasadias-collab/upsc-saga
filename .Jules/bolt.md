# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-05-10 - Fix N+1 Query in Arena Boss List
**Learning:** The `get_available_bosses` route previously executed a separate `COUNT(*)` query for every single year and subject, causing an N+1 query problem. This codebase pattern frequently occurs when iterating over categories to fetch aggregated stats.
**Action:** Instead of querying `COUNT(*)` inside the loop, use a `GROUP BY` clause in the initial query to fetch all counts in a single pass (`SELECT category, COUNT(*) as count FROM table GROUP BY category`). Pass the precomputed count down to the stat generator function.
