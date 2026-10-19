## 2026-10-18 - [O(N) Map Lookup for Repeated Array Finds]
**Learning:** In StudyPlanDashboard, repeatedly using .find() inside .sort() loops leads to severe performance degradation as the array size grows. Replacing repeated .find() with an O(1) Map lookup dramatically speeds up sorting for large datasets.
**Action:** Pre-calculate lookups using Map when traversing structures used multiple times later, especially inside tight loops like .sort().
