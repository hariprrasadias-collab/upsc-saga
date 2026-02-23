# 🧠 UPSC Second Brain — The Complete Reference

> A full-stack, AI-powered UPSC Civil Services exam preparation platform built with Flask (backend) and React/TypeScript (frontend). It combines deep gamification, multi-provider LLM integration, Spaced Repetition, and 40+ study modules into a single "second brain" for aspirants.

---

## 📑 Table of Contents

1. [Project Philosophy](#1-project-philosophy)
2. [Tech Stack](#2-tech-stack)
3. [Repository Structure](#3-repository-structure)
4. [Quick Start — Local Development](#4-quick-start--local-development)
5. [Environment Variables](#5-environment-variables)
6. [Backend Deep Dive](#6-backend-deep-dive)
   - [App Factory & Blueprints](#61-app-factory--blueprints)
   - [Database Models](#62-database-models)
   - [Routes Reference](#63-routes-reference)
   - [Services Layer](#64-services-layer)
   - [AI & Model Manager](#65-ai--model-manager)
   - [The Brain — Central Nervous System](#66-the-brain--central-nervous-system)
   - [Hephaestus — Self-Healing System](#67-hephaestus--self-healing-system)
   - [Gamification Engine](#68-gamification-engine)
7. [Frontend Deep Dive](#7-frontend-deep-dive)
   - [Application Shell](#71-application-shell)
   - [Global State & Contexts](#72-global-state--contexts)
   - [Feature Modules](#73-feature-modules)
8. [Feature Reference A–Z](#8-feature-reference-az)
9. [Database Schema Overview](#9-database-schema-overview)
10. [Migration Scripts](#10-migration-scripts)
11. [Utility & Debug Scripts](#11-utility--debug-scripts)
12. [Docker & Deployment](#12-docker--deployment)
13. [API Endpoints Cheatsheet](#13-api-endpoints-cheatsheet)
14. [Common Issues & Fixes](#14-common-issues--fixes)
15. [Authentication Model](#15-authentication-model)
16. [Adding a New Feature — Step-by-Step](#16-adding-a-new-feature--step-by-step)

---

## 1. Project Philosophy

This app treats UPSC preparation as a **campaign**, not a chore. Every concept:

- **Mythological naming** — *Mimir* (AI oracle), *Ravens* (current affairs), *Yggdrasil* (knowledge tree), *Hephaestus* (self-healing system), *Foresight* (prediction engine), *Panopticon* (biometric tracker), *Night Watchman* (morning brief).
- **Single-user local app** — All routes default to `user_id = 1`. There is **no authentication wall**. It is designed to run on a personal machine, not as a multi-tenant SaaS.
- **AI-first** — The "Brain" module connects every study action (completing a topic, answering a question) to AI generation of flashcards, mock tests, socratic dialogues, triangulations, predictions, and more — automatically.

---

## 2. Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3, Flask, Flask-CORS, Flask-Compress, Flask-Caching |
| **Database** | SQLite (`upsc_saga.db` — main; `upsc_brain.db` — brain artifacts) |
| **AI — Primary** | Google Gemini 2.0 Pro / Flash via `google-generativeai` |
| **AI — Fallback** | OpenRouter (12+ free models), NVIDIA NIM (Llama-3.1, Nemotron) |
| **AI — Consensus** | HYDRA Engine — 3-way draft → critique → synthesis pipeline |
| **Frontend** | React 18, TypeScript, Vite |
| **Routing** | React Router v6 |
| **State** | React Context API (`GlobalContext`, `AnalyticsContext`, `PomodoroContext`) |
| **HTTP** | Fetch API via `config.ts` base URL |
| **Deployment** | Docker Compose (backend on `:5000`, frontend on `:80`) |
| **Production WSGI** | Gunicorn |

### Python Dependencies (`backend/requirements.txt`)

```
flask, gunicorn, google-generativeai, python-dotenv, networkx,
cachetools, scipy, numpy, Flask-Compress, Flask-Caching, flask-cors,
requests, feedparser, google-auth-oauthlib, openai, thefuzz,
google-api-python-client
```

---

## 3. Repository Structure

```
upsc-second-brain/
├── backend/                    # Flask application
│   ├── app/
│   │   ├── __init__.py         # App factory: registers all 40+ blueprints
│   │   ├── db.py               # SQLite connection helper (get_db / close_db)
│   │   ├── cgi_fix.py          # CGI path patch for Windows compat
│   │   ├── db_models/          # Table initialisation (one file per domain)
│   │   ├── routes/             # Flask blueprints (one file per feature)
│   │   ├── services/           # Business logic + AI service layer
│   │   └── utils/              # Shared utilities
│   ├── app.py                  # Entry point (create_app())
│   ├── requirements.txt
│   ├── .env / .env.example
│   ├── upsc_saga.db            # Primary SQLite database
│   ├── fly.toml                # Fly.io deployment config
│   ├── Dockerfile
│   └── [many migrate_*.py, verify_*.py, debug_*.py scripts]
│
├── frontend/                   # React / Vite application
│   ├── src/
│   │   ├── main.tsx            # React root mount
│   │   ├── App.tsx             # Top-level layout + all tab/route mapping
│   │   ├── App.css             # Global styles
│   │   ├── animations.css      # Keyframe animations
│   │   ├── config.ts           # API base URL config
│   │   ├── contexts/           # GlobalContext, AnalyticsContext, PomodoroContext
│   │   ├── components/         # 40+ feature component folders
│   │   ├── services/           # Frontend API service layer
│   │   ├── util/               # Utility helpers
│   │   └── data/               # Static data files
│   ├── index.html
│   └── package.json (Vite + React)
│
├── docker-compose.yml          # Backend :5000, Frontend :80
├── DEPLOY.md                   # Deployment notes
├── DEPLOYMENT_GUIDE.md         # Full deployment guide
├── RAVENS_SETUP.md             # Ravens / current affairs setup
├── walkthrough.md              # Dev walkthrough / history
├── mimir_schedule.csv          # Mimir revision schedule (120k+ rows)
├── database.db                 # Auxiliary SQLite (legacy)
└── [verify_*.py, test_*.py scripts at root]
```

---

## 4. Quick Start — Local Development

### Prerequisites

- Python 3.10+
- Node.js 18+
- A Google Gemini API key (free tier works)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Fill in GEMINI_API_KEY
python app.py                     # Starts on http://localhost:5000
```

> **First run** automatically initialises all SQLite tables via `init_*_tables()` calls in the app factory.

### Frontend

```bash
cd frontend
npm install
npm run dev                       # Starts on http://localhost:5173
```

The frontend proxy calls the backend at `http://localhost:5000` (configured in `src/config.ts`).

---

## 5. Environment Variables

All variables live in `backend/.env` (never committed).

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key — primary AI provider |
| `OPENROUTER_API_KEY` | Optional | Enables 12+ free OpenRouter fallback models |
| `NVIDIA_API_KEY` | Optional | Enables NVIDIA NIM (Llama-3.1-405B, Nemotron) |
| `FLASK_ENV` | Optional | `development` or `production` |
| `SECRET_KEY` | Optional | Flask session secret (defaults to dev key) |

**Without any API key**, the Brain enters **"Lobotomized Mode"** — all AI features return mock responses; the rest of the app (PYQs, flashcards, planner, etc.) still works.

---

## 6. Backend Deep Dive

### 6.1 App Factory & Blueprints

`backend/app/__init__.py` contains `create_app()` which:

1. Initialises Flask, enables CORS (`*`), Gzip compression, rotating file logging.
2. Registers a **global error handler** that triggers `hephaestus.start_background_repair(e)` on any 500 error.
3. Spins a **background thread** on startup to scan logs and auto-repair via Hephaestus.
4. Calls `init_*_tables()` for every domain — safe to call multiple times (CREATE TABLE IF NOT EXISTS).
5. Registers **40+ Flask blueprints**:

| Blueprint | URL Prefix | File |
|-----------|-----------|------|
| `dashboard` | `/api/dashboard` | `routes/dashboard.py` |
| `golden_path` | `/api/golden-path` | `routes/golden_path.py` |
| `tasks` | `/api/tasks` | `routes/tasks.py` |
| `quests` | `/api/quests` | `routes/quests.py` |
| `battles` | `/api/battles` | `routes/battles.py` |
| `shop` (legacy) | `/api/shop` | `routes/shop.py` |
| `shop_new` | `/api/shop-new` | `routes/shop_new.py` |
| `codex` | `/api/codex` | `routes/codex.py` |
| `lore` | `/api/lore` | `routes/lore.py` |
| `mimir` | `/api/mimir` | `routes/mimir.py` |
| `seer` | `/api/seer` | `routes/seer.py` |
| `ravens` | `/api/ravens` | `routes/ravens.py` |
| `anki` | `/api/anki` | `routes/anki.py` |
| `warmap` | `/api/warmap` | `routes/warmap.py` |
| `answer_writing` | `/api/answer-writing` | `routes/answer_writing.py` |
| `watchman` | `/night-watchman` | `routes/watchman.py` |
| `mock_tests` | `/api/mock-tests` | `routes/mock_tests.py` |
| `pyq` | `/api/pyq` | `routes/pyq.py` |
| `syllabus` | `/api/syllabus` | `routes/syllabus.py` |
| `flashcards` | `/api/flashcards` | `routes/flashcards.py` |
| `analytics` | `/api/analytics` | `routes/analytics.py` |
| `essay` | `/api/essay` | `routes/essay.py` |
| `csat` | `/api/csat` | `routes/csat.py` |
| `badges` | `/api/badges` | `routes/badges.py` |
| `challenges` | `/api/challenges` | `routes/challenges.py` |
| `weak_areas` | `/api/weak-areas` | `routes/weak_areas.py` |
| `admin` | `/api/admin` | `routes/admin.py` |
| `predictive` | `/api/predictive` | `routes/predictive.py` |
| `pomodoro` | `/api/pomodoro` | `routes/pomodoro.py` |
| `timebox` | `/api/timebox` | `routes/timebox.py` |
| `planner` | `/api/planner` | `routes/planner.py` |
| `scheduler` | `/api/scheduler` | `routes/scheduler.py` |
| `templates` | `/api/templates` | `routes/templates.py` |
| `revision` | `/api/revision` | `routes/revision.py` |
| `heatmap` | `/api/heatmap` | `routes/heatmap.py` |
| `model_answers` | `/api/model-answers` | `routes/model_answers.py` |
| `issue_mapping` | `/api/issue-mapping` | `routes/issue_mapping.py` |
| `mindmap` | `/api/mindmap` | `routes/mindmap.py` |
| `study_plan` | `/api/study-plan` | `routes/study_plan.py` |
| `compilation` | `/api/compilation` | `routes/compilation.py` |
| `scribe` | `/api/scribe` | `routes/scribe.py` |
| `arena` | `/api/arena` | `routes/arena.py` |
| `socratic` | `/api/socratic` | `routes/socratic_routes.py` |
| `triangulation` | `/api/triangulation` | `routes/triangulation_routes.py` |
| `brain` | `/api/brain` | `routes/brain_routes.py` |
| `autonomy` | `/api/autonomy` | `routes/autonomy_routes.py` |
| `automation` | `/api/automation` | `routes/automation_routes.py` |
| `mind_palace` | `/api/mind_palace` | `routes/mind_palace.py` |
| `foresight` | `/api/foresight` | `routes/foresight.py` |
| `panopticon` | `/api/panopticon` | `routes/panopticon.py` |
| `neural_hash` | `/api/neural_hash` | `routes/neural_hash.py` |
| `interview` | `/api/interview` | `routes/interview.py` |

---

### 6.2 Database Models

All tables are SQLite, defined in `backend/app/db_models/`:

| File | Tables Created |
|------|---------------|
| `core.py` | `users`, `user_stats` |
| `tasks.py` | `tasks` |
| `study_plan.py` | `study_plans`, `study_plan_tasks`, `study_goals` |
| `autonomous_brain.py` | `brain_memory`, `brain_actions`, `brain_lessons`, `synapse_registry` |
| `gamification.py` | `xp_events`, `badges`, `achievements`, `challenges`, `quests`, `shop_items`, `user_inventory`, `hack_silver` |
| `flashcards.py` | `decks`, `flashcards`, `flashcard_reviews` |
| `answer_writing.py` | `answer_writing_prompts`, `user_answers`, `answer_evaluations` |
| `revision.py` | `revision_cards`, `mnemonics_history` |
| `syllabus.py` | `syllabus_topics`, `topic_progress` |
| `mock_tests.py` | `mock_tests`, `test_questions`, `test_attempts`, `test_responses` |
| `mind_palace.py` | `mind_palace_rooms`, `palace_items`, `palace_journeys` |
| `night_watchman.py` | `watchman_briefs`, `watchman_tasks`, `watchman_rituals` |
| `panopticon.py` | `panopticon_logs`, `bio_metrics` |
| `foresight.py` | `foresight_predictions` |
| `neural_hash.py` | `neural_hash_log` |
| `automation_storage.py` | `socratic_dialogues`, `triangulation_archive`, `ai_content_store`, `foresight_store` |
| `current_affairs.py` | `ravens_articles`, `ravens_feeds`, `issue_mappings`, `csat_topics`, `csat_questions` |
| `indexes.py` | Performance indexes across key columns |

**Database file location**: `backend/upsc_saga.db` (primary), `backend/upsc_brain.db` (brain artifacts).

---

### 6.3 Routes Reference

Key route files and what they expose:

#### `routes/pyq.py` — Previous Year Questions
- `GET /api/pyq/questions` — paginated, filterable by `year`, `subject`, `paper`, `search`
- `GET /api/pyq/years`, `/subjects`, `/papers` — filter options
- `POST /api/pyq/quiz/start` — start a quiz session (returns `session_id`)
- `POST /api/pyq/quiz/<id>/answer` — submit answer, get XP
- `GET /api/pyq/quiz/<id>/results` — final results
- `GET /api/pyq/analytics/heatmap` — topic × year heat grid
- `GET /api/pyq/analytics/subject-trend` — multi-year performance chart

#### `routes/flashcards.py`
- CRUD for decks and individual cards
- `POST /api/flashcards/review/<card_id>` — record review with `rating` (1–4, Ebisu SRS)
- `GET /api/flashcards/due` — cards due for review today
- `GET /api/flashcards/stats` — per-deck performance stats

#### `routes/warmap.py`
- `GET /api/warmap/tasks` — all war tasks with status
- `POST /api/warmap/tasks` — create task
- `PUT /api/warmap/tasks/<id>/complete` — mark complete, triggers Brain automation
- `GET /api/warmap/analytics` — heatmap / completion data

#### `routes/ravens.py` — Current Affairs
- `GET /api/ravens/articles` — news articles with filter by topic / date
- `POST /api/ravens/fetch` — trigger RSS feed fetch from configured sources
- `GET /api/ravens/compilation` — AI-generated compilation of recent articles
- `POST /api/ravens/compile` — generate a thematic compilation

#### `routes/analytics.py`
- `GET /api/analytics/overview` — master KPIs (XP, streak, accuracy)
- `GET /api/analytics/study-heatmap` — GitHub-style heatmap data
- `GET /api/analytics/subject-performance` — per-subject accuracy trends
- `GET /api/analytics/predictions` — ML-based performance forecast

#### `routes/brain_routes.py`
- `POST /api/brain/think` — chat prompt → AI reasoning + action list
- `POST /api/brain/process-task` — trigger full AI artifact bundle on task completion
- `POST /api/brain/ingest-manual` — ingest a manually generated AI JSON artifact
- `GET /api/brain/status` — brain online / lobotomized status, synapse registry
- `GET /api/brain/vault` — all stored brain artifacts by type

#### `routes/autonomy_routes.py`
- Autonomous decision loop: brain decides next best action from system state
- `POST /api/autonomy/cycle` — run one autonomy cycle
- `GET /api/autonomy/queue` — pending actions queue
- `GET /api/autonomy/history` — completed autonomous actions

#### `routes/flashcards.py` — SRS (Spaced Repetition)
Uses `ebisu_srs.py` (Ebisu probabilistic model) — smarter than Anki's SM2.

#### `routes/admin.py`
- Full database inspection, user stats reset, manual triggers for gamification events, model testing endpoints.
- Protected conceptually — designed for local personal use only.

---

### 6.4 Services Layer

`backend/app/services/` — business logic, all imported by routes:

| Service | Purpose |
|---------|---------|
| `model_manager.py` | **The AI Router** — multi-provider fallback (Gemini → NVIDIA → OpenRouter) with quota tracking, response caching |
| `brain_service.py` | **Central Nervous System** — connects all modules, generates 21-type artifact bundles |
| `autonomy_manager.py` | Autonomous action queue with priority scoring |
| `hephaestus_service.py` | Self-healing: reads error logs, generates code fixes, applies patches |
| `analytics_service.py` | Study analytics aggregation, streak calculation, performance metrics |
| `predictive_analytics.py` | ML-based performance forecasting using past accuracy trends |
| `foresight_engine.py` | AI question prediction engine (generates likely future PYQ questions) |
| `golden_path_service.py` | Optimal study path calculation based on syllabus coverage + weak areas |
| `study_planner.py` | Full study plan generation with daily task breakdown |
| `flashcard_service.py` | Deck management, card creation, review scheduling |
| `ebisu_srs.py` | Ebisu probabilistic spaced-repetition model |
| `game_engine.py` | XP rewards, level-up triggers, event dispatch |
| `badge_service.py` | Badge unlock logic (15+ badge types) |
| `challenge_service.py` | Daily/weekly challenge tracking |
| `quest_service.py` | Multi-step quest management |
| `shop_service.py` | HackSilver economy — item purchases, inventory |
| `weak_area_analyzer.py` | Identifies topics needing attention from performance data |
| `weak_area_service.py` | Extended weak area CRUD with AI-suggested study plans |
| `outcome_tracker.py` | Long-term performance trend tracking |
| `panopticon_service.py` | Biometric / mental energy tracking |
| `night_watchman.py` | Morning briefing generation (agenda + news + tasks) |
| `ravens_service.py` | RSS feed fetching, article storage, deduplication |
| `upsc_summarizer.py` | AI-powered article summarization |
| `socratic_service.py` | Generates multi-persona Socratic debates on a topic |
| `triangulation_service.py` | PESTLE + GS linkage analysis for Mains answers |
| `neural_hash_service.py` | Extracts "examiner's mental model" / cross-linkages |
| `mindmap_service.py` | Hierarchical mind map generation + storage |
| `compilation_service.py` | Compiles multiple articles into a structured brief |
| `answer_evaluator.py` | AI scoring of Mains-style answers |
| `essay_evaluator.py` | Essay structure + argument quality scoring |
| `mock_test_service.py` | Test session management, scoring, analytics |
| `pomodoro_service.py` | Pomodoro session storage + analytics |
| `psychometric_service.py` | Infers user learning style (visual/auditory/kinesthetic), peak hours |
| `ab_tester.py` | A/B testing framework for AI prompt variants |
| `synapse_registry.py` | Registry of all "synapses" (data sources Brain can query) |
| `scheduler.py` | Study schedule management from CSV / DB |
| `content_recommender.py` | Recommends next content based on history |
| `director_service.py` | High-level orchestration across multiple services |
| `doppelganger_service.py` | Generates "competitor profile" for motivational comparison |
| `hippocampus_service.py` | Short-term memory / recall context for Brain |
| `interview_service.py` | Interview prep question generation |
| `issue_mapper.py` | Maps news articles to syllabus topics |
| `neural_lace_service.py` | Creates knowledge linkage graphs |
| `newsroom_service.py` | Curates and prioritises news for UPSC relevance |
| `optimization_engine.py` | Session-level study optimisation suggestions |
| `prometheus_service.py` | Long-term performance goal projections |
| `pyq_analytics.py` | PYQ-specific analytics (topic frequency, year trend) |
| `self_review.py` | Auto-review generation from study history |
| `syllabus_tracker.py` | Tracks syllabus completion per topic/subject |
| `visualizations.py` | Chart data preparation for analytics dashboard |
| `xp_service.py` | XP calculation and level boundaries |

---

### 6.5 AI & Model Manager

**File**: `backend/app/services/model_manager.py`

**Multi-Provider Waterfall with Quota Management:**

```
Task Complexity = PRO
→ NVIDIA NIM (Llama-3.1-405B, Nemotron-340B)
→ Google Gemini Pro (2.0-pro, 1.5-pro)
→ OpenRouter Premium (Claude 3.7, GPT-4o)
→ OpenRouter Free Tier (DeepSeek-R1, Llama-3.3-70B, etc.)

Task Complexity = FAST
→ NVIDIA Fast (Llama-3.1-70B, Mixtral-8x22B)
→ OpenRouter Free (12 models)
→ Google Gemini Flash
```

**Key behaviours:**
- Quota exceeded (429) → model blacklisted for 24h in `quota_status.json`
- All responses cached in `TTLCache(maxsize=200, ttl=3600)` keyed by `MD5(prompt + model + kwargs)`
- `generate_consensus()` — **HYDRA Engine**: Nvidia drafts → Gemini critiques → Nvidia synthesises final answer

---

### 6.6 The Brain — Central Nervous System

**File**: `backend/app/services/brain_service.py` (~2100 lines)

The Brain is the **apex intelligence layer**. When a study task is completed, it:

1. Pulls context in parallel (system status, bio status from Panopticon, past lessons, specific topic data, psychometric profile)
2. Sends to Gemini Pro with a structured JSON schema
3. Parses response and executes actions

**21 artifact types generated per topic** (in `process_manual_completion_artifact`):

| # | Artifact | Stored In |
|---|---------|-----------|
| 1 | Flashcards (scenario-based) | `flashcards` table |
| 2 | Revision Note | `revision_cards` table |
| 3 | Mind Map | `mindmaps` table |
| 4 | Mock Test (10 MCQs with trap analysis) | `mock_tests` + `test_questions` |
| 5 | PYQ Trend Analysis | flashcard (type: `manual_ai_pyq`) |
| 6 | Question Predictions | `foresight_predictions` |
| 7 | Socratic Dialogue | `socratic_dialogues` |
| 8 | Triangulation (PESTLE + GS) | `triangulation_archive` |
| 9 | Neural Hash (examiner's lens) | `neural_hash_log` |
| 10 | Pitfalls / Common Traps | `ai_content_store` |
| 11 | Podcast Script | `ai_content_store` |
| 12 | Essay Prompt | `answer_writing_prompts` |
| 13 | Visual Mnemonic Prompt | `mnemonics_history` |
| 14 | Roleplay Scenario | `ai_content_store` |
| 15 | Map Work Challenge | flashcard (type: `map_work`) |
| 16 | Cross-Linkages | `ai_content_store` |
| 17 | Cheat Sheet (7 tabbed sections) | `ai_content_store` |
| 18 | Quote Bank | `ai_content_store` |
| 19 | Timeline | `ai_content_store` |
| 20 | Ethics Dilemma | `ai_content_store` |
| 21 | ELI5 / ELI15 / Expert explainer | `ai_content_store` |

**Manual Mode** (when AI quota is exhausted):
1. `generate_manual_completion_prompt()` — writes a "Titan Level" mega-prompt to `backend/manual_prompt.txt`
2. User pastes it into Gemini and saves the JSON to `backend/paste_response_here.json`
3. `POST /api/brain/ingest-manual` — reads `pending_manual_task.json` + `paste_response_here.json` and ingests everything

**Brain Actions** (dispatched from `think()` responses):
- `RETRIEVE_FROM_PALACE` — searches Mind Palace
- `PREDICT_QUESTIONS` — triggers Foresight Engine
- `TRIGGER_WATCHMAN` → Morning Briefing
- `SHOW_PANOPTICON` — bio status display
- `GENERATE_STUDY_PLAN`
- `CONSULT_GOLDEN_PATH`
- `SUMMON_BOSS` — summons a boss fight when a subject is fully completed

---

### 6.7 Hephaestus — Self-Healing System

**File**: `backend/app/services/hephaestus_service.py`

- Listens on the global Flask error handler
- On any 500 error: reads the traceback from `logs/app.log`, queries the AI to propose a code fix, applies it if confidence is high
- On startup: scans the log file for recurring errors and attempts pre-emptive repair
- All repairs are logged to `brain_actions` table

---

### 6.8 Gamification Engine

**File**: `backend/app/services/game_engine.py`

Events that trigger XP:

| Event | XP |
|-------|----|
| `TASK_COMPLETE` | 50 |
| `TASK_COMPLETE_BONUS` | 100 |
| `STRATEGY_COMMIT` | 25 |
| `PYQ_ANSWER_CORRECT` | 20 |
| `FLASHCARD_REVIEW` | 5 |
| `POMODORO_COMPLETE` | 30 |
| `MOCK_TEST_COMPLETE` | 75 |
| `BOSS_DEFEATED` | 200 |

- **Levels**: XP thresholds → `xp_service.py`
- **Badges**: 15+ types (First Blood, Scholar, Streak Master, etc.) → `badge_service.py`
- **Currency**: HackSilver earned from study, spent in the Shop → `shop_service.py`
- **Spartan Rage**: Frontend visual mode triggered at high XP streaks
- **Level Up Modal**: fires `showLevelUp` in GlobalContext when a new level is reached

---

## 7. Frontend Deep Dive

### 7.1 Application Shell

`frontend/src/App.tsx` is the layout host:

```
┌─────────────────────────────────────────────────────────┐
│  LEFT SIDEBAR (nav)   │  MAIN CONTENT  │  RIGHT RITUALS │
│  <Sidebar />          │  Tab / Route   │  <RitualsPanel>│
└─────────────────────────────────────────────────────────┘
         ↓ floating overlays (z-order)
 <AshParticles>   <SpartanRage>   <MimirChat modal>
 <PomodoroTimer>  <LevelUpModal>  <CommandPalette>
 <BrainInterface>
```

- **Tab system**: `currentTab` from `GlobalContext` controls which component renders in the main column (all within `/` route).
- **Route system**: React Router handles `/pyq-quiz/:sessionId`, `/boss-arena`, `/workbench`, etc. — these are full-page takeovers.
- **Lazy loading**: All heavy components use `React.lazy()` + `<Suspense>` for code splitting.

---

### 7.2 Global State & Contexts

#### `GlobalContext` (`src/contexts/GlobalContext.tsx`)

The master state provider. Exposes:

| State/Action | Purpose |
|-------------|---------|
| `userStats` | XP, level, streak, HackSilver |
| `currentTab` | Active module tab |
| `setCurrentTab()` | Navigate to a tab |
| `isRageMode` | Spartan Rage visual mode flag |
| `showLevelUp` | Triggers Level Up modal |
| `refreshDashboard()` | Refetches user stats from backend |
| `isSidebarOpen/isRitualsOpen` | Panel open/close state |
| `toggleSidebar/toggleRituals` | Panel toggle handlers |

#### `AnalyticsContext` (`src/contexts/AnalyticsContext.tsx`)

Scoped to the Analytics Dashboard — manages filter state (date range, subject).

#### `PomodoroContext` (`src/contexts/PomodoroContext.tsx`)

Global Pomodoro timer state — timer is accessible from any component even when navigating tabs.

---

### 7.3 Feature Modules

Each folder in `frontend/src/components/` is a self-contained feature:

| Folder | Component | Description |
|--------|-----------|-------------|
| `Admin/` | `AdminDashboard` | DB inspection, manual triggers, model test console |
| `Analytics/` | `AnalyticsDashboard`, `PYQHeatmap` | Full KPI dashboard; PYQ year × topic heat grid |
| `AnkiDojo/` | `AnkiDojo` | Anki-compatible flashcard review interface |
| `AnswerWriting/` | `AnswerWriting` | Mains answer practice with AI evaluation |
| `Armory/` | `Armory` | HackSilver shop — buy power-ups, study aids |
| `BossArena/` | `BossArena` | Gamified boss fight quizzes triggered on subject completion |
| `Brain/` | `BrainInterface`, `BrainVault` | Chat with The Brain; browse all stored AI artifacts |
| `CSAT/` | `CSATModule` | CSAT Paper II (Aptitude/Reasoning) practice module |
| `CommandPalette/` | `CommandPalette` | Keyboard-driven quick-nav (Ctrl+K style) |
| `DashboardMain/` | `DashboardMain` | Overview: streak, XP bar, today's agenda, quick actions |
| `Essay/` | `EssayWorkshop` | Essay practice with AI structure + argument scoring |
| `Flashcards/` | `FlashcardsManager` | Deck browser, card editor, SRS review mode |
| `Foresight/` | `Foresight` | AI-predicted questions and topic probability scores |
| `GoldenPath/` | `GoldenPath` | Optimal study sequence recommendation |
| `IssueMapping/` | `IssueMapping` | Maps current affairs articles to syllabus topics |
| `LoreTablets/` | `LoreTablets` | Historical and static lore/reference material |
| `Mimir/` | `Mimir` | Floating AI oracle chat (modal + embedded modes) |
| `MindMap/` | `MindMapCreator` | Interactive hierarchical mind map creator |
| `MindPalace/` | `MindPalace` | Spatial memory palace — place concepts in 3D rooms |
| `MockTests/` | `MockTests` | Full timed mock test engine with scoring + review |
| `ModelAnswers/` | `ModelAnswersManager` | UPSC model answer library browser |
| `NeuralHash/` | `NeuralHash` | Examiner pattern extractor — topic deep analysis |
| `NightWatchman/` | `MorningBriefing` | Daily morning brief (tasks + news + alerts) |
| `PYQ/` | `PYQDatabase`, `QuizSession`, `QuizResults` | PYQ browser, quiz mode, results analysis |
| `Panopticon/` | `Panopticon` | Energy/focus tracking; bio-status dashboard |
| `Planning/` | `StudyPlanDashboard` | Full study plan view with daily tasks |
| `PomodoroTimer/` | `PomodoroTimer` | Global floating Pomodoro (25/5, 50/10 modes) |
| `Quests/` | `QuestsPage` | Active quests + challenge tracker |
| `Ravens/` | `Ravens`, `CompilationGenerator` | Current affairs feed + AI compilation generator |
| `Revision/` | `RevisionCards`, `MnemonicGenerator`, `RevisionCenter` | Spaced revision card browser; mnemonic creator |
| `Scribe/` | `AnswerWorkbench` | AI-assisted answer writing workbench |
| `Seer/` | `Seer` | Predictive analytics — performance forecasting |
| `Socratic/` | `SocraticHistory` | Browse saved Socratic dialogues |
| `SpartanRage/` | `SpartanRage` | Full-screen rage mode animation overlay |
| `Syllabus/` | `SyllabusTracker` | UPSC syllabus completion tracker (GS1–4 + Optional) |
| `TimeBoxing/` | `TimeBoxing` | Time-blocking / calendar view for study sessions |
| `WarMap/` | `WarMapContainer`, `TriangulationHistory` | Task war map + triangulation archive |
| `WeakAreas/` | `WeakAreasDashboard` | Weak topic detector + AI drill recommendations |
| `Yggdrasil/` | `Yggdrasil` | Knowledge tree (Codex) — concept web visualisation |

**Shared components:**
- `Sidebar.tsx` — navigation rail with all module links + XP bar
- `RitualsPanel.tsx` — right panel (daily rituals, habit tracker)
- `StudyTimer.tsx` — lightweight inline study timer
- `Toast.tsx` — toast notification system
- `XPBar.tsx` — animated XP progress bar
- `LevelUpModal.tsx` — level-up celebration overlay
- `AshParticles.tsx` — background particle effect (intensifies in rage mode)

---

## 8. Feature Reference A–Z

### Answer Writing (Mains Practice)
Submit a Mains-style answer → AI evaluates on: structure, content depth, examples, word limit, GS relevance. Score + detailed feedback returned. Prompts stored in `answer_writing_prompts` table.

### Boss Arena
When you complete all tasks for a subject/book, a Boss Fight is summoned. A 10-question timed MCQ quiz — defeat the boss to earn bonus XP and a badge. Boss name is auto-generated (`"The Guardian of Laxmikanth"`).

### Brain Vault
Every AI artifact ever generated (flashcards, socratic dialogues, triangulations, predictions, cheat sheets) is stored and browsable in the Brain Vault. Filter by type, topic, or date.

### CSAT Module
Aptitude and reasoning practice for UPSC Paper 1. Bank of questions, timed drill mode, per-topic performance stats.

### Compilation Generator
Aggregates multiple Ravens articles on a theme → AI generates a structured compilation brief with key points, significance, and Mains linkages.

### Essay Workshop
Full essay writing environment. Prompts are AI-generated (essay_prompt artifact from Brain), essays are AI-evaluated for: thesis clarity, argument strength, balance, examples, conclusion quality.

### Flashcards (SRS)
Ebisu probabilistic model — unlike Anki's SM-2, Ebisu tracks *probability of recall* as a Beta distribution. `ebisu_srs.py` handles the math. Rating 1–4 (Again/Hard/Good/Easy) updates the model parameters.

### Foresight (Question Prediction)
Analysed PYQ patterns → AI predicts 3 "Black Swan" questions per topic. Stored in `foresight_predictions`. Probability score is shown on the Foresight UI.

### Golden Path
Given remaining time budget (hours) + syllabus coverage + weak areas → AI generates an optimal topic sequence. The Brain adopts this as the "Grand Strategy" and references it in all subsequent `think()` calls.

### Heatmap (PYQ)
Year (X) × Topic (Y) matrix showing which topics appeared in which UPSC Prelims years. Colour intensity = frequency. Built from `pyq_questions` table.

### Issue Mapping
RSS articles are auto-mapped to syllabus topics using fuzzy matching + AI (`thefuzz` library + Gemini). View articles by GS topic.

### Mind Palace
Spatial memory system — create "rooms", place concept "items" in locations, then take a "journey" to mentally traverse and recall them. Backend: `mind_palace_rooms`, `palace_items`, `palace_journeys`.

### Mimir (AI Oracle)
Floating chat window. `POST /api/mimir/ask` → Brain's `think()` is called. Mimir suggests actions (study plan, predictions, briefing) which can be clicked to navigate directly.

### Mock Tests
Full UPSC Prelims-style tests (100 questions / 2 hours). AI generates questions per topic. Negative marking supported. End screen shows accuracy, time per question, topic-wise breakdown.

### Neural Hash
Extracts the "examiner's mental model" for a topic — core themes, cross-linkages, common traps — so you understand what UPSC examiners are actually testing.

### Night Watchman
Morning briefing system. Every day, generates: today's task list (from War Map), top 3 current affairs (from Ravens), bio-status (from Panopticon), and a motivational directive. `GET /night-watchman/brief`.

### Panopticon
Tracks mental energy via a daily self-assessment (energy %, focus quality). The Brain reads this data via `check_bio_status()` and adjusts recommendations (e.g., avoids assigning heavy topics when energy is low).

### Pomodoro Timer
Global 25/5 or 50/10 Pomodoro timer that persists across tab navigation. Session data stored → contributes to XP and analytics.

### PYQ Database
Full filterable database of UPSC Prelims (2010–2024) questions. Filter by year, subject, paper. Full-text search. Start a timed quiz from any filtered subset.

### Ravens (Current Affairs)
RSS feeds from configured news sources → articles fetched, deduplicated, stored. Available as a filterable feed. Supports AI compilation generation.

### Revision
Three sub-tools:
1. **Revision Cards** — flip card review of stored revision notes
2. **Mnemonic Generator** — AI creates acronym/story/visual mnemonics
3. **Revision Center** — scheduled revision (SRS-based due dates)

### Scribe (Answer Workbench)
Full Mains answer writing environment with a rich text editor, AI mentor sidebar, word count, and inline AI feedback.

### Socratic Dialogue
4-persona staged debate: Skeptic (Socrates), Idealist (Plato), Realist (Aristotle), Strategist (Machiavelli). Each turn is 50–100 words. Ends with a Hegelian synthesis. Stored in `socratic_dialogues`, browsable in Socratic History.

### Study Plan
Upload or generate a study plan (CSV or AI-generated). Tasks assigned per day. War Map and Morning Briefing pull from active plan.

### Syllabus Tracker
Full UPSC syllabus (GS1–4 + Optional Subjects). Mark topics as `Pending → In Progress → Completed`. Completion % shown per subject.

### Time Boxing
Calendar view for blocking study sessions. Drag-and-drop time allocation across subjects for the week.

### Triangulation
For any topic: PESTLE analysis, GS1/2/3/4 linkages, optional subject linkages, scholar quotes, data bank, arguments for/against, way forward. Designed as a Mains answer prep tool.

### War Map
Task board for day-to-day study tasks. Completing a task → triggers Brain's full AI artifact bundle (flashcards, mock test, predictions, triangulation, etc.).

### Weak Areas
Automatically identifies topics where performance (accuracy < threshold) is weak. AI suggests targeted drill plan. Integrated with the Golden Path to prioritise these in the study sequence.

### Yggdrasil (Codex)
The knowledge tree — a visual network of all studied concepts and their relationships. Built using `networkx` on the backend.

---

## 9. Database Schema Overview

### Core Tables

```sql
users (id, username, email, created_at)
user_stats (user_id, xp, level, streak, hack_silver, total_tasks_completed, ...)

tasks (id, user_id, title, subject, topic, status, priority, due_date, ...)
study_plans (id, user_id, title, start_date, end_date, is_active)
study_plan_tasks (id, plan_id, topic, subject, scheduled_date, status, ...)
```

### Flashcard Tables

```sql
decks (id, user_id, name, subject, created_at)
flashcards (id, deck_id, front, back, source, card_type, ...)
flashcard_reviews (id, card_id, rating, reviewed_at, next_review_at, model_alpha, model_beta, model_t)
```

### PYQ Tables

```sql
pyq_questions (id, year, paper, subject, topic, question_text, option_a-d, correct_answer, explanation)
pyq_quiz_sessions (id, user_id, filters_json, started_at, completed_at)
pyq_quiz_answers (id, session_id, question_id, user_answer, is_correct, time_taken)
```

### Gamification Tables

```sql
xp_events (id, user_id, event_type, xp_amount, description, created_at)
badges (id, user_id, badge_type, badge_name, earned_at)
challenges (id, user_id, type, target, progress, completed, expires_at)
shop_items (id, name, description, cost, item_type, effect_data)
user_inventory (id, user_id, item_id, purchased_at, is_active)
```

### AI / Brain Tables

```sql
brain_memory (id, user_id, memory_type, content, context, created_at)
brain_actions (id, user_id, action_type, payload, result, created_at)
socratic_dialogues (id, user_id, topic, dialogue_json, verdict_json, created_at)
triangulation_archive (id, topic, synthesis, full_data_json, created_at)
ai_content_store (id, content_type, topic, content, metadata_json, created_at)
foresight_predictions (id, question, subject, topic, type, probability, created_at)
neural_hash_log (id, topic, entity_type, hash_data_json, created_at)
```

### Mock Tests

```sql
mock_tests (id, title, subject, total_questions, duration_minutes, test_type, total_marks)
test_questions (id, test_id, question_number, question_text, option_a-d, correct_answer, explanation)
test_attempts (id, test_id, user_id, started_at, completed_at, score, accuracy)
test_responses (id, attempt_id, question_id, user_answer, is_correct, time_taken)
```

---

## 10. Migration Scripts

> ⚠️ All `migrate_*.py` scripts are **one-time, safe, additive** — they add columns/tables using `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` patterns. Safe to run on existing databases.

| Script | What It Does |
|--------|-------------|
| `migrate_flashcards.py` | Adds SRS columns to `flashcards` table |
| `migrate_csat.py` | Creates CSAT questions + topic tables |
| `migrate_syllabus.py` | Seeds full UPSC syllabus into `syllabus_topics` |
| `migrate_full_syllabus.py` | Extended syllabus with subtopics |
| `migrate_pyq.py` | Creates PYQ tables + imports from CSV |
| `migrate_arena.py` | Boss arena + battle tables |
| `migrate_badges.py` | Badge + achievement tables |
| `migrate_challenges.py` | Daily/weekly challenge tables |
| `migrate_answer_writing.py` | Answer writing + evaluation tables |
| `migrate_mock_tests.py` | Mock test engine tables |
| `migrate_essay.py` | Essay prompts + submissions table |
| `migrate_shop.py` | Shop items + inventory tables |
| `migrate_weak_areas.py` | Weak area tracking tables |
| `migrate_revisions.py` | Revision card tables |
| `migrate_mindmaps.py` | Mind map storage tables |
| `migrate_mnemonics.py` | Mnemonics history table |
| `migrate_scribe.py` | Scribe/workbench tables |
| `migrate_performance.py` | Performance analytics tables |
| `migrate_add_hacksilver.py` | Adds `hack_silver` column to `user_stats` |
| `migrate_add_admin_column.py` | `is_admin` flag on users |
| `migrate_tasks_priority.py` | Priority + tags on tasks table |
| `migrate_model_answers.py` | Model answers library table |
| `import_pyq_csv.py` | Bulk-imports PYQ questions from CSV |
| `import_scheduler_csv.py` | Imports study schedule from `mimir_schedule.csv` |

**Running a migration:**

```bash
cd backend
source venv/bin/activate
python migrate_flashcards.py  # example
```

---

## 11. Utility & Debug Scripts

Located in `backend/`:

| Script | Purpose |
|--------|---------|
| `check_db.py` | List all tables and row counts |
| `check_schema.py` | Print schema of specific table |
| `inspect_db.py` | Full DB introspection dump |
| `debug_analytics.py` | Run analytics queries manually |
| `debug_battles.py` | Inspect battle/boss data |
| `debug_plan.py` | Print active study plan tasks |
| `debug_news.py` | Inspect Ravens article counts |
| `debug_flashcards.py` | Flashcard count + SRS stats |
| `seed_analytics.py` | Seed fake analytics data for testing |
| `seed_revision.py` | Seed revision cards |
| `seed_syllabus.py` | Seed syllabus topics |
| `cleanup_orphaned_flashcards.py` | Remove flashcards with no deck |
| `cleanup_duplicates.py` | Remove duplicate PYQ entries |
| `fix_schema.py` | Comprehensive schema patch (run if errors on startup) |
| `fix_db.py` | DB repair utility |
| `restore_db.py` | Restore DB from backup |
| `test_backend_apis.py` | Full API endpoint test suite |
| `test_gemini.py` | Test Gemini API connectivity |
| `verify_*.py` | Feature-specific verification scripts |
| `stress_test_quota.py` | Stress-test model quota rotation |
| `analyze_openrouter.py` | Analyse OpenRouter usage patterns |

Also at **project root**:

| Script | Purpose |
|--------|---------|
| `run_saga.bat` | Windows launcher (starts both backend + frontend) |
| `verify_full_autonomy.py` | Tests the full autonomous Brain cycle |
| `verify_quota_compliance.py` | Confirms quota rotation works correctly |
| `check_csat.py` | Verify CSAT data integrity |
| `mimir_schedule.csv` | 120k+ row study schedule (Mimir / scheduler import) |

---

## 12. Docker & Deployment

### Local Docker

```bash
# From project root
cp backend/.env.example backend/.env
# Fill in GEMINI_API_KEY
docker compose up --build
```

- Backend: `http://localhost:5000`
- Frontend: `http://localhost:80`

### Production (Fly.io)

Config in `backend/fly.toml`. See `DEPLOY.md` and `DEPLOYMENT_GUIDE.md` for full steps.

```bash
cd backend
fly deploy
```

### Backend Dockerfile

Multi-stage build → installs Python dependencies → runs `gunicorn app:app -w 4 -b 0.0.0.0:5000`.

The `instance/` directory is mounted as a Docker volume to persist `upsc_saga.db`, logs, and `current_strategy.json` across restarts.

---

## 13. API Endpoints Cheatsheet

```
# Dashboard
GET  /api/dashboard               → user stats + today's agenda

# Study Tasks / War Map
GET  /api/warmap/tasks            → all tasks
POST /api/warmap/tasks            → create task { title, subject, topic, priority }
PUT  /api/warmap/tasks/:id/complete → mark done (triggers Brain)
DELETE /api/warmap/tasks/:id       → delete task

# Flashcards
GET  /api/flashcards/decks         → all decks
POST /api/flashcards/decks         → create deck { name, subject }
GET  /api/flashcards/due           → cards due for review
POST /api/flashcards/review/:id    → submit review { rating: 1-4 }

# PYQ
GET  /api/pyq/questions?year=&subject=&search=   → filtered questions
POST /api/pyq/quiz/start { filters }             → returns { session_id }
POST /api/pyq/quiz/:id/answer { answer }
GET  /api/pyq/quiz/:id/results

# Brain
POST /api/brain/think { message }               → AI response + actions
POST /api/brain/process-task { topic, subject } → trigger artifact generation
POST /api/brain/ingest-manual                   → ingest manual AI JSON
GET  /api/brain/vault                           → all stored brain content

# Autonomy
POST /api/autonomy/cycle                        → run one autonomous cycle

# Analytics
GET  /api/analytics/overview
GET  /api/analytics/study-heatmap
GET  /api/analytics/subject-performance

# Night Watchman
GET  /night-watchman/brief                       → today's morning briefing

# Ravens
GET  /api/ravens/articles?topic=&date=
POST /api/ravens/fetch                           → trigger RSS fetch
POST /api/ravens/compile { theme }

# Study Plan
GET  /api/study-plan/active
POST /api/study-plan/generate { start_date, duration_weeks }

# Gamification
GET  /api/quests
GET  /api/badges
GET  /api/shop-new/items
POST /api/shop-new/purchase/:item_id
```

---

## 14. Common Issues & Fixes

### `401 Unauthorized` / Empty responses on API calls

**Cause**: Some routes try to read a Flask session that doesn't exist.
**Fix**: All routes are patched to use `user_id = 1` as the fallback when no session is found. If you see a 401, find the route and replace any `session.get('user_id')` call with:
```python
user_id = session.get('user_id', 1)
```

### Brain is "Lobotomized" / AI features not working

**Check**: `GET /api/brain/status` → look for `"lobotomized": true`
**Fix**: Ensure `GEMINI_API_KEY` is set in `backend/.env`. The Brain falls back to mock mode if the key is missing.

### Quota exceeded errors (429)

**Cause**: Free Gemini quota hit (15 requests/minute, 1500/day on free tier).
**Fix**: ModelManager automatically rotates to OpenRouter or NVIDIA. If all are exhausted, `quota_status.json` will have blocked entries. They auto-clear after 24h, or delete the file to force reset:
```bash
rm backend/app/services/quota_status.json
```

### Database errors on startup

```bash
cd backend
source venv/bin/activate
python fix_schema.py       # Applies all missing schema patches
python check_db.py         # Verify tables exist
```

### Missing table: `X does not exist`

Run the corresponding migration:
```bash
python migrate_X.py
```
If unsure, run `fix_schema.py` — it's a master patch script.

### Frontend can't connect to backend

Check `frontend/src/config.ts` — ensure `API_BASE_URL` points to `http://localhost:5000`.

### AI artifacts not being saved after task completion

The Brain runs in a background thread. Check `logs/app.log` for errors. Common cause: `GEMINI_API_KEY` missing or DB table doesn't exist. Run `fix_schema.py`.

### React app shows "Loading the Realms..." indefinitely

Backend is not responding. Start the backend first:
```bash
cd backend && python app.py
```

### `thefuzz` import error

```bash
pip install thefuzz python-Levenshtein
```

---

## 15. Authentication Model

> **This is a single-user local application. There is NO authentication barrier.**

The app was designed for personal use on a local machine. All endpoints accept requests without any token or session validation.

**Pattern used everywhere:**

```python
user_id = session.get('user_id', 1)  # Always defaults to user_id = 1
```

If you want to add multi-user support in the future:
1. Add a `POST /api/auth/login` route that sets `session['user_id']`
2. Add Flask-Login or JWT middleware
3. Replace all `user_id = 1` defaults with proper session reads

---

## 16. Adding a New Feature — Step-by-Step

1. **DB Model** — Create `backend/app/db_models/my_feature.py`
   ```python
   def init_my_feature_tables():
       conn = get_db()
       conn.execute('''CREATE TABLE IF NOT EXISTS my_table (id INTEGER PRIMARY KEY, ...)''')
       conn.commit()
   ```

2. **Register in App Factory** — Add to `backend/app/__init__.py`:
   ```python
   from app.db_models.my_feature import init_my_feature_tables
   with app.app_context():
       init_my_feature_tables()
   ```

3. **Service** — Create `backend/app/services/my_feature_service.py` with business logic.

4. **Route** — Create `backend/app/routes/my_feature.py`:
   ```python
   from flask import Blueprint, jsonify
   bp = Blueprint('my_feature', __name__)
   
   @bp.route('/api/my-feature', methods=['GET'])
   def get_my_feature():
       user_id = session.get('user_id', 1)
       ...
       return jsonify({...})
   ```

5. **Register Blueprint** — In `backend/app/__init__.py`:
   ```python
   from .routes import my_feature
   app.register_blueprint(my_feature.bp)
   ```

6. **Frontend Component** — Create `frontend/src/components/MyFeature/MyFeature.tsx`

7. **Add to App.tsx** — Lazy import + tab mapping:
   ```tsx
   const MyFeature = lazy(() => import('./components/MyFeature/MyFeature'));
   // In JSX:
   {currentTab === 'my-feature' && <MyFeature />}
   ```

8. **Add to Sidebar** — Add nav link in `Sidebar.tsx` with the tab name `'my-feature'`.

---

## Architecture Flow Diagram

```
User Action (e.g., complete a topic)
         │
         ▼
  PUT /api/warmap/tasks/:id/complete
         │
         ▼
  warmap.py route → Updates task status → Triggers game_engine
         │
         ├──► XP awarded → user_stats updated → GlobalContext refreshed
         │
         └──► brain_service.process_task_completion(task_data)
                    │
                    ├──► concurrent.futures (parallel AI calls):
                    │      CREATE_FLASHCARDS, CREATE_MOCK_TEST,
                    │      PREDICT_QUESTIONS, GENERATE_LINKAGES,
                    │      GENERATE_PODCAST, GENERATE_SOCRATIC
                    │
                    └──► Check Boss Fight → SUMMON_BOSS if subject complete
                                │
                                └──► Boss Arena quest created → frontend notified
```

---

*Built with obsession by an aspirant who refused to use plain Notion.*
