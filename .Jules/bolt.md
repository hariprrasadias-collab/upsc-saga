## 2024-05-30 - N+1 database queries during loop iterations
**Learning:** Found N+1 database updates and inserts inside loops in `backend/app/routes/mock_tests.py` causing performance bottlenecks, particularly when dealing with many questions or answers. For example, `submit_attempt` looped over each question and ran an individual `conn.execute('UPDATE ...')` query, and `create_test` looped over questions and ran `conn.execute('INSERT ...')`.
**Action:** Use `.executemany()` outside of loops for bulk database operations to drastically reduce query execution time. Accumulate updates or inserts into lists and execute them once.

## 2024-05-30 - LightningCSS and Nested Keyframes
**Learning:** Vite's LightningCSS minifier throws `SyntaxError: [lightningcss minify] Unknown at rule: @keyframes` during production builds if `@keyframes` are nested inside other CSS selectors.
**Action:** Always define `@keyframes` at the top level of the CSS file to avoid build failures. Extracted all nested `@keyframes` to the root level.
