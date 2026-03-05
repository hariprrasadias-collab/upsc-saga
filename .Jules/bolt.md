# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized N+1 queries in identify_weak_areas]
**Learning:** The `identify_weak_areas` function in `backend/app/services/analytics_service.py` contained an N+1 query loop fetching historical mock scores for every underperforming subject independently. This created unnecessary database calls, scaling negatively with the number of weak subjects.
**Action:** Replace looped database queries that filter by ID/subject with a single combined query using an `IN` clause (e.g., `WHERE subject IN (?,?)`), and then use Python's `collections.defaultdict` to efficiently group the results in memory.
