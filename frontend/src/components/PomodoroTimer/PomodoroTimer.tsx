import React, { useState } from 'react';
import './PomodoroTimer.css';
import { usePomodoro } from '../../contexts/PomodoroContext';

interface PomodoroTimerProps {
    onSessionComplete?: () => void;
    className?: string; // Allow custom positioning classes
}

const PomodoroTimer: React.FC<PomodoroTimerProps> = ({ onSessionComplete, className }) => {
    const {
        mode,
        timeLeft,
        isRunning,
        sessionsCompleted,
        toggleTimer,
        resetTimer,
        switchMode,
        setTimeLeft
    } = usePomodoro();

    const [isMinimized, setIsMinimized] = useState(true);
    const [isEditing, setIsEditing] = useState(false);
    const [editMinutes, setEditMinutes] = useState('25');

    const formatTime = (seconds: number): string => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    const getProgress = (): number => {
        // Approximate total duration based on mode for progress bar
        // This might be inaccurate if custom time is set, but sufficient for visual
        let total = 25 * 60;
        if (mode === 'shortBreak') total = 5 * 60;
        if (mode === 'longBreak') total = 15 * 60;

        // If timeLeft is greater than default, use timeLeft as total
        if (timeLeft > total) total = timeLeft;
        if (total === 0) return 0;

        return ((total - timeLeft) / total) * 100;
    };

    const handleEditSave = () => {
        const mins = parseInt(editMinutes);
        if (!isNaN(mins) && mins > 0) {
            setTimeLeft(mins * 60);
            setIsEditing(false);
        }
    };

    if (isMinimized) {
        return (
            <div className={`pomodoro-minimized ${className || ''}`} onClick={() => setIsMinimized(false)}>
                <span className="pomodoro-icon">🍅</span>
                <span className="pomodoro-time">{formatTime(timeLeft)}</span>
            </div>
        );
    }

    return (
        <div className={`pomodoro-widget ${className || ''}`}>
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
                    Short
                </button>
                <button
                    className={`mode-btn ${mode === 'longBreak' ? 'active' : ''}`}
                    onClick={() => switchMode('longBreak')}
                >
                    Long
                </button>
            </div>

            <div className="pomodoro-timer-display">
                <svg className="progress-ring" width="320" height="320">
                    <circle
                        cx="160"
                        cy="160"
                        r="145"
                        fill="none"
                        stroke="#2c3e50"
                        strokeWidth="12"
                    />
                    <circle
                        cx="160"
                        cy="160"
                        r="145"
                        fill="none"
                        stroke={mode === 'work' ? '#e74c3c' : '#2ecc71'}
                        strokeWidth="12"
                        strokeDasharray={`${2 * Math.PI * 145}`}
                        strokeDashoffset={`${2 * Math.PI * 145 * (1 - getProgress() / 100)}`}
                        transform="rotate(-90 160 160)"
                        strokeLinecap="round"
                    />
                </svg>

                {isEditing ? (
                    <div className="timer-edit-overlay">
                        <input
                            type="number"
                            value={editMinutes}
                            onChange={(e) => setEditMinutes(e.target.value)}
                            className="timer-edit-input"
                            min="1"
                            max="120"
                        />
                        <div className="timer-edit-actions">
                            <button onClick={handleEditSave} className="save-btn">✓</button>
                            <button onClick={() => setIsEditing(false)} className="cancel-btn">✕</button>
                        </div>
                    </div>
                ) : (
                    <div className="timer-text-container">
                        <div className="timer-text">
                            {formatTime(timeLeft)}
                        </div>
                        {!isRunning && (
                            <button
                                className="edit-time-btn"
                                onClick={() => {
                                    setEditMinutes(Math.floor(timeLeft / 60).toString());
                                    setIsEditing(true);
                                }}
                                title="Edit Timer"
                            >
                                ✎
                            </button>
                        )}
                    </div>
                )}
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
                    <span className="stat-label">Sessions:</span>
                    <span className="stat-value">{sessionsCompleted}</span>
                </div>
                <div className="stat-item">
                    <span className="stat-label">XP:</span>
                    <span className="stat-value">+{sessionsCompleted * 50}</span>
                </div>
            </div>
        </div>
    );
};

export default PomodoroTimer;
