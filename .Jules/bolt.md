# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-11-09 - Backend N+1 Insert Optimization
**Learning:** When generating tests or quizzes with many questions in SQLite, inserting rows sequentially within a loop causes significant N+1 performance bottlenecks due to repeated query parsing and execution overhead.
**Action:** Always batch multiple `INSERT` statements into a single query using `executemany()` and accumulating parameters in a list beforehand, especially in endpoints handling dynamic lists (e.g., question generation).
