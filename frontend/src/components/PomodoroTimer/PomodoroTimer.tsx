import React, { useState, useEffect, useRef } from 'react';
import './PomodoroTimer.css';
import './pomodoro-enhancements.css';
import './ui-polish.css';
import './visual-enhancements.css';
import './advanced-refinements.css';
import './ultra-premium.css';
import './timer-visibility-fix.css';
import './flip-board-timer.css';
import { usePomodoro } from '../../contexts/PomodoroContext';
import { audioManager } from '../../util/AudioManager';
import { AmbientSoundPlayer } from './AmbientSoundPlayer';

import { SessionHistory } from './SessionHistory';

// Internal FlipCard Component
const FlipCard = ({ digit }: { digit: string }) => {
    const [prevDigit, setPrevDigit] = useState(digit);
    const [flipping, setFlipping] = useState(false);

    useEffect(() => {
        if (digit !== prevDigit) {
            setFlipping(true);
            const timer = setTimeout(() => {
                setFlipping(false);
                setPrevDigit(digit);
            }, 600);
            return () => clearTimeout(timer);
        }
    }, [digit, prevDigit]);

    return (
        <div className={`flip-card ${flipping ? 'flipping' : ''}`}>
            {/* Static Layers */}
            <div className="flip-card-layer flip-card-top">
                <div className="flip-card-digit">{digit}</div>
            </div>
            <div className="flip-card-layer flip-card-bottom">
                <div className="flip-card-digit">{prevDigit}</div>
            </div>

            {/* Flipping Layers */}
            <div className="flip-card-layer flip-card-top-flip">
                <div className="flip-card-digit">{prevDigit}</div>
            </div>
            <div className="flip-card-layer flip-card-bottom-flip">
                <div className="flip-card-digit">{digit}</div>
            </div>
        </div>
    );
};

interface PomodoroTimerProps {
    onSessionComplete?: () => void;
    className?: string;
}

const PomodoroTimer: React.FC<PomodoroTimerProps> = ({ className }) => {
    const {
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
        setTimeLeft,
        updateSettings,
        setActivePreset
    } = usePomodoro();

    const [isMinimized, setIsMinimized] = useState(true);
    const [isEditing, setIsEditing] = useState(false);
    const [editMinutes, setEditMinutes] = useState('25');
    const [showSettings, setShowSettings] = useState(false);
    const [showHistory, setShowHistory] = useState(false);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [showConfetti, setShowConfetti] = useState(false);
    const [notifiedAt, setNotifiedAt] = useState<Set<number>>(new Set());

    const wasRunningRef = useRef(isRunning);
    const prevTimeRef = useRef(timeLeft);

    useEffect(() => {
        const originalTitle = document.title;
        if (isRunning && !isMinimized) {
            document.title = `${formatTime(timeLeft)} - ${mode === 'work' ? '⚔️ Focus' : '🛡️ Break'}`;
        } else {
            document.title = originalTitle;
        }
        return () => { document.title = originalTitle; };
    }, [isRunning, timeLeft, mode, isMinimized]);

    useEffect(() => {
        if (!isRunning || !settings.notifications) return;
        const total = mode === 'work' ? 25 * 60 : mode === 'shortBreak' ? 5 * 60 : 15 * 60;
        const progress = ((total - timeLeft) / total) * 100;

        if (progress >= 25 && !notifiedAt.has(25)) {
            new Notification('Pomodoro', { body: '25% complete - Keep going!' });
            setNotifiedAt(prev => new Set(prev).add(25));
        } else if (progress >= 50 && !notifiedAt.has(50)) {
            new Notification('Pomodoro', { body: 'Halfway there! 🔥' });
            setNotifiedAt(prev => new Set(prev).add(50));
        } else if (progress >= 75 && !notifiedAt.has(75)) {
            new Notification('Pomodoro', { body: 'Almost done! 💪' });
            setNotifiedAt(prev => new Set(prev).add(75));
        }
    }, [timeLeft, isRunning, mode, settings.notifications, notifiedAt]);

    useEffect(() => {
        setNotifiedAt(new Set());
    }, [mode]);

    useEffect(() => {
        const handleKeyPress = (e: KeyboardEvent) => {
            if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;

            if (e.code === 'Space') {
                e.preventDefault();
                toggleTimer();
            } else if (e.code === 'KeyR') {
                e.preventDefault();
                resetTimer();
            } else if (e.code === 'Digit1') {
                e.preventDefault();
                switchMode('work');
            } else if (e.code === 'Digit2') {
                e.preventDefault();
                switchMode('shortBreak');
            } else if (e.code === 'Digit3') {
                e.preventDefault();
                switchMode('longBreak');
            } else if (e.code === 'KeyS') {
                e.preventDefault();
                setShowSettings(prev => !prev);
            }
        };

        window.addEventListener('keydown', handleKeyPress);
        return () => window.removeEventListener('keydown', handleKeyPress);
    }, [toggleTimer, resetTimer, switchMode]);

    useEffect(() => {
        if (isRunning && !wasRunningRef.current) {
            audioManager.play('click');
        } else if (!isRunning && wasRunningRef.current && timeLeft > 0) {
            audioManager.play('click');
        }
        wasRunningRef.current = isRunning;

        if (timeLeft === 0 && prevTimeRef.current > 0) {
            audioManager.play('success');
            if (mode === 'work') {
                setShowConfetti(true);
                setTimeout(() => setShowConfetti(false), 3000);
            }
        }
        prevTimeRef.current = timeLeft;
    }, [isRunning, timeLeft, mode]);

    const formatTime = (seconds: number): string => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    const formatTotalTime = (seconds: number): string => {
        const hours = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${mins}m`;
    };

    const getProgress = (): number => {
        let total = 25 * 60;
        if (mode === 'shortBreak') total = 5 * 60;
        if (mode === 'longBreak') total = 15 * 60;
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
                <div className={`pomodoro-orb ${isRunning ? 'pulsing' : ''}`}>
                    <span className="pomodoro-icon">{mode === 'work' ? '⚔️' : '🛡️'}</span>
                </div>
                <span className="pomodoro-time">{formatTime(timeLeft)}</span>
                <span className="keyboard-hint" title="Keyboard: Space=Play/Pause, R=Reset, 1/2/3=Modes, S=Settings">⌨️</span>
            </div>
        );
    }

    return (
        <div className={`pomodoro-widget ${className || ''} ${isFullscreen ? 'fullscreen' : ''}`}>
            {showConfetti && (
                <div className="confetti-container">
                    {[...Array(50)].map((_, i) => (
                        <div key={i} className="confetti" style={{
                            left: `${Math.random() * 100}%`,
                            animationDelay: `${Math.random() * 0.5}s`,
                            backgroundColor: ['#f1c40f', '#e74c3c', '#3498db', '#2ecc71', '#9b59b6'][Math.floor(Math.random() * 5)]
                        }} />
                    ))}
                </div>
            )}

            <div className="pomodoro-header">
                <h3>{mode === 'work' ? '⚔️ BATTLE TIME' : '🛡️ RESPITE'}</h3>
                <div className="pomodoro-controls">
                    <button aria-label={isFullscreen ? "Exit Fullscreen" : "Fullscreen"} onClick={() => setIsFullscreen(!isFullscreen)} className="settings-btn" title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}>
                        {isFullscreen ? '↙️' : '⛶'}
                    </button>
                    {isFullscreen && (
                        <button aria-label="Close Fullscreen" onClick={() => setIsFullscreen(false)} className="settings-btn close-fullscreen" title="Close">✕</button>
                    )}
                    <button aria-label="Toggle History" onClick={() => setShowHistory(!showHistory)} className="settings-btn" title="History">📊</button>
                    <button aria-label="Toggle Settings" onClick={() => setShowSettings(!showSettings)} className="settings-btn" title="Settings">⚙️</button>
                    <button aria-label="Minimize Timer" onClick={() => setIsMinimized(true)} className="minimize-btn" title="Minimize">−</button>
                </div>
            </div>

            {currentTask && (
                <div className="current-task-display">
                    <span className="task-label">CURRENT OBJECTIVE:</span>
                    <span className="task-title">{currentTask.title}</span>
                </div>
            )}

            <div className="preset-selector">
                <span className="preset-label">PRESET:</span>
                <div className="preset-options">
                    {presets.map(preset => (
                        <button
                            key={preset.id}
                            className={`preset-btn ${activePreset.id === preset.id ? 'active' : ''}`}
                            onClick={() => !isRunning && setActivePreset(preset.id)}
                            disabled={isRunning}
                            title={`${preset.name}: ${preset.workDuration}/${preset.shortBreakDuration}/${preset.longBreakDuration}min`}
                        >
                            <span className="preset-icon">{preset.icon}</span>
                            <span className="preset-name">{preset.name}</span>
                        </button>
                    ))}
                </div>
            </div>

            <div className="pomodoro-modes">
                <button className={`mode-btn ${mode === 'work' ? 'active' : ''}`} onClick={() => switchMode('work')}>BATTLE</button>
                <button className={`mode-btn ${mode === 'shortBreak' ? 'active' : ''}`} onClick={() => switchMode('shortBreak')}>REST</button>
                <button className={`mode-btn ${mode === 'longBreak' ? 'active' : ''}`} onClick={() => switchMode('longBreak')}>FEAST</button>
            </div>

            <div className="pomodoro-timer-display">
                <svg className={`progress-ring ${isRunning && timeLeft <= 60 ? 'urgent' : ''}`} width="320" height="320">
                    <defs>
                        <linearGradient id="gold-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor="#d4a574" />
                            <stop offset="100%" stopColor="#f1c40f" />
                        </linearGradient>
                        <linearGradient id="blue-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor="#3498db" />
                            <stop offset="100%" stopColor="#2980b9" />
                        </linearGradient>
                        <filter id="glow">
                            <feGaussianBlur stdDeviation="3.5" result="coloredBlur" />
                            <feMerge>
                                <feMergeNode in="coloredBlur" />
                                <feMergeNode in="SourceGraphic" />
                            </feMerge>
                        </filter>
                    </defs>
                    <circle cx="160" cy="160" r="145" fill="none" stroke="rgba(255, 255, 255, 0.05)" strokeWidth="8" />
                    <circle cx="160" cy="160" r="145" fill="none" stroke={mode === 'work' ? "url(#gold-gradient)" : "url(#blue-gradient)"}
                        strokeWidth="8" strokeDasharray={`${2 * Math.PI * 145}`}
                        strokeDashoffset={`${2 * Math.PI * 145 * (1 - getProgress() / 100)}`}
                        transform="rotate(-90 160 160)" strokeLinecap="round" filter="url(#glow)" className="progress-circle" />
                </svg>

                {isEditing ? (
                    <div className="timer-edit-overlay">
                        <input type="number" value={editMinutes} onChange={(e) => setEditMinutes(e.target.value)}
                            className="timer-edit-input" min="1" max="120" />
                        <div className="timer-edit-actions">
                            <button onClick={handleEditSave} className="save-btn">✓</button>
                            <button onClick={() => setIsEditing(false)} className="cancel-btn">✕</button>
                        </div>
                    </div>
                ) : (
                    <div className="timer-text-container">
                        {isFullscreen ? (
                            <div className="flip-timer-display">
                                {(() => {
                                    const timeStr = formatTime(timeLeft);
                                    const digits = timeStr.split('');
                                    const min1 = digits[0];
                                    const min2 = digits[1];
                                    const sec1 = digits[3];
                                    const sec2 = digits[4];
                                    return (
                                        <>
                                            <FlipCard digit={min1} />
                                            <FlipCard digit={min2} />
                                            <div className="flip-colon"></div>
                                            <FlipCard digit={sec1} />
                                            <FlipCard digit={sec2} />
                                        </>
                                    );
                                })()}
                            </div>
                        ) : (
                            <>
                                <div className={`timer-text ${isRunning ? 'active' : ''} ${isRunning && timeLeft <= 60 ? 'urgent' : ''}`}>{formatTime(timeLeft)}</div>
                                {!isRunning && (
                                    <button className="edit-time-btn" onClick={() => {
                                        setEditMinutes(Math.floor(timeLeft / 60).toString());
                                        setIsEditing(true);
                                    }} title="Edit Timer">✎</button>
                                )}
                            </>
                        )}
                    </div>
                )}
            </div>

            <div className="pomodoro-actions">
                <button className={`timer-btn ${isRunning ? 'pause' : 'start'}`} onClick={toggleTimer}>
                    {isRunning ? '⏸ HOLD' : '▶ ENGAGE'}
                </button>
                <button className="reset-btn" onClick={resetTimer}>↻ RESTART</button>
            </div>

            <div className="pomodoro-stats">
                <div className="stat-item">
                    <span className="stat-label">VICTORIES</span>
                    <span className="stat-value">{sessionsCompleted}</span>
                </div>
                <div className="stat-item">
                    <span className="stat-label">TOTAL TIME</span>
                    <span className="stat-value">{formatTotalTime(totalStudyTime)}</span>
                </div>
            </div>

            {showSettings && (
                <div className="pomodoro-settings-panel">
                    <h4>⚙️ Settings</h4>
                    <div className="setting-item">
                        <label>
                            <input type="checkbox" checked={settings.autoStartBreaks}
                                onChange={(e) => updateSettings({ autoStartBreaks: e.target.checked })} />
                            Auto-start breaks
                        </label>
                    </div>
                    <div className="setting-item">
                        <label>
                            <input type="checkbox" checked={settings.autoStartPomodoros}
                                onChange={(e) => updateSettings({ autoStartPomodoros: e.target.checked })} />
                            Auto-start work sessions
                        </label>
                    </div>
                    <div className="setting-item">
                        <label>
                            Auto-start delay:
                            <input type="number" min="0" max="60" value={settings.autoStartDelay}
                                onChange={(e) => updateSettings({ autoStartDelay: parseInt(e.target.value) })}
                                className="delay-input" /> seconds
                        </label>
                    </div>
                    <div className="setting-item">
                        <label>
                            <input type="checkbox" checked={settings.notifications}
                                onChange={(e) => updateSettings({ notifications: e.target.checked })} />
                            Enable notifications
                        </label>
                    </div>
                    <div className="keyboard-shortcuts">
                        <h5>⌨️ Keyboard Shortcuts</h5>
                        <div className="shortcut"><kbd>Space</kbd> Play/Pause</div>
                        <div className="shortcut"><kbd>R</kbd> Reset</div>
                        <div className="shortcut"><kbd>1/2/3</kbd> Switch modes</div>
                        <div className="shortcut"><kbd>S</kbd> Toggle settings</div>
                    </div>
                </div>
            )}

            {showHistory && <SessionHistory />}
            <AmbientSoundPlayer />
        </div>
    );
};

export default PomodoroTimer;
