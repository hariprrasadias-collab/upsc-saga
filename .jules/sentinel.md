## 2026-05-03 - DOMPurify with React safely rendering HTML
**Vulnerability:** XSS vulnerability through improperly sanitizing input into dangerouslySetInnerHTML.
**Learning:** In a pnpm environment, installing dependencies can sometimes create or update npm's package-lock.json if not careful with commands or defaults. Also, dompurify inherently provides its own types; installing @types/dompurify creates conflict or unnecessary bloat.
**Prevention:** Use DOMPurify.sanitize(input) inside dangerouslySetInnerHTML. Be explicit with pnpm commands in pnpm workspaces, and do not arbitrarily add type stubs for packages that don't need them.
