## 2024-06-25 - [SQL UNION ALL Aggregation Optimization]
**Learning:** To resolve O(N) memory and data transfer bottlenecks when counting or aggregating records combined from multiple tables using `UNION ALL`, wrap the `UNION ALL` queries in a subquery and apply a SQL `GROUP BY` clause (e.g., `SELECT date, COUNT(*) FROM (...) GROUP BY date`) to shift the aggregation workload to the database.
**Action:** Always check `UNION ALL` aggregations and offload row-level counting to the DB engine.
