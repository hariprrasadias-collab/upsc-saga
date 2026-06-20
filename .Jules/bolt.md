# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Eliminate N+1 UPDATE queries in mock tests]
**Learning:** In the mock tests grading route, individual `UPDATE` statements were executed in a loop over test questions, creating an N+1 query bottleneck.
**Action:** Lift `UPDATE` logic out of loops. Accumulate parameters into a list during iteration and use a single `executemany()` operation to batch the updates, reducing database roundtrips to just two queries.

## 2025-03-03 - [Fix production CSS minification error]
**Learning:** In the frontend, the deployment failed during the vite production build (`vite:css-post` / `lightningcss minify`) because of an `Unexpected }` error. I discovered that duplicate CSS code blocks had been pasted into `frontend/src/components/DashboardMain/RevisionWidget.css` which broke the CSS structure and caused the minifier to crash.
**Action:** Always check the full file using `grep` or `sed` for missing braces or duplicates when a CSS build fails with unexpected braces. Removed the duplicated blocks.
