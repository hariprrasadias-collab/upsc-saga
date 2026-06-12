# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-06-12 - [Batch question insertion to eliminate N+1 queries]
**Learning:** The `create_test` endpoint in `backend/app/routes/mock_tests.py` inserted questions in a loop, resulting in a database query for each question.
**Action:** When inserting multiple rows into a database, always use `executemany` with a list of tuples to batch the inserts and avoid N+1 query bottlenecks.

## 2024-06-12 - [TS6133 Unused Variable Compilation Error]
**Learning:** During strict TypeScript builds, variables defined but not used (e.g. `isUpscale` in a React component) will cause `error TS6133` which fails the production build process.
**Action:** Always rename unused parameters by prepending an underscore (e.g. `_isUpscale`) to safely bypass the compiler error and unblock the build without altering logic.

## 2024-06-12 - [Render Deployment: Duplicate scripts in package.json]
**Learning:** If a Render deployment fails with 'Publish directory dist does not exist!' despite the frontend build succeeding, it might be due to a duplicate `scripts` block in the root `package.json` that overrides the correct build script (which properly copies the artifacts).
**Action:** Remove the duplicate/incorrect `scripts` block in `package.json` so the correct build command executes.
