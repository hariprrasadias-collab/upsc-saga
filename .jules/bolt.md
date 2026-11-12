## 2024-05-19 - [CommandPalette Commands Memoization]
**Learning:** The `commands` array in `CommandPalette.tsx` was being recreated on every render, causing the `filteredCommands` useMemo to re-evaluate and the `useEffect` handling keyboard shortcuts to constantly re-bind its event listeners. This was happening every time the query state changed.
**Action:** Wrap the static `commands` array in `useMemo` so its reference is stable across renders, preventing cascading re-evaluations and re-bindings.
