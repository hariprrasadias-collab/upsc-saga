# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-07-30 - [Optimized subject-wise analytics to eliminate N+1 queries]
**Learning:** The `get_subject_wise` analytics route queried subject performance data in a loop, resulting in a series of N+1 database queries. Since each call queried the same tables but filtered to a single subject, this caused unnecessary database overhead.
**Action:** Replace looped individual fetches with a single bulk query using `IN` clauses and `GROUP BY` logic, ensuring independent tables are wrapped in isolated `try...except` blocks to maintain fault tolerance.

## 2026-07-30 - [Fixed TypeScript Unused Variable error causing production build failure]
**Learning:** In frontend TypeScript configurations for this codebase, unused variables trigger a strict  error during production builds, failing the compilation.
**Action:** Always run a local production build (
> @ build /app
> cd frontend && npm install && npm run build


up to date, audited 380 packages in 3s

111 packages are looking for funding
  run `npm fund` for details

19 vulnerabilities (1 low, 4 moderate, 13 high, 1 critical)

To address issues that do not require attention, run:
  npm audit fix

To address all issues (including breaking changes), run:
  npm audit fix --force

Run `npm audit` for details.

> frontend@0.0.0 build
> npm install && tsc -b && vite build


up to date, audited 380 packages in 2s

111 packages are looking for funding
  run `npm fund` for details

19 vulnerabilities (1 low, 4 moderate, 13 high, 1 critical)

To address issues that do not require attention, run:
  npm audit fix

To address all issues (including breaking changes), run:
  npm audit fix --force

Run `npm audit` for details.
src/components/Brain/Renderers/VisualPromptRenderer.tsx(250,35): error TS6133: 'isUpscale' is declared but its value is never read.
 ELIFECYCLE  Command failed with exit code 2.
 WARN   Local package.json exists, but node_modules missing, did you mean to install?) before submitting, and fix unused variables by removing them or prefixing them with an underscore (e.g., `_isUpscale`).

## 2025-03-03 - [Fixed TypeScript Unused Variable error causing production build failure]
**Learning:** In frontend TypeScript configurations for this codebase, unused variables trigger a strict `TS6133` error during production builds, failing the compilation.
**Action:** Always run a local production build (`NODE_ENV=production pnpm build`) before submitting, and fix unused variables by removing them or prefixing them with an underscore (e.g., `_isUpscale`). Also verify `package.json` build scripts don't hardcode `npm` commands.
