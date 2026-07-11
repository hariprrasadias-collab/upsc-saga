# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized subject-wise performance fetching to eliminate N+1 queries]
**Learning:** The `get_subject_wise` function in `backend/app/routes/analytics.py` iteratively fetched performance data for 6 subjects by calling `get_subject_performance`, which executed 3 separate database queries per subject (18 queries total).
**Action:** Refactor iterative function calls that perform independent database queries into bulk SQL queries utilizing `GROUP BY` and `IN` clauses. When aggregating across multiple tables (e.g., `mock_tests`, `answer_writing`, `syllabus_topics`), isolate each bulk query within its own `try...except` block to maintain fault tolerance.
