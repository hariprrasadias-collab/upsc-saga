## 2024-05-23 - Frontend List Optimization
**Learning:** Large lists in React can cause significant performance degradation if individual items are not memoized, especially when the parent component re-renders frequently (e.g., due to state updates that affect the list structure or unrelated child components).
**Action:** When rendering large lists where items have stable identities and props, always extract the list item into a separate component and wrap it in `React.memo` to prevent unnecessary re-renders of unchanged items.
