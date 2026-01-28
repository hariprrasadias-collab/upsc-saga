## 2025-10-26 - Optimistic UI for High-Frequency Interactions
**Learning:** For rapid-fire user interactions like flashcard reviews, waiting for server confirmation (even <100ms) breaks flow. Optimistic UI updates are essential here.
**Action:** When implementing "next item" flows, always update UI state immediately and sync with backend in background, unless data integrity is critical for the *immediate* next step.

## 2025-10-26 - Frontend Test Configuration
**Learning:** The frontend `vitest` configuration was picking up Playwright E2E tests (`tests/`), causing failures.
**Action:** Ensure `vitest.config.ts` explicitly includes only unit tests (e.g., `src/**/*.test.tsx`) to avoid conflict with E2E suites.
