# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-03-03 - [Optimize N+1 query in `analyze_all_performance`]
**Learning:** The `analyze_all_performance` function in `backend/app/services/weak_area_analyzer.py` iterated through all unique topics and performed N+1 database queries via `analyze_topic_performance(topic)` to calculate the weakness score for each topic. As the number of topics grew, the performance degraded significantly, dropping from seconds to fractions of a second with batch execution.
**Action:** Used bulk `GROUP BY` SQL queries to fetch performance stats and recent failures for all topics at once. Then, calculated the weakness score locally using a Python dictionary and applied all updates via a single `executemany` UPSERT statement.
