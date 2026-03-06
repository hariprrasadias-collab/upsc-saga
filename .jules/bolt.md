## 2024-05-20 - [Offload Data Aggregation to SQLite]
**Learning:** Using Python to perform data aggregation (like finding unique active dates across multiple tables via loops and `set()`) causes huge memory overhead and slow response times when dealing with thousands of rows in SQLite.
**Action:** Always prefer pushing `UNION` and `COUNT(DISTINCT)` logic directly to the database query rather than transferring raw records across the SQLite-Python boundary. It reduces Python RAM overhead and leads to 35-50% speedups.
