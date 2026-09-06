
## 2024-05-22 - [Optimizing Static Objects in React Components]
**Learning:** When optimizing static objects in React components, do not wrap them in `useMemo` as it introduces unnecessary hook overhead. Instead, hoist the static object completely outside the component module scope to prevent reallocation on every render.
**Action:** Move static objects outside the React component completely.

## 2025-03-03 - [Optimizing function references]
**Learning:** Extract functions that don't depend on component scope to standalone components or hooks instead of just `useCallback`. This reduces re-creation overhead.
**Action:** Extract functions to standalone components and hoist static configs.
