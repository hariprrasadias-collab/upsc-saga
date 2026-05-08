## 2026-05-08 - Optimize Arena Bosses Loading
**Learning:** The 'get_available_bosses' endpoint in the arena system exhibited an N+1 query problem by fetching distinct years/subjects and subsequently querying the database for counts iteratively in a loop using 'get_boss_stats'.
**Action:** Always fetch aggregate data upfront using 'GROUP BY' and pass the precalculated values down to helper functions to avoid redundant database calls inside loops.
