## 2024-10-24 - Performance Optimization
**Learning:** The 'get_progress_trend' endpoint has an N+1 query issue where it executes 60 queries for a 30-day trend, resulting in a flat line due to ignoring historical state.
**Action:** Replace the loop of queries with a single aggregation query and reconstruct history in memory using 'last_updated' timestamps.
