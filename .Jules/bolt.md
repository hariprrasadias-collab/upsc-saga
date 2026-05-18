# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-05-19 - Avoid N+1 Subqueries in identify_weak_areas
**Learning:** The `identify_weak_areas` function in `backend/app/services/analytics_service.py` was fetching trend scores for each low-performing subject using a loop (an N+1 query pattern).
**Action:** Replace the loop with a single `IN` query utilizing `placeholders = ','.join(['?'] * len(subjects))` to bulk-fetch all required attempts. Correlate the data locally using a Python dictionary (`scores_by_subject[s['subject']].append(s)`) instead of firing an additional query per row.
