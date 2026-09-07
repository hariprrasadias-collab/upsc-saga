## 2025-01-20 - [Debounce Search Inputs]
**Learning:** The React application was issuing an API call on every keystroke when filtering PYQ data and Ravens articles, creating unnecessary load and UI latency.
**Action:** Created and utilized a custom `useDebounce` hook to delay execution until 300ms after the last keystroke, preventing spamming of the `searchQuery` endpoints.
