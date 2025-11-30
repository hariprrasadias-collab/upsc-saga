import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { ReactNode } from 'react';

type TimerMode = 'work' | 'shortBreak' | 'longBreak';

export interface PomodoroSession {
    id: string;
    taskId?: string;
    taskTitle?: string;
    duration: number;
    timestamp: string;
    mode: TimerMode;
}

export interface PomodoroPreset {
    id: string;
    name: string;
    icon: string;
    workDuration: number; // minutes
    shortBreakDuration: number;
    longBreakDuration: number;
    sessionsUntilLongBreak: number;
}

export interface PomodoroSettings {
    autoStartBreaks: boolean;
    autoStartPomodoros: boolean;
    autoStartDelay: number;
    notifications: boolean;
    sound: boolean;
    activePresetId: string;
}

interface PomodoroContextType {
    mode: TimerMode;
    timeLeft: number;
    isRunning: boolean;
    sessionsCompleted: number;
    totalStudyTime: number;
    currentTask: { id: string; title: string } | null;
    settings: PomodoroSettings;
    presets: PomodoroPreset[];
    activePreset: PomodoroPreset;
    toggleTimer: () => void;
    resetTimer: () => void;
    switchMode: (newMode: TimerMode) => void;
    setSessionsCompleted: (n: number) => void;
    setTimeLeft: (seconds: number) => void;
    startTask: (taskId: string, title: string, durationMinutes?: number, isBreak?: boolean) => void;
    updateSettings: (settings: Partial<PomodoroSettings>) => void;
    setActivePreset: (id: string) => void;
}

const PomodoroContext = createContext<PomodoroContextType | undefined>(undefined);

export const usePomodoro = () => {
    const context = useContext(PomodoroContext);
    if (!context) {
        throw new Error('usePomodoro must be used within a PomodoroProvider');
    }
    return context;
};

interface PomodoroProviderProps {
    children: ReactNode;
    onSessionComplete?: () => void;
}

// Default Presets
const DEFAULT_PRESETS: PomodoroPreset[] = [
    { id: 'classic', name: 'Classic', icon: '🍅', workDuration: 25, shortBreakDuration: 5, longBreakDuration: 15, sessionsUntilLongBreak: 4 },
    { id: 'deep-work', name: 'Deep Work', icon: '🧠', workDuration: 90, shortBreakDuration: 20, longBreakDuration: 30, sessionsUntilLongBreak: 2 },
    { id: 'quick-sprint', name: 'Quick Sprint', icon: '⚡', workDuration: 15, shortBreakDuration: 3, longBreakDuration: 10, sessionsUntilLongBreak: 6 },
    { id: 'study', name: 'Study Session', icon: '📚', workDuration: 50, shortBreakDuration: 10, longBreakDuration: 20, sessionsUntilLongBreak: 3 },
    { id: 'ultra', name: 'Ultra Focus', icon: '🎯', workDuration: 120, shortBreakDuration: 25, longBreakDuration: 40, sessionsUntilLongBreak: 2 }
];

export const PomodoroProvider: React.FC<PomodoroProviderProps> = ({ children, onSessionComplete }) => {
    const [presets] = useState<PomodoroPreset[]>(DEFAULT_PRESETS);
    const [settings, setSettings] = useState<PomodoroSettings>({
        autoStartBreaks: false,
        autoStartPomodoros: false,
        autoStartDelay: 5,
        notifications: true,
        sound: true,
        activePresetId: 'classic'
    });

    const activePreset = presets.find(p => p.id === settings.activePresetId) || presets[0];

    const [mode, setMode] = useState<TimerMode>('work');
    const [timeLeft, setTimeLeft] = useState(activePreset.workDuration * 60);
    const [isRunning, setIsRunning] = useState(false);
    const [sessionsCompleted, setSessionsCompleted] = useState(0);
    const [totalStudyTime, setTotalStudyTime] = useState(0);
    const [currentTask, setCurrentTask] = useState<{ id: string; title: string } | null>(null);

    const DURATIONS = {
        work: activePreset.workDuration * 60,
        shortBreak: activePreset.shortBreakDuration * 60,
        longBreak: activePreset.longBreakDuration * 60
    };

    // Load initial data
    useEffect(() => {
        const sessions = JSON.parse(localStorage.getItem('pomodoro_sessions') || '[]');
        const total = sessions.reduce((acc: number, s: PomodoroSession) =>
            s.mode === 'work' ? acc + s.duration : acc, 0);
        setTotalStudyTime(total);
        setSessionsCompleted(sessions.filter((s: PomodoroSession) => s.mode === 'work').length);

        const savedSettings = localStorage.getItem('pomodoro_settings');
        if (savedSettings) {
            setSettings(JSON.parse(savedSettings));
        }
    }, []);

    const handleTimerComplete = useCallback(async () => {
        setIsRunning(false);
        const duration = DURATIONS[mode];

        const session: PomodoroSession = {
            id: Date.now().toString(),
            taskId: currentTask?.id,
            taskTitle: currentTask?.title,
            duration,
            timestamp: new Date().toISOString(),
            mode
        };

        const sessions = JSON.parse(localStorage.getItem('pomodoro_sessions') || '[]');
        sessions.push(session);
        localStorage.setItem('pomodoro_sessions', JSON.stringify(sessions));

        if (mode === 'work') {
            setSessionsCompleted(prev => prev + 1);
            setTotalStudyTime(prev => prev + duration);
            window.dispatchEvent(new Event('pomodoroUpdate'));
            if (onSessionComplete) onSessionComplete();
        }

        if (settings.notifications && 'Notification' in window && Notification.permission === 'granted') {
            new Notification('Pomodoro Timer', {
                body: mode === 'work' ? 'Victory! Task complete.' : 'Respite over. Back to battle.',
                icon: '/pomodoro-icon.png'
            });
        }

        if ((mode === 'work' && settings.autoStartBreaks) || (mode !== 'work' && settings.autoStartPomodoros)) {
            setTimeout(() => {
                const nextMode: TimerMode = mode === 'work'
                    ? (sessionsCompleted % activePreset.sessionsUntilLongBreak === activePreset.sessionsUntilLongBreak - 1 ? 'longBreak' : 'shortBreak')
                    : 'work';
                setMode(nextMode);
                setTimeLeft(DURATIONS[nextMode]);
                setIsRunning(true);
            }, settings.autoStartDelay * 1000);
        }
    }, [mode, currentTask, onSessionComplete, DURATIONS, settings, sessionsCompleted, activePreset]);

    useEffect(() => {
        let interval: number | null = null;
        if (isRunning && timeLeft > 0) {
            interval = window.setInterval(() => setTimeLeft(prev => prev - 1), 1000);
        } else if (timeLeft === 0) {
            handleTimerComplete();
        }
        return () => { if (interval) clearInterval(interval); };
    }, [isRunning, timeLeft, handleTimerComplete]);

    const toggleTimer = () => {
        if (!isRunning && 'Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
        setIsRunning(!isRunning);
    };

    const resetTimer = () => {
        setIsRunning(false);
        setTimeLeft(DURATIONS[mode]);
    };

    const switchMode = (newMode: TimerMode) => {
        setMode(newMode);
        setTimeLeft(DURATIONS[newMode]);
        setIsRunning(false);
        setCurrentTask(null);
    };

    const startTask = (taskId: string, title: string, durationMinutes?: number, isBreak?: boolean) => {
        const newMode = isBreak ? 'shortBreak' : 'work';
        setMode(newMode);
        setTimeLeft(durationMinutes ? durationMinutes * 60 : DURATIONS[newMode]);
        setCurrentTask({ id: taskId, title });
        setIsRunning(true);
    };

    const updateSettings = (newSettings: Partial<PomodoroSettings>) => {
        const updated = { ...settings, ...newSettings };
        setSettings(updated);
        localStorage.setItem('pomodoro_settings', JSON.stringify(updated));
    };

    const setActivePreset = (id: string) => {
        updateSettings({ activePresetId: id });
        const preset = presets.find(p => p.id === id);
        if (preset) {
            if (mode === 'work') setTimeLeft(preset.workDuration * 60);
            else if (mode === 'shortBreak') setTimeLeft(preset.shortBreakDuration * 60);
            else if (mode === 'longBreak') setTimeLeft(preset.longBreakDuration * 60);
        }
    };

    return (
        <PomodoroContext.Provider value={{
            mode,
            timeLeft,
            isRunning,
            sessionsCompleted,
            totalStudyTime,
            currentTask,
            settings,
            presets,
            activePreset,
            toggleTimer,
            resetTimer,
            switchMode,
            setSessionsCompleted,
            setTimeLeft,
            startTask,
            updateSettings,
            setActivePreset
        }}>
            {children}
        </PomodoroContext.Provider>
    );
};
