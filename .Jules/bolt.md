# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-03-03 - [Optimized weak areas calculation to eliminate N+1 queries]
**Learning:** The `identify_weak_areas` function in `backend/app/services/analytics_service.py` iteratively executed database queries inside a `for subj in low_scores:` loop to fetch historical `test_attempts` data for each bottom-performing subject. This resulted in an N+1 query bottleneck that scales linearly with the number of subjects configured to be analyzed.
**Action:** When calculating historical trends across multiple filtered entities (like low performing subjects), fetch the requisite historical data collectively outside the loop using an `IN` clause. Group the results in Python memory (`scores_by_subject = {s: [] for s in subjects}`) to reduce database round-trips from O(N) to O(1).
