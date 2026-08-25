## 2024-05-25 - [Optimize Decorative Elements]
**Learning:** Decorative components placed high in the tree (like App.tsx) can cause O(N) re-renders across all child elements without memoization.
**Action:** Use React.memo and useMemo for decorative global components to prevent unnecessary cascading re-renders during unrelated state changes.
