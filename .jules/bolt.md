## 2024-05-13 - Optimize Seer Trends API
**Learning:** Found an N+1 query issue in the get_year_trends endpoint. The endpoint was querying the DB for subjects and their counts for each year iteratively. This leads to poor performance on larger databases.
**Action:** Replace the iterative queries with a single GROUP BY query, then use an in-memory dictionary to aggregate the data efficiently.
