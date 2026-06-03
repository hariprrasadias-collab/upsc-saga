
## 2024-06-02 - Batched Backend Analytics Queries
**Learning:** In the `get_subject_wise` endpoint, looping to fetch metrics per subject generated an N+1 query problem. Extracting the multiple independent queries into bulk `GROUP BY` operations with `IN` clauses solved it, significantly improving local response times. Each bulk query must be wrapped in its own `try...except` to protect the successful queries from failing ones (e.g. if a table is missing).
**Action:** Always batch repeated identical DB queries into a single query using `IN` and `GROUP BY` when fetching analytics for lists, and defensively isolate queries that touch independent tables.
