# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-03-03 - [Optimized flashcard analytics to use SQL conditional aggregation]
**Learning:** The `get_analytics` route in `backend/app/routes/flashcards.py` fetched all flashcards via `LEFT JOIN` and iterated over them in Python to determine their maturity bucket, representing an O(N) database-to-Python transfer and iteration overhead.
**Action:** Since maturity thresholds are fixed `halflife` intervals (e.g. `halflife < 1`, `1 <= halflife < 7`), use SQL conditional aggregation (`SUM(CASE WHEN ...)`) to shift the bucket counts to the database engine. This reduces N rows transferred to 1 row and completes in a fraction of the time.
