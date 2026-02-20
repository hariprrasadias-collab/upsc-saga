# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2026-02-20 - Analytics Loop Inefficiency
**Learning:** Analytics endpoints that iterate over date ranges often recalculate state-invariant metrics (like current syllabus completion) inside the loop, causing N+1 query performance issues.
**Action:** Lift state-invariant queries outside of loops to calculate once and reuse the value.

## 2026-02-20 - Render Build Dependency Pruning
**Learning:** Render sets `NODE_ENV=production` by default, which causes `npm install` to skip `devDependencies`. This breaks builds if tools like `vite` or `typescript` are only in `devDependencies`.
**Action:** Ensure all build-time dependencies (e.g., `vite`, `typescript`, `@types/*`) are listed in `dependencies` in `package.json`.
