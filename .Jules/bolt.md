# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2024-03-01 - N+1 Queries in Time-Series Mock Data
**Learning:** The `syllabus_topics` table only tracks current status without historical records. Analytics routes like `get_progress_trend` run loops over dates but execute identical queries because the underlying data lacks temporal resolution, leading to O(n) redundant database queries.
**Action:** When generating time-series data for tables without historical tracking, fetch the aggregate counts once outside the date loop to avoid redundant database calls.
