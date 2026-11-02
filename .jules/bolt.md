## 2024-05-24 - [React.memo on AshParticles]
**Learning:** In a highly interactive app where global contexts trigger frequent re-renders at the root level (like App.tsx), pure visual components with many DOM nodes should be strictly memoized. `AshParticles` renders 50 distinct DOM elements and re-rendered on every sidebar toggle or tab change because it lacked memoization.
**Action:** Always wrap purely visual/decorative components that render multiple elements in `React.memo` if they are placed high in the component tree alongside frequently changing state.
