## 2024-05-23 - Accordion Header Pattern
**Learning:** Using `div`s for accordion headers breaks accessibility by lacking `aria-expanded` and keyboard support.
**Action:** Replace with `<button>`, reset styles (`width: 100%`, `text-align: left`, `border: none`), and add `aria-expanded`/`aria-controls` for full accessibility.
