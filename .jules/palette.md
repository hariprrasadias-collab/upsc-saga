## 2024-10-24 - Accessibility Refactoring Pitfalls
**Learning:** When replacing `div`s with semantic `<button>` elements for accessibility, `color: inherit` is critical in CSS resets. Browsers default buttons to black text, which breaks dark mode designs instantly if missed.
**Action:** Always include `color: inherit; font-family: inherit; font-size: inherit; background: transparent; border: none;` when making custom semantic buttons.
