import React, { useState, useEffect } from 'react';
import './PomodoroTimer.css';

type TimerMode = 'work' | 'shortBreak' | 'longBreak';

interface PomodoroTimerProps {
    onSessionComplete?: () => void;
}

const PomodoroTimer: React.FC<PomodoroTimerProps> = ({ onSessionComplete }) => {
    const [mode, setMode] = useState<TimerMode>('work');
    const [timeLeft, setTimeLeft] = useState(25 * 60); // 25 minutes
    const [isRunning, setIsRunning] = useState(false);
    const [sessionsCompleted, setSessionsCompleted] = useState(0);
    const [isMinimized, setIsMinimized] = useState(false);

    const DURATIONS = {
        work: 25 * 60,
        shortBreak: 5 * 60,
        longBreak: 15 * 60
    };

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
    }, [isRunning, timeLeft]);

    const handleTimerComplete = async () => {
        setIsRunning(false);

        if (mode === 'work') {
            const newSessions = sessionsCompleted + 1;
            setSessionsCompleted(newSessions);

            // Award XP for completed Pomodoro
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

            // Switch to break (long break every 4 sessions)
            if (newSessions % 4 === 0) {
                setMode('longBreak');
                setTimeLeft(DURATIONS.longBreak);
            } else {
                setMode('shortBreak');
                setTimeLeft(DURATIONS.shortBreak);
            }
        } else {
            // Back to work after break
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
    };

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

    const formatTime = (seconds: number): string => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    const getProgress = (): number => {
        return ((DURATIONS[mode] - timeLeft) / DURATIONS[mode]) * 100;
    };

    if (isMinimized) {
        return (
            <div className="pomodoro-minimized" onClick={() => setIsMinimized(false)}>
                <span className="pomodoro-icon">🍅</span>
                <span className="pomodoro-time">{formatTime(timeLeft)}</span>
            </div>
        );
    }

    return (
        <div className="pomodoro-widget">
            <div className="pomodoro-header">
                <h3>🍅 Pomodoro</h3>
                <div className="pomodoro-controls">
                    <button onClick={() => setIsMinimized(true)} className="minimize-btn">−</button>
                </div>
            </div>

            <div className="pomodoro-modes">
                <button
                    className={`mode-btn ${mode === 'work' ? 'active' : ''}`}
                    onClick={() => switchMode('work')}
                >
                    Work
                </button>
                <button
                    className={`mode-btn ${mode === 'shortBreak' ? 'active' : ''}`}
                    onClick={() => switchMode('shortBreak')}
                >
                    Short Break
                </button>
                <button
                    className={`mode-btn ${mode === 'longBreak' ? 'active' : ''}`}
                    onClick={() => switchMode('longBreak')}
                >
                    Long Break
                </button>
            </div>

            <div className="pomodoro-timer-display">
                <svg className="progress-ring" width="200" height="200">
                    <circle
                        cx="100"
                        cy="100"
                        r="85"
                        fill="none"
                        stroke="#2c3e50"
                        strokeWidth="8"
                    />
                    <circle
                        cx="100"
                        cy="100"
                        r="85"
                        fill="none"
                        stroke={mode === 'work' ? '#e74c3c' : '#2ecc71'}
                        strokeWidth="8"
                        strokeDasharray={`${2 * Math.PI * 85}`}
                        strokeDashoffset={`${2 * Math.PI * 85 * (1 - getProgress() / 100)}`}
                        transform="rotate(-90 100 100)"
                        strokeLinecap="round"
                    />
                </svg>
                <div className="timer-text">
                    {formatTime(timeLeft)}
                </div>
            </div>

            <div className="pomodoro-actions">
                <button
                    className={`timer-btn ${isRunning ? 'pause' : 'start'}`}
                    onClick={toggleTimer}
                >
                    {isRunning ? '⏸ Pause' : '▶ Start'}
                </button>
                <button className="reset-btn" onClick={resetTimer}>
                    ↻ Reset
                </button>
            </div>

            <div className="pomodoro-stats">
                <div className="stat-item">
                    <span className="stat-label">Sessions Today:</span>
                    <span className="stat-value">{sessionsCompleted}</span>
                </div>
                <div className="stat-item">
                    <span className="stat-label">XP Earned:</span>
                    <span className="stat-value">+{sessionsCompleted * 50}</span>
                </div>
            </div>
        </div>
    );
};

export default PomodoroTimer;
