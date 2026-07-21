# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2026-07-20 - Optimizing N+1 Queries Across Independent Tables
**Learning:** When refactoring iterative function calls into bulk SQL queries for independent tables (like `mock_tests`, `answer_writing`, and `syllabus_topics`), a missing table (e.g., `answer_questions` in local tests) can crash the entire endpoint.
**Action:** Always wrap each table's bulk query in an isolated `try...except` block to preserve fault tolerance and prevent failure cascades.
