# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-10-09 - [Optimized Subject Breakdown rendering]
**Learning:** The React component repeatedly executed expensive array operations (`.flatMap().filter()` twice per subject) within a map loop inside the render function for the subject breakdown view, causing significant O(N) overhead.
**Action:** Moved the computation into a `useMemo` hook that generates an O(1) dictionary lookup map (`Record<string, {total: number, completed: number}>`) to eliminate redundant O(N) overhead during renders.
