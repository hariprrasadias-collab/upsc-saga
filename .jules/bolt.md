## 2024-03-24 - React Context setState Cascading Renders
**Learning:** Found cascading renders triggered by synchronous `setState` calls inside `useEffect` during timer completion (`setTimeLeft` triggering `handleTimerComplete` which calls `setIsRunning(false)` and `setSessionsCompleted`).
**Action:** Push the timer completion callback to the next tick using `setTimeout(() => handleTimerComplete(), 0)` or initialize state properly with a factory function to avoid initial redundant state updates.
