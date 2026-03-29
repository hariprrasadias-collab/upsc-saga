# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-03-03 - [Optimized consult_the_seer and get_year_trends]
**Learning:** Functions in `backend/app/routes/seer.py` were executing loops containing iterative `SELECT` queries across sequential dates or years, leading to N+1 query bottlenecks and unoptimized database access.
**Action:** Replace sequential queries within a loop with a single grouped query (`GROUP BY`) and use a Python `dict` or `defaultdict` to efficiently map results dynamically to the iterated sequences.
