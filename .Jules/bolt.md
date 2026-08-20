# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2026-08-20 - [Fix N+1 query in analytics service]
**Learning:** Replaced nested SQL query for mock test history inside a loop over subjects with a single grouped query fetched beforehand in `backend/app/services/analytics_service.py`. This avoids an N+1 query bottleneck which slows down the analytics dashboard for users with a large test history.
**Action:** Always fetch bulk data before looping over items when retrieving historical performance data.
