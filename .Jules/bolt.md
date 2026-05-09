# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-05-18 - Optimize Boss Stats / N+1 Prevention
**Learning:** In the `/api/arena/bosses` route, the application originally fetched distinct years and subjects, then executed a separate `SELECT COUNT(*)` query for each one individually, creating an N+1 performance bottleneck.
**Action:** Prevent N+1 query bottlenecks on large datasets by using a single `GROUP BY` query to fetch both the distinct identifiers and their corresponding counts simultaneously, passing the precalculated counts down to dependent functions.
