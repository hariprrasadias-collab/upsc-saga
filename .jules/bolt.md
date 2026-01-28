## 2024-05-22 - [Repeated SQL in Loops]
**Learning:** Found an O(N) query pattern in `analytics.py` where constant data (syllabus progress) was re-queried for every day in a trend projection loop. This is likely due to a lack of historical data tables, forcing the backend to "project" current state across the timeline.
**Action:** When implementing trend endpoints without historical tables, calculate the current state *once* and project it in memory, rather than re-querying the DB in the loop. Always check for loop-invariant database queries.
