## 2025-03-08 - [Batch Analytics Dates with UNION]
**Learning:** SQLite data aggregations (like UNION) are significantly more performant than running multiple individual SELECT queries and deduplicating in Python memory, specifically avoiding the fetching of thousands of rows into Python sets.
**Action:** Use a single UNION query to extract and aggregate unique elements from multiple tables when calculating aggregations like streak days.
