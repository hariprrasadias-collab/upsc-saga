# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Fix N+1 query bottleneck in Arena Available Bosses list]
**Learning:** The `get_available_bosses` function originally utilized a standard O(N) database query pattern by fetching a distinct list of boss years/subjects, then invoking `get_boss_stats` (which contained a `SELECT COUNT(*)` query) individually for every single list item.
**Action:** Lift repeated counting logic by using a bulk `GROUP BY` SQL aggregation up front (e.g., `SELECT subject, COUNT(*) FROM pyq_questions GROUP BY subject`). Pass the pre-calculated metrics as an optional parameter to the child logic `get_boss_stats` to eliminate N+1 latency entirely.
