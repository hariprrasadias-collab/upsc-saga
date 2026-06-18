# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Eliminated N+1 query in mock test submission]
**Learning:** The mock test submission logic in `backend/app/routes/mock_tests.py` updated the `is_correct` status for each answer inside a loop using iterative `execute` calls, which triggered a significant N+1 query bottleneck during test evaluations.
**Action:** When updating bulk database records during grading or similar tasks, gather the update parameters in a list and perform a single batched query using `conn.executemany` to minimize database hits.
