## 2026-01-31 - Build Tool Dependencies in CI
**Learning:** Deployment platforms like Render often set `NODE_ENV=production`, causing `npm install` (or `pnpm`) to skip `devDependencies`. If build tools like `vite`, `typescript`, or `@vitejs/plugin-react` are in `devDependencies`, the build script (`tsc -b && vite build`) will fail with "command not found".
**Action:** Always move build-critical tools (vite, typescript, build plugins) to `dependencies` in `package.json` for projects deployed on such platforms, unless you explicitly configure the build environment to install dev dependencies.
