## 2024-05-23 - [N+1 Query in Year Trends API]
**Learning:** Using a loop to run aggregate queries for each item (e.g., year) results in N+1 database calls, which is a performance bottleneck.
**Action:** Always prefer a single `GROUP BY` SQL query and group the data in memory for backend APIs.
