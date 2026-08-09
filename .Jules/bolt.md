# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-18 - Replacing iterative function calls with batched queries
**Learning:** When attempting to refactor iterative N+1 query patterns in Python (`get_subject_performance` called in a loop) into a single batched query using dynamic `IN` clauses, missing dependencies or missing tables in some development/test environments (like `answer_questions`) can cause the entire bulk operation to fail.
**Action:** Always ensure that when performing bulk SQL queries across multiple distinct tables, you wrap each table's bulk query in its own isolated `try...except` block to preserve fault tolerance and ensure one missing table doesn't crash the entire API endpoint.
