## 2024-05-24 - Custom Debounce to Avoid Dependency Addition
**Learning:** To satisfy the strict constraint of not adding new dependencies without permission, standard utilities like `use-debounce` cannot be used out-of-the-box.
**Action:** Implement simple utilities (like a custom hook or an inline `useEffect` with `setTimeout`) manually using built-in React hooks to avoid modifying package configurations and triggering lockfile updates or dependency warnings.
