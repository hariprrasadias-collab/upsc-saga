## 2026-10-12 - [O(N) Render Optimization]
**Learning:** Re-computing `.filter()` and `.reduce()` inline inside React map functions creates O(N*M) time complexity during renders, causing performance degradation when arrays are large.
**Action:** Use `useMemo` to pre-compute group dictionaries in O(N) time for O(1) rendering lookups.
