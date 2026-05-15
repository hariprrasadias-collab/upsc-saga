# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-05-15 - [Optimized weak area identification to eliminate N+1 queries]
**Learning:** The `identify_weak_areas` function in `backend/app/services/analytics_service.py` originally fetched bottom-performing subjects and then executed a separate query inside a loop for each subject to get historical trends. This led to an N+1 query problem, creating multiple round-trips to the database.
**Action:** Instead of querying per subject, extract the subject list, use an `IN` clause to fetch all historical scores in one query, and group the data locally in Python using a dictionary.
