# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-06-10 - Refactor database updates in loops to executemany
**Learning:** Database updates inside iterative loops, such as scoring test answers where `UPDATE` is called for every individual question, can cause severe N+1 bottlenecks.
**Action:** Lift the `UPDATE` logic out of loops by accumulating target IDs or parameters into a list, and then executing a single `executemany` statement at the end of the loop to process all updates in bulk.
