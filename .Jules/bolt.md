# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-06-19 - N+1 Bottlenecks in the Seer API Endpoints
**Learning:** The `consult_the_seer` and `get_year_trends` endpoints contained implicit N+1 bottlenecks. Specifically, iterating over dynamic sets like dates (7 iterations) and years (N iterations based on db row counts) while executing nested db queries inside the loop compounded query execution latency. Wait states heavily scaled linearly relative to data volume.
**Action:** When aggregating or reporting on data that spans grouped domains (e.g., historical timelines or distinct entity categories), fetch all relevant records within a single bounds query (e.g., using `BETWEEN` or `GROUP BY ...`) rather than looping across bounded parameters. Transform and restructure the query responses locally within Python dictionaries in memory to yield expected JSON array schemas.
