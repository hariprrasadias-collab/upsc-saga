## 2024-05-18 - [Add ARIA labels to close buttons]
**Learning:** Adding ARIA labels to close buttons significantly improves accessibility for screen readers.
**Action:** Always add aria-label="Close" or similar to 'x' buttons.
## 2024-05-18 - Make interactive divs accessible
**Learning:** Custom interactive elements (like `div`s with `onClick`) are completely invisible to keyboard navigation. This breaks accessibility for a significant portion of users.
**Action:** Always add `role="button"`, `tabIndex={0}`, and an `onKeyDown` handler (supporting 'Enter' and ' ') to custom interactive elements.
