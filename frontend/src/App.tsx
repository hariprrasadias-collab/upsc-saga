// frontend/src/App.tsx
import { useState, useEffect, useCallback } from 'react';
// Remove react-router-dom import if not used or not installed
import './index.css'; // Global styles and fonts
import './App.css'; // App-specific styles including background
import Sidebar from './components/Sidebar';
import DashboardMain from './components/DashboardMain';
import WarMapContainer from './components/WarMap/WarMapContainer';
import QuestsPage from './components/Quests/QuestsPage';
import RitualsPanel from './components/RitualsPanel';

// Define Task and RawTaskFromAPI interfaces here for now
export interface Task {
  id: number;
  title: string;
  isCompleted: boolean;
  xp_reward: number;
  associated_stat: string | null;
  due_date: string; // YYYY-MM-DD
}

export interface RawTaskFromAPI {
  id: number;
  title: string;
  isCompleted: number; // 0 or 1 from API
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
  strength_stat: number;
  runic_stat: number;
  vitality_stat: number;
  luck_stat: number;
}

function App() {
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [todayTasks, setTodayTasks] = useState<Task[]>([]);
  const [ankiDueCount, setAnkiDueCount] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Tab state for sidebar navigation (must be before any conditional returns)
  const [currentTab, setCurrentTab] = useState('dashboard');

  const fetchDashboardData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:5000/api/dashboard-data');
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data');
      }
      const data = await response.json();

      setUserStats(data.stats);

      // Convert isCompleted from 0/1 to boolean for frontend consistency
      const tasksWithBooleanCompletion: Task[] = data.tasks.map((task: RawTaskFromAPI) => ({
        id: task.id,
        title: task.title,
        isCompleted: task.isCompleted === 1,
        xp_reward: task.xp_reward,
        associated_stat: task.associated_stat,
        due_date: task.due_date,
      }));
      setTodayTasks(tasksWithBooleanCompletion);
      setAnkiDueCount(data.anki_due);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unknown error occurred while fetching dashboard data.");
      }
      console.error('Error fetching dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Handle task completion from Dashboard and QuestsPage
  const handleTaskCompleted = useCallback(async () => {
    await fetchDashboardData(); // Re-fetch all dashboard data to update stats and tasks
  }, [fetchDashboardData]);


  if (isLoading) {
    return (
      <div className="loading-screen">
        <p>Loading your adventure...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-screen">
        <p>Error: {error}</p>
        <p>Please ensure your Flask backend is running (`python app.py` in the backend folder).</p>
      </div>
    );
  }


  return (
    <div className="app-container" style={{
      backgroundImage: `url(/assets/bg_main.jpg)`,
      backgroundSize: 'cover',
      minHeight: '100vh',
    }}>
      <Sidebar
        currentTab={currentTab}
        onTabChange={setCurrentTab}
        userStats={userStats}
        ankiDueCount={ankiDueCount}
      />
      <main className="content" style={{
        backgroundImage: currentTab === 'dashboard' ? `url(/assets/bg_sidebar.png)` : undefined,
        backgroundSize: 'cover',
        minHeight: '100vh',
      }}>
        {currentTab === 'dashboard' && (
          <DashboardMain
            stats={userStats ?? {
              id: 0,
              username: '',
              level: 1,
              current_xp: 0,
              max_xp: 100,
              strength_stat: 0,
              runic_stat: 0,
              vitality_stat: 0,
              luck_stat: 0,
            }}
          />
        )}
        {currentTab === 'war-map' && (
          <WarMapContainer onTaskCompleted={handleTaskCompleted} />
        )}
        {currentTab === 'quests' && (
          <QuestsPage onTaskCompleted={handleTaskCompleted} />
        )}
        {/* Add more tab content here as needed */}
      </main>
      <RitualsPanel
        tasks={todayTasks}
        onTaskComplete={handleTaskCompleted}
      />
    </div>
  );
}

export default App;