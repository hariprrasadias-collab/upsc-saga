## 2024-05-24 - N+1 Query in Pie Chart Trends
**Learning:** Found an N+1 query loop in `backend/app/routes/seer.py` where pie chart trends fetched counts in a loop across years and subjects, resulting in many single queries. A single GROUP BY statement easily eliminated this bottleneck, taking 0.0013s compared to 0.0019s.
**Action:** Consolidate iterative queries involving identical parameters by using single `GROUP BY` statements when iterating over nested rows to significantly speed up analytics aggregation.
