## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2026-06-04 - Remove hardcoded OpenClaw API Key
**Vulnerability:** Hardcoded API key for OpenClaw found as a fallback in `os.environ.get`.
**Learning:** Hardcoding credentials as fallbacks exposes them to version control, undermining environment variable protections.
**Prevention:** Always rely strictly on environment variables for sensitive credentials, ensuring no fallback values are hardcoded in the source code.
## 2026-06-04 - Fix TS6133 frontend build failure
**Vulnerability:** Unused parameter `isUpscale` caused strict TypeScript compilation failures during Render production deployments.
**Learning:** The build step `tsc -b` runs strictly; unused parameters fail the build and block deployments. Prefixing unused parameters with an underscore (`_isUpscale`) satisfies strict configurations.
**Prevention:** Always run `NODE_ENV=production npm run build` locally to verify typescript compilation before committing.
## 2026-06-04 - Fix duplicate build script overriding package.json dependencies
**Vulnerability:** A duplicate `scripts` block in the root `package.json` overrode the primary build configuration, silently stripping out the `--include=dev` flag during production builds.
**Learning:** JSON parses the last occurrence of a key. Duplicate keys in configuration files can cause critical CI/CD build scripts to fail silently by executing unintended or incomplete commands, leading to missing dependencies in production environments.
**Prevention:** Validate JSON configuration files to ensure no duplicate keys exist, and consolidate related configurations (like `scripts`) into a single object block.
