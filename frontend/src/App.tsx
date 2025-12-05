import { Routes, Route, useLocation } from 'react-router-dom';
import { Suspense, lazy, useEffect } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import DashboardMain from './components/DashboardMain';
import RitualsPanel from './components/RitualsPanel';
import SpartanRage from './components/SpartanRage/SpartanRage';
import MimirChat from './components/Mimir/Mimir';
import PomodoroTimer from './components/PomodoroTimer/PomodoroTimer';
import LevelUpModal from './components/LevelUpModal';
import AshParticles from './components/AshParticles';
import { useGlobal } from './contexts/GlobalContext';
import { AnalyticsProvider } from './contexts/AnalyticsContext';
import { PomodoroProvider } from './contexts/PomodoroContext';
import CommandPalette from './components/CommandPalette/CommandPalette';
import BrainInterface from './components/Brain/BrainInterface';

// Lazy Load Heavy Components
const WarMapContainer = lazy(() => import('./components/WarMap/WarMapContainer'));
const SyllabusTracker = lazy(() => import('./components/Syllabus/SyllabusTracker'));
const QuestsPage = lazy(() => import('./components/Quests/QuestsPage'));
const YggdrasilTree = lazy(() => import('./components/Yggdrasil/Yggdrasil'));
const NeuralHash = lazy(() => import('./components/NeuralHash/NeuralHash'));
const LoreTablets = lazy(() => import('./components/LoreTablets/LoreTablets'));
const PYQDatabase = lazy(() => import('./components/PYQ/PYQDatabase'));
const Armory = lazy(() => import('./components/Armory/Armory'));
const AnkiDojo = lazy(() => import('./components/AnkiDojo/AnkiDojo'));
const Seer = lazy(() => import('./components/Seer/Seer'));
const Ravens = lazy(() => import('./components/Ravens/Ravens'));
const AnswerWriting = lazy(() => import('./components/AnswerWriting/AnswerWriting'));
const MockTests = lazy(() => import('./components/MockTests/MockTests'));
const EssayWorkshop = lazy(() => import('./components/Essay/EssayWorkshop'));
const CSATModule = lazy(() => import('./components/CSAT/CSATModule'));
const FlashcardsManager = lazy(() => import('./components/Flashcards/FlashcardsManager'));
const AnalyticsDashboard = lazy(() => import('./components/Analytics/AnalyticsDashboard'));
const WeakAreasDashboard = lazy(() => import('./components/WeakAreas/WeakAreasDashboard'));
const AdminDashboard = lazy(() => import('./components/Admin/AdminDashboard'));
const AnswerWorkbench = lazy(() => import('./components/Scribe/AnswerWorkbench'));
const BossArena = lazy(() => import('./components/BossArena/BossArena'));
const QuizSession = lazy(() => import('./components/PYQ/QuizSession'));
const QuizResults = lazy(() => import('./components/PYQ/QuizResults'));
const TimeBoxing = lazy(() => import('./components/TimeBoxing/TimeBoxing'));
const StudyPlanDashboard = lazy(() => import('./components/Planning/StudyPlanDashboard'));
const RevisionCards = lazy(() => import('./components/Revision/RevisionCards'));
const MnemonicGenerator = lazy(() => import('./components/Revision/MnemonicGenerator'));
const PYQHeatmap = lazy(() => import('./components/Analytics/PYQHeatmap'));
const ModelAnswersManager = lazy(() => import('./components/ModelAnswers/ModelAnswersManager'));
const RevisionCenter = lazy(() => import('./components/Revision/RevisionCenter'));
const MindMapCreator = lazy(() => import('./components/MindMap/MindMapCreator'));
const CompilationGenerator = lazy(() => import('./components/Ravens/CompilationGenerator'));
const MindPalace = lazy(() => import('./components/MindPalace/MindPalace'));
const Foresight = lazy(() => import('./components/Foresight/Foresight'));
const MorningBriefing = lazy(() => import('./components/NightWatchman/MorningBriefing'));
const Panopticon = lazy(() => import('./components/Panopticon/Panopticon'));
const GoldenPath = lazy(() => import('./components/GoldenPath/GoldenPath'));

function App() {
  const {
    userStats,
    currentTab,
    setCurrentTab,
    isRageMode,
    showLevelUp,
    setShowLevelUp,
    isLoading,
    error,
    refreshDashboard,
    isSidebarOpen,
    toggleSidebar,
    isRitualsOpen,
    toggleRituals
  } = useGlobal();

  const location = useLocation();

  useEffect(() => {
    fetch('/api/ravens/background-fetch', { method: 'POST' })
      .then(response => {
        if (!response.ok) {
          console.error('Failed to start background fetch');
        } else {
          console.log('Background fetch for Ravens initiated.');
        }
      })
      .catch(error => console.error('Error starting background fetch:', error));
  }, []);

  // Handle task completion (audio + refresh) - passed to components that need simple callback
  const handleSessionComplete = async () => {
    await refreshDashboard();
  };

  // Trigger background news fetch on app load
  useEffect(() => {
    const triggerRavens = async () => {
      try {
        await fetch('http://localhost:5000/api/ravens/background-fetch', { method: 'POST' });
        console.log("🦅 Ravens dispatched for background scouting.");
      } catch (err) {
        console.error("🦅 Failed to dispatch Ravens:", err);
      }
    };
    triggerRavens();
  }, []);

  if (isLoading && !userStats) return <div className="loading-screen">Loading the Realms...</div>;
  if (error) return <div className="error-screen">Error: {error}</div>;

  return (
    <AnalyticsProvider>
      <PomodoroProvider onSessionComplete={handleSessionComplete}>
        <div className={`app-container ${isSidebarOpen ? 'left-open' : ''} ${isRitualsOpen ? 'right-open' : ''}`} style={{
          backgroundImage: `url(/assets/bg_main.jpg)`,
          backgroundSize: 'cover',
          minHeight: '100vh',
          position: 'relative'
        }}>

          {/* BACKGROUND PARTICLES (Z-Index 0) */}
          <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0 }}>
            <AshParticles isRageMode={isRageMode} />
          </div>

          {/* LEFT SIDEBAR */}
          <Sidebar />

          {/* HAMBURGER BUTTON (Mobile & Desktop) */}
          <button
            className={`sidebar-toggle-btn ${isSidebarOpen ? 'open' : ''}`}
            onClick={toggleSidebar}
            aria-label="Toggle Sidebar"
          >
            ☰
          </button>

          {/* RIGHT SIDEBAR TOGGLE (Rituals) */}
          <button
            className={`sidebar-toggle-btn right ${isRitualsOpen ? 'open' : ''}`}
            onClick={toggleRituals}
            aria-label="Toggle Rituals"
          >
            ☰
          </button>

          {/* MAIN CONTENT AREA (Middle Column - Z-Index 10) */}
          <main className={`content ${isSidebarOpen ? 'sidebar-open' : 'sidebar-closed'} ${isRitualsOpen ? 'rituals-open' : 'rituals-closed'}`} style={{
            backgroundImage: currentTab === 'dashboard' ? `url(/assets/bg_sidebar.png)` : undefined,
            backgroundSize: 'cover',
            height: '100vh',
            maxHeight: '100vh',
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            zIndex: 10,
            position: 'relative',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
          }}>
            <Suspense fallback={<div className="loading-screen">Summoning Realm...</div>}>
              {/* Only render Tab Content if we are on the root path */}
              {location.pathname === '/' && (
                <>
                  {currentTab === 'dashboard' && <DashboardMain />}
                  {currentTab === 'war-map' && <WarMapContainer onTaskCompleted={refreshDashboard} />}
                  {currentTab === 'syllabus' && <SyllabusTracker onTaskCompleted={refreshDashboard} />}
                  {currentTab === 'quests' && <QuestsPage onTaskCompleted={refreshDashboard} />}
                  {currentTab === 'codex' && <YggdrasilTree />}
                  {currentTab === 'lore-tablets' && <LoreTablets />}
                  {currentTab === 'pyq' && <PYQDatabase />}
                  {currentTab === 'armory' && <Armory />}
                  {currentTab === 'dojo' && <AnkiDojo />}
                  {currentTab === 'seer' && <Seer />}
                  {currentTab === 'ravens' && <Ravens />}
                  {currentTab === 'answer-writing' && <AnswerWriting onTaskCompleted={refreshDashboard} />}
                  {currentTab === 'mock-tests' && <MockTests onTaskCompleted={refreshDashboard} />}
                  {currentTab === 'essay' && <EssayWorkshop onTaskCompleted={refreshDashboard} />}
                  {currentTab === 'csat' && <CSATModule />}
                  {currentTab === 'compilation' && <CompilationGenerator />}
                  {currentTab === 'flashcards' && <FlashcardsManager onTaskCompleted={refreshDashboard} />}
                  {currentTab === 'analytics' && <AnalyticsDashboard onNavigate={setCurrentTab} />}
                  {currentTab === 'weak-areas' && <WeakAreasDashboard />}
                  {currentTab === 'admin' && <AdminDashboard />}
                  {currentTab === 'scribe' && <AnswerWorkbench />}
                  {currentTab === 'arena' && <BossArena onBattleComplete={refreshDashboard} />}
                  {(currentTab === 'planner' || currentTab === 'study-plan') && <StudyPlanDashboard />}
                  {currentTab === 'revision-cards' && <RevisionCards />}
                  {currentTab === 'mnemonics' && <MnemonicGenerator />}
                  {currentTab === 'heatmap' && <PYQHeatmap />}
                  {currentTab === 'model-answers' && <ModelAnswersManager />}
                  {currentTab === 'mindmap' && <MindMapCreator />}
                  {currentTab === 'mind-palace' && <MindPalace />}
                  {currentTab === 'foresight' && <Foresight />}
                  {currentTab === 'watchman' && <MorningBriefing />}
                  {currentTab === 'panopticon' && <Panopticon />}
                  {currentTab === 'neural-hash' && <NeuralHash />}
                  {currentTab === 'golden-path' && <GoldenPath />}
                  {currentTab === 'revision-center' && <RevisionCenter />}
                  {currentTab === 'timebox' && <TimeBoxing />}
                </>
              )}

              {/* Quiz Mode Routes */}
              <Routes>
                <Route path="/" element={null} />
                <Route path="/pyq-quiz/:sessionId" element={<QuizSession />} />
                <Route path="/pyq-quiz-results/:sessionId" element={<QuizResults />} />
                <Route path="/analytics" element={<AnalyticsDashboard />} />
                <Route path="/workbench" element={<AnswerWorkbench />} />
                <Route path="/boss-arena" element={<BossArena onBattleComplete={refreshDashboard} />} />
                <Route path="/timebox" element={<TimeBoxing />} />
                <Route path="/revision-center" element={<RevisionCenter />} />
                <Route path="/mindmap" element={<MindMapCreator />} />
                <Route path="/mind-palace" element={<MindPalace />} />
                <Route path="/foresight" element={<Foresight />} />
                <Route path="/watchman" element={<MorningBriefing />} />
                <Route path="/panopticon" element={<Panopticon />} />
                <Route path="/neural-hash" element={<NeuralHash />} />
                <Route path="/golden-path" element={<GoldenPath />} />

                {/* Brain Navigation Routes */}
                <Route path="/mock-tests" element={<MockTests onTaskCompleted={refreshDashboard} />} />
                <Route path="/flashcards" element={<FlashcardsManager onTaskCompleted={refreshDashboard} />} />
                <Route path="/study-plan" element={<StudyPlanDashboard />} />
                <Route path="/weak-areas" element={<WeakAreasDashboard />} />
              </Routes>
            </Suspense>
          </main>

          {/* RITUALS PANEL (Right Column) */}
          <div className={`rituals-panel-wrapper ${isRitualsOpen ? 'open' : 'closed'}`} style={{ zIndex: 15, position: 'relative' }}>
            <RitualsPanel />
          </div>

          {/* --- OVERLAYS & FLOATING ELEMENTS --- */}

          <SpartanRage />

          {/* Floating Mimir - Modal Mode */}
          <MimirChat mode="modal" />

          {/* Pomodoro Timer - Global productivity tool (Hidden on Dashboard to avoid duplication) */}
          <PomodoroTimer className="pomodoro-above-mimir" />

          {showLevelUp && userStats && (
            <LevelUpModal
              newLevel={userStats.level}
              onClose={() => setShowLevelUp(false)}
            />
          )}

          {/* Global Command Palette */}
          <CommandPalette />

          {/* Central Nervous System Interface */}
          <BrainInterface />
        </div>
      </PomodoroProvider>
    </AnalyticsProvider>
  );
}

export default App;