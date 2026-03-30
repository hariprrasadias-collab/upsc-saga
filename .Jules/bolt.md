# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-03-30 - [Optimized mock score trend retrieval to eliminate N+1 queries]
**Learning:** The `identify_weak_areas` function in `backend/app/services/analytics_service.py` iterated over the lowest scoring subjects, executing a new query for each subject to fetch historical `test_attempts` scores. This caused N+1 database queries, slowing down the weakness identification and performance trend feature.
**Action:** Used an `IN (...)` query block to fetch all required scores for the multiple subjects at once. Leveraged Python's `collections.defaultdict` to group these historical scores efficiently in memory, ensuring O(1) database queries while still allowing subject-level trend calculations.
