# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2026-04-13 - Resolve Arena Boss N+1 Query Bottleneck
**Learning:** In endpoints that aggregate dynamically generated stats for multiple objects (like available years or subjects for boss fights), executing a `SELECT COUNT(*)` iteratively per object creates a severe N+1 query bottleneck. While simple to write initially, this scales poorly as the number of years or subjects grows.
**Action:** Replaced iterative loops containing  with a single bulk query using `GROUP BY` to fetch all keys and their corresponding counts at once. Updated the signature of the underlying utility function (`get_boss_stats`) to accept a `precomputed_count` parameter, gracefully preventing duplicate queries while maintaining backward compatibility for isolated calls.
## 2026-04-13 - Resolve Arena Boss N+1 Query Bottleneck
**Learning:** In endpoints that aggregate dynamically generated stats for multiple objects (like available years or subjects for boss fights), executing a SELECT COUNT(*) iteratively per object creates a severe N+1 query bottleneck.
**Action:** Replaced iterative loops containing SELECT COUNT(*) with a single bulk query using GROUP BY to fetch all keys and their corresponding counts at once. Updated the signature of the underlying utility function (get_boss_stats) to accept a precomputed_count parameter.
