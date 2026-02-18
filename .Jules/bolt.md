# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2024-05-23 - Incorrect Schema Assumptions
**Learning:** Code referenced `answer_questions` table which doesn't exist (correct name is `answer_writing_prompts`), causing silent failures in analytics due to broad exception handling.
**Action:** Verify schema using `sqlite3 .schema` before optimizing queries, especially when try/except blocks mask errors.
