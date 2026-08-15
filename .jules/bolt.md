## 2024-05-18 - [Optimize UNION ALL with GROUP BY]
**Learning:** In SQLite, when fetching records from multiple tables with `UNION ALL` to aggregate counts, retrieving all the raw rows and aggregating them in Python causes O(N) memory and data transfer bottlenecks.
**Action:** Wrap the `UNION ALL` subqueries in a `SELECT ... GROUP BY` statement, letting SQLite perform the counting operations, which is significantly faster and reduces memory overhead.
