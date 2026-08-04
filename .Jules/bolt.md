# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-18 - [Bulk Database Queries replacing N+1 iterations]
**Learning:** SQLite iteration in `get_subject_wise` was performing 3 individual queries per subject (18 total for 6 subjects) inside a loop, creating unnecessary I/O overhead. Converting these into bulk `IN (...)` queries with `GROUP BY` reduced the query count to 3.
**Action:** When calculating performance metrics across multiple distinct categories (like subjects), avoid looping single queries. Instead, aggregate using `IN` and `GROUP BY` clauses with dynamically parameterized placeholders to ensure efficient batched execution while maintaining tenant isolation. Wrap each bulk operation in isolated `try...except` blocks to prevent missing tables (e.g., `answer_questions`) from failing the whole batch.
