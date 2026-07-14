# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-07-13 - [Refactored Seer module loops to prevent N+1 SQL queries]
**Learning:** In the `seer.py` backend, analytic counts were queried inside Python loops causing N+1 database roundtrips (like checking XP for 7 days or distributions across years).
**Action:** Batch database hits by querying the entire dataset once, then grouping/mapping results with Python dictionaries (`xp_map = {row['due_date']: row['total_xp'] ...}`) before applying them to loop constructs, reducing time complexity from O(N) to O(1).
