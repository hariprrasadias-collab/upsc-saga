## 2024-05-18 - Fault Tolerance in Batch Endpoints
**Learning:** When replacing iterative function calls with bulk SQL queries across multiple independent tables, a database failure in one table (e.g., table not existing yet) can halt the entire endpoint if not isolated.
**Action:** Always wrap each table's bulk query in its own isolated try...except block to preserve fault tolerance and ensure partial data is still returned.
