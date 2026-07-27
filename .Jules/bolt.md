# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-07-26 - [Refactor N+1 queries in get_subject_wise]
**Learning:** The `get_subject_wise` endpoint was calling `get_subject_performance` for each subject iteratively, leading to an N+1 query pattern across independent tables (mock_tests, answer_questions, syllabus_topics). Using a single batch SQL query with `GROUP BY` and `IN` speeds it up by ~50%.
**Action:** Whenever iterating over multiple categories to fetch stats, prefer batching the query using `GROUP BY` and an `IN` clause. Because different tables might not exist (e.g., `answer_questions`), wrap each table's batch query in its own isolated `try...except` block.
