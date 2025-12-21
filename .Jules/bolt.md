## 2024-05-23 - React List Rendering Performance
**Learning:** Inline rendering of large lists (e.g., `{items.map(item => <div key={item.id}>...</div>)}`) causes the entire list to re-render when the parent component updates, even if only one item changed. This is a significant bottleneck for large datasets like the UPSC syllabus tree.
**Action:** Extract list items into separate components wrapped in `React.memo`. Ensure event handlers passed to them are stable (wrapped in `useCallback`) and that state updates preserve object references for unchanged items.
