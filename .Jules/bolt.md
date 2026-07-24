# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-04 - [Optimized subject-wise performance analytics to eliminate N+1 queries]
**Learning:** The `get_subject_wise` endpoint in `backend/app/routes/analytics.py` called `get_subject_performance` in a loop across 6 subjects. Since `get_subject_performance` executed 3 queries per subject (for mock averages, answer writing, and syllabus progress), this caused an N+1 query problem, resulting in 18 separate database calls.
**Action:** When calculating statistics across distinct categories (like subjects), pre-calculate the aggregates for all categories at once using single `GROUP BY` queries before the loop. Pass this aggregated dictionary down to the helper function (e.g., as `precalc_data=None`) to bypass the N+1 issue while retaining backward compatibility for isolated calls. Ensure all filtering clauses (like `WHERE user_id = ?`) are correctly translated to the bulk queries to avoid data leakage. Furthermore, when implementing the `precalc_data` logic inside the helper function, wrap only the original DB queries in an `if precalc_data is None:` block rather than using an early `return` to guarantee that any subsequent default logic (such as initializing other uncalculated metrics to 0) still executes.
