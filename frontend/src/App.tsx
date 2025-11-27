// frontend/src/App.tsx
import { useState, useEffect, useCallback } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import './index.css';
import './App.css';
import './animations.css';
import { AnalyticsProvider } from './contexts/AnalyticsContext';
import { PomodoroProvider } from './contexts/PomodoroContext';

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
import MimirChat from './components/Mimir/MimirChat';
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

// --- UTILS ---
import { audioManager } from './util/AudioManager';

// --- TYPES ---
export interface Task {
  id: number;
  title: string;
  isCompleted: boolean;
  xp_reward: number;
  associated_stat: string | null;
  due_date: string;
}

export interface RawTaskFromAPI {
  id: number;
  title: string;
  isCompleted: number;
  xp_reward: number;
  associated_stat: string | null;
  due_date: string;
}

export interface UserStats {
  id: number;
  username: string;
  level: number;
  current_xp: number;
  max_xp: number;
  hacksilver: number;
  strength_stat: number;
  runic_stat: number;
  vitality_stat: number;
  luck_stat: number;
}

function App() {
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [todayTasks, setTodayTasks] = useState<Task[]>([]);
  const location = useLocation();

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Navigation State
  const [currentTab, setCurrentTab] = useState('dashboard');

  // Feature States
  const [isRageMode, setIsRageMode] = useState(false);
  const [showLevelUp, setShowLevelUp] = useState(false);

  const fetchDashboardData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:5000/api/dashboard-data');
      if (!response.ok) throw new Error('Failed to fetch dashboard data');
      const data = await response.json();

      // --- LEVEL UP DETECTION LOGIC ---
      setUserStats((prev) => {
        const newStats = data.stats;
        if (prev && newStats.level > prev.level) {
          audioManager.play('levelup');
          setShowLevelUp(true);
        }
        return newStats;
      });

      // Process Tasks
      const tasksWithBooleanCompletion: Task[] = data.tasks.map((task: RawTaskFromAPI) => ({
        id: task.id,
        title: task.title,
        isCompleted: task.isCompleted === 1,
        xp_reward: task.xp_reward,
        associated_stat: task.associated_stat,
        due_date: task.due_date,
      }));

      setTodayTasks(tasksWithBooleanCompletion);

    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // --- AUDIO & VISUAL EFFECTS FOR RAGE MODE ---
  useEffect(() => {
    if (isRageMode) {
      document.body.classList.add('rage-mode');
      audioManager.startLoop('rage');
    } else {
      document.body.classList.remove('rage-mode');
      audioManager.stopLoop('rage');
    }
  }, [isRageMode]);

  // --- TASK COMPLETION HANDLER ---
  const handleTaskCompleted = useCallback(async () => {
    audioManager.play('success');
    await fetchDashboardData();
  }, [fetchDashboardData]);


  if (isLoading && !userStats) return <div className="loading-screen">Loading the Realms...</div>;
  if (error) return <div className="error-screen">Error: {error}</div>;

  return (
    <AnalyticsProvider>
      <PomodoroProvider onSessionComplete={handleTaskCompleted}>
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
          <Sidebar
            currentTab={currentTab}
            setCurrentTab={setCurrentTab}
          />

          {/* MAIN CONTENT AREA (Middle Column - Z-Index 10) */}
          <main className="content" style={{
            backgroundImage: currentTab === 'dashboard' ? `url(/assets/bg_sidebar.png)` : undefined,
            backgroundSize: 'cover',
            minHeight: '100vh',
            zIndex: 10,
            position: 'relative'
          }}>
            {/* Only render Tab Content if we are on the root path */}
            {location.pathname === '/' && (
              <>
                {currentTab === 'dashboard' && (
                  <DashboardMain
                    stats={userStats!}
                  />
                )}
                {currentTab === 'war-map' && (
                  <WarMapContainer onTaskCompleted={handleTaskCompleted} />
                )}
                {currentTab === 'syllabus' && (
                  <SyllabusTracker onTaskCompleted={handleTaskCompleted} />
                )}
                {currentTab === 'quests' && (
                  <QuestsPage onTaskCompleted={handleTaskCompleted} />
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
                  <AnswerWriting onTaskCompleted={handleTaskCompleted} />
                )}
                {currentTab === 'mock-tests' && (
                  <MockTests onTaskCompleted={handleTaskCompleted} />
                )}
                {currentTab === 'essay' && (
                  <EssayWorkshop onTaskCompleted={handleTaskCompleted} />
                )}
                {currentTab === 'csat' && <CSATModule />}
                {currentTab === 'compilation' && <CompilationGenerator />}
                {currentTab === 'mimir' && <MimirChat />}
                {currentTab === 'flashcards' && (
                  <FlashcardsManager onTaskCompleted={handleTaskCompleted} />
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
                  <BossArena onBattleComplete={handleTaskCompleted} />
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
              <Route path="/boss-arena" element={<BossArena onBattleComplete={handleTaskCompleted} />} />
              <Route path="/timebox" element={<TimeBoxing />} />
              <Route path="/revision-center" element={<RevisionCenter />} />
              <Route path="/mindmap" element={<MindMapCreator />} />
            </Routes>
          </main>

          {/* RITUALS PANEL (Right Column) */}
          <div style={{ zIndex: 15, position: 'relative' }}>
            <RitualsPanel
              tasks={todayTasks}
              onTaskComplete={handleTaskCompleted}
              // FIX: When clicked, switch tab to War Map
              onPlanRituals={() => setCurrentTab('war-map')}
            />
          </div>

          {/* --- OVERLAYS & FLOATING ELEMENTS --- */}

          <SpartanRage onToggleRage={setIsRageMode} />

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
          <CommandPalette setCurrentTab={setCurrentTab} />

        </div>
      </PomodoroProvider>
    </AnalyticsProvider>
  );
}

export default App;