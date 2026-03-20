# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized boss aggregation query to eliminate N+1 queries]
**Learning:** In the `get_available_bosses` function inside `backend/app/routes/arena.py`, a `SELECT COUNT(*)` query was being executed iteratively for each unique year and subject retrieved from earlier queries. This was a classic N+1 problem, causing latency to scale directly with the number of unique years/subjects.
**Action:** Replaced the iterative fetching with single aggregate queries using `GROUP BY` (e.g., `SELECT year, COUNT(*) as count FROM pyq_questions GROUP BY year`). This simple structural change successfully reduced latency by about half during benchmarking. Always look to replace loop-driven counts with database-level aggregations.
