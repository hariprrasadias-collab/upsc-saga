# Comprehensive Sidebar Menus Testing & Fixing Plan

## 1. Goal Description
The objective is to fix all breaking features across the 44 sidebar menus in the application and implement comprehensive frontend and backend tests for every functionality and possible scenario to prevent future regressions.

## 2. Scope & Discovery
From `frontend/src/components/Sidebar.tsx`, the following 44 menus were discovered:
- **Standalone:** Dashboard, Analytics, Weak Areas
- **Planning:** Study Plan, War Map, Triangulation History, Syllabus, Quests, Revision Cards, Mnemonics, Mind Map, Mind Palace, Revision Center, Time Boxing, The Golden Path
- **Training:** Anki Dojo, Answer Writing, The Scribe, Socratic History, Mock Tests, Boss Arena, Essay Workshop, CSAT Prep, Project Foresight
- **Knowledge:** Mimir, Brain Vault, Flashcards, The Seer, The Ravens, Compilation, PYQ, Heatmap, Model Answers, Codex, Lore Tablets, Watchman
- **Enhancement:** Armory, Panopticon, Neural Hash
- **Admin:** Admin Control Panel

## 3. Proposed Changes (Agent Orchestration)

### Phase 1: Planning (Completed via this document)
- `project-planner` and `explorer-agent` mapped all routes and established the strategy.

### Phase 2: Implementation (Parallel Execution - Post Approval)

#### Group 1: Foundation
- **`database-architect`**: Audit schema to ensure all 44 features have robust database backing without integrity errors.
- **`security-auditor`**: Enforce correct authentication and rate-limiting across all related API endpoints.

#### Group 2: Core Fixing
- **`backend-specialist`**: Fix crashing or inconsistent API routes. Ensure every route returns the standardized `{ success, data, error }` JSON envelope. Prevent 500 errors on missing data.
- **`frontend-specialist`**: Fix UI crashes. Ensure all 44 components safely unwrap the `data` envelope and handle loading/error states gracefully.

#### Group 3: Comprehensive Testing
- **`test-engineer`**: 
  - **Backend:** Write Pytest integration and unit tests for *every* blueprint (`test_dashboard.py`, `test_syllabus.py`, etc.), covering edge cases and invalid inputs.
  - **Frontend:** Write Playwright E2E tests for the Sidebar navigation and critical user flows for each of the 44 modules. Setup React Testing Library tests for individual component rendering and state changes.

## 4. Verification Plan
- **Automated Tests:** Execute the full Pytest suite (`pytest tests/`) and Playwright E2E tests (`npx playwright test`).
- **Scripts:** Run `checklist.py` (Security, Lint, Schema, UX, SEO) to ensure 100% compliance.
- **Manual Verification:** Manually click through all 44 sidebar items to ensure rendering and lack of console errors.

## User Review Required
> [!IMPORTANT]
> This is a massive scope covering 44 distinct features. Implementing exhaustive tests for all 44 modules will take significant time. Do you approve this orchestration plan? (Y/N)
> - Y: Proceed with Phase 2 (Invoking specialized agents in parallel).
> - N: Provide feedback for plan adjustment.
