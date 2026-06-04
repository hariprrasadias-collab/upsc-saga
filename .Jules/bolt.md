# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-06-03 - [Optimized consult_the_seer and get_year_trends to eliminate N+1 queries]
**Learning:** The `consult_the_seer` and `get_year_trends` functions in `backend/app/routes/seer.py` used loops over dates and years respectively, making individual database queries within each loop iteration. This caused significant N+1 query bottlenecks, drastically increasing latency when fetching XP histories or PYQ distribution data.
**Action:** Replaced the loops over dates and years with single aggregated queries using `BETWEEN` and composite `GROUP BY` clauses. This fetches all the required data in one go and relies on python to correlate and structure the final payload, achieving an order of magnitude speedup.
