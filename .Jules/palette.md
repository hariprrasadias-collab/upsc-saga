## 2026-08-15 - Adding ARIA labels to icon buttons

**Learning:** When reviewing `frontend/src/components/PomodoroTimer/PomodoroTimer.tsx`, several icon-only buttons (like Fullscreen, History, Settings, Minimize, Save, Cancel, Edit Timer) were missing `aria-label`s, which is problematic for screen reader accessibility since the buttons only contain emojis or symbols.

**Action:** Ensure that all icon-only buttons receive descriptive `aria-label` attributes to explicitly announce their purpose to screen reader users, even if they have a `title` attribute, as `aria-label` is more consistently announced by assistive technologies.

## 2026-08-15 - Handling missing module in tests

**Learning:** Running `pnpm exec vitest run` in the `frontend` folder currently fails due to a missing `/app/frontend/src/setupTests.ts` file. Pre-existing lint and test errors can be ignored safely if our change is unrelated.

## 2026-08-15 - Fixing deployment issues

**Learning:** When trying to fix an issue where a PR was rejected from Render, we can modify `package.json` to have build point to `pnpm run build` and remove the duplicate `scripts` object and unused `_isUpscale` in `VisualPromptRenderer.tsx`.
