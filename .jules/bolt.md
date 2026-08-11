## 2025-08-11 - Database Aggregation for UNION ALL queries
**Learning:** Fetching raw `UNION ALL` records into Python memory to count them manually creates an O(N) memory and data transfer bottleneck, particularly for high-volume activity routes like heatmap time-distributions.
**Action:** Always wrap `UNION ALL` queries in a subquery and apply a SQL `GROUP BY` clause (e.g., `SELECT date, COUNT(*) FROM (...) GROUP BY date`) to shift the aggregation workload to SQLite before returning rows to Python.
