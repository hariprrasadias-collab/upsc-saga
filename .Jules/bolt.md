# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-24 - SQLite Correlated Subquery Optimization
**Learning:** When optimizing SQLite correlated subqueries on heavily filtered main queries (e.g., fetching the latest review for flashcards in a specific deck), do not replace them with non-correlated `LEFT JOIN` + `GROUP BY` queries, as this forces a full table scan.
**Action:** Instead, retain the correlated subqueries and add a covering composite index (e.g., `(foreign_key, sort_column DESC)`) to optimize the subquery lookups without sacrificing the efficient filtering of the main query.
