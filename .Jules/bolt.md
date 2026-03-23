# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-02-28 - Optimizing multi-table metrics aggregations in SQLite
**Learning:** While `UNION ALL` can reduce latency in SQLite queries by combining extractions from different tables, it causes the entire query to fail if any underlying table is missing. For environments with varying schema states (like early phases of a startup app where some tables may not be created yet), executing queries for individual tables sequentially within their own `try...except` blocks is a much more robust approach to batching.
**Action:** When refactoring N+1 queries that aggregate data across multiple tables, prioritize creating individual batched queries (e.g., using `IN (...)` and `GROUP BY`) wrapped in their own `try...except` blocks to ensure graceful degradation over attempting to combine everything into a single massive query.
