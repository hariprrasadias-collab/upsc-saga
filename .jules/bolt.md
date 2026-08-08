## 2024-05-18 - [Time Distribution Group By]
**Learning:** Found N+1 query issue in heatmap data fetching logic where we manually grouped by dates. Can offload the group by to SQL.
**Action:** Always prefer SQL Group By and aggregations instead of processing large datasets in Python memory.
