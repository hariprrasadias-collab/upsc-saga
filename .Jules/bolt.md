# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-22 - [Optimizing Static Objects in React Components]
**Learning:** When optimizing static objects in React components, do not wrap them in `useMemo` as it introduces unnecessary hook overhead. Instead, hoist the static object completely outside the component module scope to prevent reallocation on every render.
**Action:** Move static objects outside the React component completely.

## 2025-03-03 - [Optimizing function references]
**Learning:** Extract functions that don't depend on component scope to standalone components or hooks instead of just `useCallback`. This reduces re-creation overhead. Use `useMemo` to pre-calculate values rather than calling functions during render.
**Action:** Extract functions to standalone components and hoist static configs, and pre-calculate expensive computations with `useMemo`.
