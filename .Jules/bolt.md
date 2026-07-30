# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-05-18 - [Fix N+1 in Weak Area Analyzer]
**Learning:** The previous implementation used an N+1 query pattern where it fetched all topics, and then ran 2 SQL queries *per topic* in python loop.
**Action:** Used SQL `GROUP BY` to aggregate all topics and fetch them in one bulk query, reducing queries from O(N) to O(1), and modified the helper function to accept `precalc_data` to reuse existing calculations.
