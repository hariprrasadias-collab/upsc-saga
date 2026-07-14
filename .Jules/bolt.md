# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-07-14 - Optimize N+1 Query in Weak Area Analyzer
**Learning:** Analyzing performance across all topics (analyze_all_performance) previously executed separate count queries and UPSERTs inside a loop over every topic, causing an N+1 bottleneck on the database when processing bulk analytics.
**Action:** Implemented a single `GROUP BY` query to fetch aggregate statistics for all topics upfront, and an `executemany` call for bulk UPSERTs. Passed pre-calculated counts down to helper functions to bypass redundant individual queries, optimizing DB performance.
