# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-22 - [Optimized StudyPlanDashboard overview rendering]
**Learning:** The `StudyPlanDashboard` component repeatedly scanned the entire `activePlan` array (which could be quite large) using `reduce` and `flatMap.filter` for every single subject in the overall view, resulting in O(N * S) time complexity where N is total slots and S is the number of subjects.
**Action:** Replace multiple passes over the array with a single pass that computes all totals and subject-specific stats into an accumulator object (`subjectStats`), reducing the operation to O(N) and avoiding wasteful re-evaluations during renders.

## 2024-05-22 - [Optimized StudyPlanDashboard overview rendering]
**Learning:** React re-renders will repeatedly execute expensive rendering logic unless memoized. The previous single-pass optimization was still executing on every render.
**Action:** Always wrap derived expensive data calculations in `useMemo` when calculating aggregated statistics from large arrays like `activePlan` to avoid O(N) operations on every single render cycle.

## 2024-05-22 - [Fixed useMemo conditional hook violation]
**Learning:** While `useMemo` is great for avoiding re-evaluations, React's Rules of Hooks strictly prohibit calling hooks (like `useMemo`) inside loops, conditions, or nested functions (like the `if (viewMode === 'overall')` block).
**Action:** Do not use `useMemo` if the memoized calculation must reside inside a conditional block. In such cases, either hoist the condition inside the `useMemo` at the top level of the component or stick to a highly optimized synchronous single-pass loop (which is still much faster than the O(N * S) unoptimized version).
