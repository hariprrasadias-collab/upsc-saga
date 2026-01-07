## 2024-05-23 - [Sanitization without Bleach]
**Vulnerability:** XSS vulnerability found in AnkiDojo where `dangerouslySetInnerHTML` consumed potentially unsafe HTML from an Anki instance.
**Learning:** `bleach` was not available in the environment, and adding dependencies was restricted. I had to implement a custom whitelist-based sanitizer using Python's standard `html.parser`.
**Prevention:** Use the `WhiteListSanitizer` class in `backend/app/utils/security.py` for any future rich text sanitization needs where `bleach` is unavailable. It strictly whitelists safe tags/attributes and strips dangerous ones like `<script>` and `javascript:`.

## 2024-05-23 - [Full-Stack Build Dependencies]
**Vulnerability:** A backend security fix triggered a full-stack deployment failure due to latent frontend TypeScript errors and build configuration issues.
**Learning:** In a monorepo or full-stack deployment (like Render), even isolated backend changes can fail if the frontend doesn't build cleanly. The frontend build process enforces strict type checking (`tsc -b`).
**Prevention:** Always verify the full build pipeline (`pnpm build` in frontend) before pushing changes, even if they seem backend-only. Ensure unused variables and imports are cleaned up as they cause build failures in strict mode.

## 2024-05-23 - [Runtime Dependency Missing]
**Vulnerability:** `beautifulsoup4` was used in backend code but missing from `requirements.txt`.
**Learning:** Even if local dev works (due to pre-installed packages), Render builds fail if dependencies aren't explicit.
**Prevention:** Always check `requirements.txt` when adding new imports.
