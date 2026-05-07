# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-22 - Replaced N+1 subqueries with batched grouped queries
**Learning:** The `get_year_trends` endpoint previously generated an N+1 issue because for each year, a separate `GROUP BY subject` query was made against `pyq_questions`, resulting in many inefficient roundtrips to the SQLite database.
**Action:** Replace looped queries with a single query (`SELECT year, subject, COUNT(*) GROUP BY year, subject`), grouping the payload manually on the Python backend. Make sure to use `sorted()` or similar when assembling the distinct sets to maintain stable JSON structures.
