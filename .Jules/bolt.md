# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-03-16 - [Optimized weak areas calculation to eliminate N+1 query loop]
**Learning:** The `identify_weak_areas` function historically iterated through bottom-performing subjects to calculate trend metrics, fetching past test attempt scores from the database individually for each subject inside a loop.
**Action:** Use an `IN` clause to fetch all relevant historical mock scores in a single batched query, and structure the data into a `collections.defaultdict(list)` mapped by subject beforehand. This resolves the N+1 issue, mapping O(N) database queries to O(1) batched query + O(N) memory mapping.
