# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-23 - Weak Area Analyzer N+1 DB Queries Bottleneck
**Learning:** `analyze_all_performance` inside `backend/app/services/weak_area_analyzer.py` had a severe N+1 database querying anti-pattern. It was fetching distinct topics, then inside a loop, it was executing `analyze_topic_performance` for *each* topic. This internal function executed a stats `SELECT`, a recent failures `SELECT`, and an `INSERT ... ON CONFLICT` statement per topic, resulting in O(N) database queries (where N is the number of topics). Since the loop only processed data via SQL internally, it could all be unified.
**Action:** Replaced the loop and individual sub-queries with three O(1) operations. First, bulk fetched all topic statistics using `GROUP BY topic, subject`. Second, bulk fetched all recent failures using `GROUP BY topic` and correlated the results locally with Python dictionaries. Finally, executed a single bulk `cursor.executemany` statement to `UPSERT` the computed values into the `weak_areas` table, massively reducing execution time from ~2.8 seconds to ~0.04 seconds for 1000 topics.
