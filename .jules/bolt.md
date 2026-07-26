## 2024-07-26 - Optimized Data Aggregation in Analytics
**Learning:** Fetching large, unaggregated datasets (like all user activity dates) from SQLite and grouping them in Python creates an O(N) memory and processing bottleneck.
**Action:** Pushed aggregation to the database using `GROUP BY date, COUNT(*) as count`. This reduces data transfer to O(1) relative to total items, making operations like heatmap generation significantly faster and more memory-efficient.
