// frontend/src/App.tsx
import { Routes, Route, useLocation } from 'react-router-dom';
import './index.css';
import './App.css';
import './animations.css';
import { AnalyticsProvider } from './contexts/AnalyticsContext';
import { PomodoroProvider } from './contexts/PomodoroContext';
import { useGlobal } from './contexts/GlobalContext';

// --- COMPONENT IMPORTS ---
import Sidebar from './components/Sidebar';
import DashboardMain from './components/DashboardMain';
import WarMapContainer from './components/WarMap/WarMapContainer';
import SyllabusTracker from './components/Syllabus/SyllabusTracker';
import WeakAreasDashboard from './components/WeakAreas/WeakAreasDashboard';
import AdminDashboard from './components/Admin/AdminDashboard';
import QuestsPage from './components/Quests/QuestsPage';
import RitualsPanel from './components/RitualsPanel';
import AshParticles from './components/AshParticles';
import SpartanRage from './components/SpartanRage/SpartanRage';
import YggdrasilTree from './components/Yggdrasil/Yggdrasil';
import LoreTablets from './components/LoreTablets/LoreTablets';
import PYQDatabase from './components/PYQ/PYQDatabase';
import QuizSession from './components/PYQ/QuizSession';
import QuizResults from './components/PYQ/QuizResults';
import Armory from './components/Armory/Armory';

import LevelUpModal from './components/LevelUpModal';
import AnkiDojo from './components/AnkiDojo/AnkiDojo';
import Seer from './components/Seer/Seer';
import Ravens from './components/Ravens/Ravens';
import AnswerWriting from './components/AnswerWriting/AnswerWriting';
import MockTests from './components/MockTests/MockTests';
import EssayWorkshop from './components/Essay/EssayWorkshop';
import CSATModule from './components/CSAT/CSATModule';
import MimirChat from './components/Mimir/Mimir';
import FlashcardsManager from './components/Flashcards/FlashcardsManager';
import AnalyticsDashboard from './components/Analytics/AnalyticsDashboard';
import AnswerWorkbench from './components/Scribe/AnswerWorkbench';
import BossArena from './components/BossArena/BossArena';
import PomodoroTimer from './components/PomodoroTimer/PomodoroTimer';
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
                {currentTab === 'mimir' && <MimirChat />}
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
            </Routes>
          </main>

          {/* RITUALS PANEL (Right Column) */}
          <div style={{ zIndex: 15, position: 'relative' }}>
            <RitualsPanel />
          </div>

          {/* --- OVERLAYS & FLOATING ELEMENTS --- */}

          <SpartanRage />

          {/* Floating Mimir - Always visible */}
          <MimirChat mode="floating" />

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

        </div>
      </PomodoroProvider>
    </AnalyticsProvider>
  );
}

export default App;