# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-09 - [SQLite Aggregation over Python Loop in Flashcard Context]
**Learning:** In the `get_brain_context` logic of `FlashcardService`, pulling all flashcard reviews and iterating through them with `datetime.fromisoformat` and Python conditionals was causing an unnecessary O(N) memory and processing overhead. Running `fetchall()` and processing thousands of records via Python was slower than offloading data aggregation and condition checks directly to the SQLite query engine. Using SQL aggregate functions like `COALESCE(SUM(CASE WHEN ...))` paired with a Common Table Expression (`WITH`) is 3-4x faster for larger datasets.
**Action:** In SQLite-backed backend services, push data aggregation and `COUNT`/`SUM` logic directly into the database query rather than iterating over result sets in Python memory. This approach conforms to the overarching memory guideline: "For performance, push data aggregation (e.g., UNION, COUNT(DISTINCT)) directly to SQLite queries instead of fetching datasets into Python memory."

## 2025-03-09 - [Render Deployment: package.json script execution crash]
**Learning:** During deployment to Render, invoking `npm install && npm run build` recursively inside a child `package.json` file when the main project uses pnpm resulted in a crash and `npm` destructuring error logs, likely due to an internal package manager discrepancy when deployed via a root `pnpm` command. Additionally, TS strict mode `noUnusedLocals` (TS6133) can break production builds if variables are merely commented out or bypassed without prefixing an underscore (e.g. `_isUpscale`). Finally, having multiple `"scripts"` keys in the same `package.json` quietly overwrites previous script definitions, which completely broke Render's root build delegate script.
**Action:** When troubleshooting Render builds, ensure sub-package build scripts strictly contain build logic (`tsc && vite build`) without recursive `npm install` prefixes. Fix TypeScript strict mode warnings (by either removing or using `_`) explicitly instead of ignoring them. Always verify `package.json` for duplicate top-level keys.

## 2025-03-09 - [Balancing SQL Aggregation with Domain Logic in Flashcards]
**Learning:** While offloading data aggregation (like `due_count`) directly to SQLite queries provides immense performance benefits (O(1) database execution vs O(N) Python iteration), blindly translating complex domain functions into SQL logic is dangerous. In `FlashcardService`, trying to replicate `get_card_maturity(alpha, beta, halflife)` natively in a SQL query using just `halflife` hard-coding created a severe functional regression by ignoring the `alpha` and `beta` parameters essential to the Ebisu SRS algorithm.
**Action:** When optimizing performance bottlenecks via SQLite, use a "mixed approach" when complex domain logic is involved. Compute standard counts and time-based metrics natively in SQL, but for domain-specific algorithms, return only the minimal required rows (`alpha`, `beta`, `halflife`) and execute the strict domain function in Python. This preserves correct behavior while still yielding substantial performance gains.
