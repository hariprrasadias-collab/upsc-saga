## 2024-06-03 - Batching Analytics Queries
**Learning:** The `get_subject_wise` endpoint originally caused an N+1 query problem by iterating over subjects and executing three separate queries for each, resulting in 18 queries.
**Action:** Always utilize `GROUP BY` and an `IN` clause to aggregate metrics for all items in batched queries, avoiding database round trips in loops.
