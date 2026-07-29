# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2026-07-29 - Bulk Queries Across Independent Tables
**Learning:** Replacing N+1 loops with bulk SQL queries across multiple independent tables (e.g., mock_tests, answer_writing, syllabus_topics) introduces a failure risk: a missing table or schema issue in one domain will halt the entire batch execution for all other domains.
**Action:** Always wrap each individual table's bulk query in its own isolated `try...except` block to preserve fault tolerance when aggregating data from decoupled sources.
