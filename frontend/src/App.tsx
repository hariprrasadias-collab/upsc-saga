import { Routes, Route, useLocation } from 'react-router-dom';
import './App.css';
import Sidebar from './components/Sidebar';
import DashboardMain from './components/DashboardMain';
import WarMapContainer from './components/WarMap/WarMapContainer';
import SyllabusTracker from './components/Syllabus/SyllabusTracker';
import QuestsPage from './components/Quests/QuestsPage';
import YggdrasilTree from './components/Yggdrasil/Yggdrasil';
import LoreTablets from './components/LoreTablets/LoreTablets';
import PYQDatabase from './components/PYQ/PYQDatabase';
import Armory from './components/Armory/Armory';
import AnkiDojo from './components/AnkiDojo/AnkiDojo';
import Seer from './components/Seer/Seer';
import Ravens from './components/Ravens/Ravens';
import AnswerWriting from './components/AnswerWriting/AnswerWriting';
import MockTests from './components/MockTests/MockTests';
import EssayWorkshop from './components/Essay/EssayWorkshop';
import CSATModule from './components/CSAT/CSATModule';
import FlashcardsManager from './components/Flashcards/FlashcardsManager';
import AnalyticsDashboard from './components/Analytics/AnalyticsDashboard';
import WeakAreasDashboard from './components/WeakAreas/WeakAreasDashboard';
import AdminDashboard from './components/Admin/AdminDashboard';
import AnswerWorkbench from './components/Scribe/AnswerWorkbench';
import BossArena from './components/BossArena/BossArena';
import RitualsPanel from './components/RitualsPanel';
import SpartanRage from './components/SpartanRage/SpartanRage';
import MimirChat from './components/Mimir/Mimir';
import PomodoroTimer from './components/PomodoroTimer/PomodoroTimer';
import LevelUpModal from './components/LevelUpModal';
import AshParticles from './components/AshParticles';
import { useGlobal } from './contexts/GlobalContext';
import { AnalyticsProvider } from './contexts/AnalyticsContext';
import { PomodoroProvider } from './contexts/PomodoroContext';
import QuizSession from './components/PYQ/QuizSession';
import QuizResults from './components/PYQ/QuizResults';
import TimeBoxing from './components/TimeBoxing/TimeBoxing';
import StudyPlanDashboard from './components/Planning/StudyPlanDashboard';
import CommandPalette from './components/CommandPalette/CommandPalette';
import RevisionCards from './components/Revision/RevisionCards';
import MnemonicGenerator from './components/Revision/MnemonicGenerator';
import PYQHeatmap from './components/Analytics/PYQHeatmap';
import ModelAnswersManager from './components/ModelAnswers/ModelAnswersManager';
import RevisionCenter from './components/Revision/RevisionCenter';
import MindMapCreator from './components/MindMap/MindMapCreator';
import CompilationGenerator from './components/Ravens/CompilationGenerator';
import BrainInterface from './components/Brain/BrainInterface';

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
    toggleSidebar
  } = useGlobal();

  const location = useLocation();

  // Handle task completion (audio + refresh) - passed to components that need simple callback
  const handleSessionComplete = async () => {
    await refreshDashboard();
  };

  if (isLoading && !userStats) return <div className="loading-screen">Loading the Realms...</div>;
  if (error) return <div className="error-screen">Error: {error}</div>;

  return (
    <AnalyticsProvider>
      <PomodoroProvider onSessionComplete={handleSessionComplete}>
        <div className="app-container" style={{
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

          {/* MAIN CONTENT AREA (Middle Column - Z-Index 10) */}
          <main className={`content ${isSidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`} style={{
            backgroundImage: currentTab === 'dashboard' ? `url(/assets/bg_sidebar.png)` : undefined,
            backgroundSize: 'cover',
            height: '100vh',
            maxHeight: '100vh',
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            zIndex: 10,
            position: 'relative',
            transition: 'margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
          }}>
            {/* Only render Tab Content if we are on the root path */}
            {location.pathname === '/' && (
              <>
                {currentTab === 'dashboard' && (
                  <DashboardMain />
                )}
                {currentTab === 'war-map' && (
                  <WarMapContainer onTaskCompleted={refreshDashboard} />
                )}
                {currentTab === 'syllabus' && (
                  <SyllabusTracker onTaskCompleted={refreshDashboard} />
                )}
                {currentTab === 'quests' && (
                  <QuestsPage onTaskCompleted={refreshDashboard} />
                )}
                {currentTab === 'codex' && (
                  <YggdrasilTree />
                )}
                {currentTab === 'lore-tablets' && (
                  <LoreTablets />
                )}
                {currentTab === 'pyq' && (
                  <PYQDatabase />
                )}
                {currentTab === 'armory' && (
                  <Armory />
                )}
                {currentTab === 'dojo' && (
                  <AnkiDojo />
                )}
                {currentTab === 'seer' && (
                  <Seer />
                )}
                {currentTab === 'ravens' && (
                  <Ravens />
                )}
                {currentTab === 'answer-writing' && (
                  <AnswerWriting onTaskCompleted={refreshDashboard} />
                )}
                {currentTab === 'mock-tests' && (
                  <MockTests onTaskCompleted={refreshDashboard} />
                )}
                {currentTab === 'essay' && (
                  <EssayWorkshop onTaskCompleted={refreshDashboard} />
                )}
                {currentTab === 'csat' && <CSATModule />}
                {currentTab === 'compilation' && <CompilationGenerator />}
                {/* Mimir is now a modal, no fullpage route */}
                {currentTab === 'flashcards' && (
                  <FlashcardsManager onTaskCompleted={refreshDashboard} />
                )}
                {currentTab === 'analytics' && (
                  <AnalyticsDashboard onNavigate={setCurrentTab} />
                )}
                {currentTab === 'weak-areas' && (
                  <WeakAreasDashboard />
                )}
                {currentTab === 'admin' && (
                  <AdminDashboard />
                )}
                {currentTab === 'scribe' && (
                  <AnswerWorkbench />
                )}
                {currentTab === 'arena' && (
                  <BossArena onBattleComplete={refreshDashboard} />
                )}
                {(currentTab === 'planner' || currentTab === 'study-plan') && (
                  <StudyPlanDashboard />
                )}
                {currentTab === 'revision-cards' && (
                  <RevisionCards />
                )}
                {currentTab === 'mnemonics' && (
                  <MnemonicGenerator />
                )}
                {currentTab === 'heatmap' && (
                  <PYQHeatmap />
                )}
                {currentTab === 'model-answers' && (
                  <ModelAnswersManager />
                )}
                {currentTab === 'mindmap' && (
                  <MindMapCreator />
                )}
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
              
              {/* Brain Navigation Routes */}
              <Route path="/mock-tests" element={<MockTests onTaskCompleted={refreshDashboard} />} />
              <Route path="/flashcards" element={<FlashcardsManager onTaskCompleted={refreshDashboard} />} />
              <Route path="/study-plan" element={<StudyPlanDashboard />} />
              <Route path="/weak-areas" element={<WeakAreasDashboard />} />
            </Routes>
          </main>

          {/* RITUALS PANEL (Right Column) */}
          <div style={{ zIndex: 15, position: 'relative' }}>
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