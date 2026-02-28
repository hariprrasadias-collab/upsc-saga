import React, { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { audioManager } from '../util/AudioManager';
import { API_BASE_URL } from '../config';

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

interface GlobalContextType {
    userStats: UserStats | null;
    todayTasks: Task[];
    currentTab: string;
    isRageMode: boolean;
    showLevelUp: boolean;
    isLoading: boolean;
    error: string | null;

    setCurrentTab: (tab: string) => void;
    toggleRageMode: () => void;
    setIsRageMode: (isRage: boolean) => void;
    setShowLevelUp: (show: boolean) => void;
    refreshDashboard: () => Promise<void>;
    completeTask: (taskId: number) => Promise<void>;
    isSidebarOpen: boolean;
    toggleSidebar: () => void;
    isRitualsOpen: boolean;
    toggleRituals: () => void;
    isMimirOpen: boolean;
    toggleMimir: (isOpen?: boolean) => void;
}

const GlobalContext = createContext<GlobalContextType | undefined>(undefined);

export const useGlobal = () => {
    const context = useContext(GlobalContext);
    if (!context) {
        throw new Error('useGlobal must be used within a GlobalProvider');
    }
    return context;
};

interface GlobalProviderProps {
    children: ReactNode;
}

export const GlobalProvider: React.FC<GlobalProviderProps> = ({ children }) => {
    const [userStats, setUserStats] = useState<UserStats | null>(null);
    const [todayTasks, setTodayTasks] = useState<Task[]>([]);
    const [currentTab, setCurrentTab] = useState('dashboard');
    const [isRageMode, setIsRageMode] = useState(false);
    const [showLevelUp, setShowLevelUp] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const [isRitualsOpen, setIsRitualsOpen] = useState(false);
    const [isMimirOpen, setIsMimirOpen] = useState(false);

    const toggleSidebar = () => setIsSidebarOpen(prev => !prev);
    const toggleRituals = () => setIsRitualsOpen(prev => !prev);
    const toggleMimir = (isOpen?: boolean) => setIsMimirOpen(prev => isOpen !== undefined ? isOpen : !prev);

    // Refined fetchDashboardData to avoid dependency issues
    const refreshDashboard = useCallback(async () => {
        // We can't easily check current userStats here without adding it to dependency, 
        // but we can just set isLoading(true) if we want the App.tsx behavior.
        // Let's try to NOT show full screen loading on refresh.
        // We will handle "initial load" separately.

        try {
            const response = await fetch(`${API_BASE_URL}/api/dashboard-data`);
            if (!response.ok) throw new Error('Failed to fetch dashboard data');
            const responseData = await response.json();
            const data = responseData.data || responseData;

            if (data.stats) {
                setUserStats((prev) => {
                    const newStats = data.stats;
                    if (prev && newStats.level > prev.level) {
                        audioManager.play('levelup');
                        setShowLevelUp(true);
                    }
                    return newStats;
                });
            }

            if (data.tasks && Array.isArray(data.tasks)) {
                const tasksWithBooleanCompletion: Task[] = data.tasks.map((task: RawTaskFromAPI) => ({
                    id: task.id,
                    title: task.title,
                    isCompleted: task.isCompleted === 1,
                    xp_reward: task.xp_reward,
                    associated_stat: task.associated_stat,
                    due_date: task.due_date,
                }));
                setTodayTasks(tasksWithBooleanCompletion);
            } else {
                setTodayTasks([]);
            }
        } catch (err) {
            console.error("Error refreshing dashboard:", err);
            setError(err instanceof Error ? err.message : "Unknown error");
        }
    }, []);

    // Initial Load
    useEffect(() => {
        const init = async () => {
            setIsLoading(true);
            await refreshDashboard();
            setIsLoading(false);
        };
        init();

        // Restore Rage Mode from local storage
        const savedRage = localStorage.getItem('isRageMode');
        if (savedRage === 'true') {
            setIsRageMode(true);
        }
    }, [refreshDashboard]);

    // --- AUDIO & VISUAL EFFECTS FOR RAGE MODE ---
    useEffect(() => {
        if (isRageMode) {
            document.body.classList.add('rage-mode');
            audioManager.startLoop('rage');
            localStorage.setItem('isRageMode', 'true');
        } else {
            document.body.classList.remove('rage-mode');
            audioManager.stopLoop('rage');
            localStorage.setItem('isRageMode', 'false');
        }
    }, [isRageMode]);

    const toggleRageMode = () => setIsRageMode(prev => !prev);

    const completeTask = async (taskId: number) => {
        try {
            // Updated to correct route based on verification
            const response = await fetch(`${API_BASE_URL}/api/planner/task/${taskId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status: 'Completed' })
            });

            if (!response.ok) {
                throw new Error('Failed to complete task');
            }

            audioManager.play('success');
            await refreshDashboard();
        } catch (err) {
            console.error('Error completing task:', err);
            // Optionally show toast or alert
        }
    };

    const value: GlobalContextType = React.useMemo(() => ({
        userStats,
        todayTasks,
        currentTab,
        isRageMode,
        showLevelUp,
        isLoading,
        error,
        setCurrentTab,
        toggleRageMode,
        setIsRageMode,
        setShowLevelUp,
        refreshDashboard,
        completeTask,
        isSidebarOpen,
        toggleSidebar,
        isRitualsOpen,
        toggleRituals,
        isMimirOpen,
        toggleMimir
    }), [
        userStats,
        todayTasks,
        currentTab,
        isRageMode,
        showLevelUp,
        isLoading,
        error,
        refreshDashboard,
        isSidebarOpen,
        isRitualsOpen,
        isMimirOpen
    ]);

    return (
        <GlobalContext.Provider value={value}>
            {children}
        </GlobalContext.Provider>
    );
};
