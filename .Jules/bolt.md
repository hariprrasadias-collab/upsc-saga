# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-03-03 - [Optimized Seer routes to eliminate N+1 queries]
**Learning:** Functions that aggregate data across time periods or categories (like XP over the last 7 days or subjects by year) can easily introduce N+1 query problems if implemented as loops making individual database queries.
**Action:** When aggregating or calculating values inside a loop that maps over a list of domains (dates, years, categories), refactor to use a single SQL `GROUP BY` query beforehand to retrieve all related counts at once, then process the results into a map for fast lookup inside the loop. O(N) queries become O(1).
