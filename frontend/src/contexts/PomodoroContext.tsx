import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { ReactNode } from 'react';

type TimerMode = 'work' | 'shortBreak' | 'longBreak';

interface PomodoroContextType {
    mode: TimerMode;
    timeLeft: number;
    isRunning: boolean;
    sessionsCompleted: number;
    toggleTimer: () => void;
    resetTimer: () => void;
    switchMode: (newMode: TimerMode) => void;
    setSessionsCompleted: (n: number) => void;
    setTimeLeft: (seconds: number) => void;
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

export const PomodoroProvider: React.FC<PomodoroProviderProps> = ({ children, onSessionComplete }) => {
    const [mode, setMode] = useState<TimerMode>('work');
    const [timeLeft, setTimeLeft] = useState(25 * 60);
    const [isRunning, setIsRunning] = useState(false);
    const [sessionsCompleted, setSessionsCompleted] = useState(0);

    const DURATIONS = {
        work: 25 * 60,
        shortBreak: 5 * 60,
        longBreak: 15 * 60
    };

    const handleTimerComplete = useCallback(async () => {
        setIsRunning(false);

        if (mode === 'work') {
            const newSessions = sessionsCompleted + 1;
            setSessionsCompleted(newSessions);

            // Award XP
            try {
                await fetch('http://localhost:5000/api/pomodoro/complete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        duration: DURATIONS.work,
                        timestamp: new Date().toISOString()
                    })
                });

                if (onSessionComplete) onSessionComplete();
            } catch (err) {
                console.error('Failed to log Pomodoro:', err);
            }

            // Switch to break
            if (newSessions % 4 === 0) {
                setMode('longBreak');
                setTimeLeft(DURATIONS.longBreak);
            } else {
                setMode('shortBreak');
                setTimeLeft(DURATIONS.shortBreak);
            }
        } else {
            // Back to work
            setMode('work');
            setTimeLeft(DURATIONS.work);
        }

        // Notification
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Pomodoro Timer', {
                body: mode === 'work' ? 'Work session complete! Take a break.' : 'Break over! Back to work.',
                icon: '/pomodoro-icon.png'
            });
        }
    }, [mode, sessionsCompleted, onSessionComplete]);

    useEffect(() => {
        let interval: number | null = null;

        if (isRunning && timeLeft > 0) {
            interval = window.setInterval(() => {
                setTimeLeft(prev => prev - 1);
            }, 1000);
        } else if (timeLeft === 0) {
            handleTimerComplete();
        }

        return () => {
            if (interval) clearInterval(interval);
        };
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
    };

    return (
        <PomodoroContext.Provider value={{
            mode,
            timeLeft,
            isRunning,
            sessionsCompleted,
            toggleTimer,
            resetTimer,
            switchMode,
            setSessionsCompleted,
            setTimeLeft
        }}>
            {children}
        </PomodoroContext.Provider>
    );
};
