# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-05-03 - Weak Area Performance N+1 Elimination
**Learning:** Found a severe N+1 query bottleneck in `analyze_all_performance` where `analyze_topic_performance` was called in a loop for every topic, triggering 2 SELECT queries and 1 UPSERT per topic. This scales poorly (O(N)) for many topics.
**Action:** Replaced the loop with 2 bulk `GROUP BY topic` SQL queries and calculated weakness scores locally. Results are then written in one step via a single bulk `executemany` UPSERT, reducing execution time drastically.
