# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-08-03 - [Refactored N+1 queries into isolated bulk queries]
**Learning:** When refactoring iterative queries into bulk GROUP BY queries across multiple independent tables, wrapping each table's query in its own isolated try...except block is crucial. This preserves fault tolerance, preventing a missing table from breaking the entire batch operation.
**Action:** Always use isolated try...except blocks for bulk queries across different tables to ensure robust and fault-tolerant endpoints.
