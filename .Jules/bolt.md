# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized weak area performance analyzer]
**Learning:** The `analyze_all_performance` function iteratively executed 3 queries per topic in a loop (the classic N+1 problem) when recalculating weakness scores.
**Action:** Always replace iterative SELECT queries with a single aggregated query fetching all necessary logic upfront, calculate the domain scores natively in Python, and use `executemany` with `INSERT ... ON CONFLICT DO UPDATE` to do bulk upserts.
