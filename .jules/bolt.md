# Bolt's Journal

## 2024-05-22 - [Example Entry]
**Learning:** This is an example entry.
**Action:** Use this format for future entries.

## 2024-05-22 - [Syllabus Payload Optimization]
**Learning:** `SELECT *` in listing endpoints can implicitly fetch large text columns (like `notes`), causing massive payload bloat. In this case, removing `notes` reduced payload size by ~90%.
**Action:** Always audit `SELECT *` in list views. Explicitly select columns or exclude large text fields until detail view is requested.
