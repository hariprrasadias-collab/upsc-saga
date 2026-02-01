## 2024-05-23 - Analytics History Projection
**Learning:** The `get_progress_trend` endpoint projects *current* syllabus status across historical dates because the `syllabus_topics` table lacks historical state tracking. This resulted in redundant O(N) queries returning the exact same data.
**Action:** When working on trend analytics, verify if the underlying data actually supports historical tracking. If not (and projection is used), ensure the query is executed once (O(1)) rather than per-day (O(N)).
