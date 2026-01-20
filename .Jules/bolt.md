# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.
## 2024-05-23 - Lazy Loading Syllabus Notes
**Learning:** Large text columns (like 'notes') in frequently accessed list endpoints can significantly bloat payload size. Explicitly excluding them and fetching on demand is a high-impact optimization.
**Action:** Audit all list endpoints for 'heavy' columns and implement lazy loading where appropriate.
