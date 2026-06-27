# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-04 - [Optimize global AshParticles re-renders]
**Learning:** Heavy animated components placed at the root of an app (like `AshParticles` in `App.tsx`) will needlessly re-render all their DOM nodes every time global state (e.g., current tab) changes, significantly impacting UI responsiveness. Furthermore, using `useEffect` to generate static initial data causes an unnecessary secondary render cycle.
**Action:** Always wrap static/rarely-changing global visual components in `React.memo()`. Use lazy initialization (`useState(() => data)`) instead of `useEffect` for data that only needs to be generated once on mount to avoid double rendering.
