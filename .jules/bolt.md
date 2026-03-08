## 2025-03-08 - [Batch Analytics Dates with UNION]
**Learning:** SQLite data aggregations (like UNION ALL) are significantly more performant than running multiple individual SELECT queries and deduplicating/updating in Python memory, specifically avoiding 5 independent O(N) database round-trips.
**Action:** Use a single UNION/UNION ALL query to extract and aggregate unique elements from multiple tables when calculating aggregations like streak days.
