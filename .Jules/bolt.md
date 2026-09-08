# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-23 - [Optimize overall plan progress computation in StudyPlanDashboard]
**Learning:** In React components, repeatedly calling array methods like `flatMap` and `filter` on a large dataset (like an active plan) inside a map loop leads to O(M*N) time complexity where N is the total number of slots and M is the number of mapped items (subjects). We cannot use `useMemo` conditionally.
**Action:** Pre-calculate the counts using a single O(N) pass with standard variables inside the block before rendering to prevent unnecessary array allocations on every render.
