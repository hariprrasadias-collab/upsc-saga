## 2024-05-24 - Custom Modal Dialog Accessibility
**Learning:** Custom modal dialogs must use `role="dialog"` and `aria-modal="true"`. Furthermore, they must have an accessible name using `aria-labelledby` referencing the dialog's heading to be properly announced by screen readers. Visible text cues like `&times;` in close buttons should be wrapped in an `aria-hidden="true"` span to prevent confusing screen reader announcements.
**Action:** Always test custom modals with screen reader constraints in mind, linking titles with container `aria-labelledby` attributes and hiding decorative characters.

## 2024-05-24 - Frontend Build Error on Strict TS
**Learning:** In the frontend, strict TypeScript compilation during `pnpm build` will fail on unused variables (error TS6133).
**Action:** Prefix intentionally unused variables with an underscore (e.g., `_variableName`) to bypass this error.

## 2024-05-24 - Strict TS Tooltip Render Failure
**Learning:** Recharts Tooltip formatter parameters can throw TS2322 in strict type environments (e.g., Render deploys) when assigned explicit primitives like `string | undefined` vs Recharts' internal `NameType`.
**Action:** Always type Recharts formatter variables as `any` (e.g. `(value: any, name: any)`) when custom parsing values.
