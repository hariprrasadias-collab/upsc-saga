# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-03-03 - [Optimized syllabus progress trend to eliminate recalculations]
**Learning:** In `frontend/src/components/Syllabus/SyllabusTracker.tsx`, the `getProgress` function was called repeatedly during renders to calculate the progress for each paper. Inside the function, it was executing expensive `.filter()` and `.reduce()` operations on the `analytics.breakdown` array.
**Action:** Extract expensive calculations that run in a loop or multiple times per render into a `useMemo` hook that pre-computes a lookup map (e.g., `progressMap`). This changes O(N) operations per call into O(1) lookups, significantly reducing React component render time.
