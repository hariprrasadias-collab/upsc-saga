# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-08-26 - [Sidebar Memoization]
**Learning:** Re-creating a large static object (menuGroups) on every render in a frequently toggled component like Sidebar causes unnecessary processing overhead.
**Action:** Hoist static large configuration objects like menu definitions outside of the component module scope to prevent unnecessary allocations.
## 2024-08-26 - [Bypass faulty root package.json build script on Render]
**Learning:** The repository's root package.json contains a duplicate scripts block that overwrites the correct build process, causing Render deployments to fail as it fails to copy the dist folder properly.
**Action:** When restricted from modifying package.json, explicitly instruct the user to configure the Build Command and Publish Directory in the Render Dashboard to bypass the faulty scripts.
