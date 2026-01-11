import React, { useState, useEffect, useRef } from 'react';
import './RitualsPanel.css'; // Reuse existing styles or add new ones
import { useGlobal } from '../contexts/GlobalContext';
import { API_BASE_URL } from '../config';
import { ToastContainer, useToast } from './Toast';

const StudyTimer: React.FC = () => {
    const { refreshDashboard } = useGlobal();
    const { toasts, addToast, removeToast } = useToast();
    const [seconds, setSeconds] = useState(0);
    const [isActive, setIsActive] = useState(false);
    const [isPaused, setIsPaused] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const intervalRef = useRef<number | null>(null);

    useEffect(() => {
        if (isActive && !isPaused) {
            intervalRef.current = setInterval(() => {
                setSeconds((s) => s + 1);
            }, 1000);
        } else {
            if (intervalRef.current) clearInterval(intervalRef.current);
        }
        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current);
        };
    }, [isActive, isPaused]);

    const handleStart = () => {
        setIsActive(true);
        setIsPaused(false);
    };

    const handlePause = () => {
        setIsPaused(true);
    };

    const handleStop = async () => {
        setIsActive(false);
        setIsPaused(false);

        if (seconds < 60) {
            addToast("Session too short to log (min 1 minute).", "warning");
            setSeconds(0);
            return;
        }

        setIsSaving(true);
        const minutes = Math.floor(seconds / 60);
        try {
            const res = await fetch(`${API_BASE_URL}/api/tasks/log-study`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ minutes })
            });

            if (res.ok) {
                const data = await res.json();
                addToast(`Study session logged! +${data.xp_earned} XP`, "success");
                await refreshDashboard();
            } else {
                addToast("Failed to log study session.", "error");
            }
        } catch (err) {
            console.error('Error logging study:', err);
            addToast("Error connecting to server.", "error");
        } finally {
            setIsSaving(false);
            setSeconds(0);
        }
    };

    const formatTime = (totalSeconds: number) => {
        const h = Math.floor(totalSeconds / 3600);
        const m = Math.floor((totalSeconds % 3600) / 60);
        const s = totalSeconds % 60;
        return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    };

    return (
        <div className="study-timer">
            <ToastContainer toasts={toasts} removeToast={removeToast} />
            <h3>⏱️ Focus Timer</h3>
            <div
                className="timer-display"
                role="timer"
                aria-label="Current session duration"
            >
                {formatTime(seconds)}
            </div>
            <div className="timer-controls">
                {!isActive ? (
                    <button
                        className="timer-btn start"
                        onClick={handleStart}
                        aria-label="Start study timer"
                        disabled={isSaving}
                    >
                        START
                    </button>
                ) : (
                    <>
                        {isPaused ? (
                            <button
                                className="timer-btn resume"
                                onClick={handleStart}
                                aria-label="Resume study timer"
                                disabled={isSaving}
                            >
                                RESUME
                            </button>
                        ) : (
                            <button
                                className="timer-btn pause"
                                onClick={handlePause}
                                aria-label="Pause study timer"
                                disabled={isSaving}
                            >
                                PAUSE
                            </button>
                        )}
                        <button
                            className="timer-btn stop"
                            onClick={handleStop}
                            disabled={isSaving}
                            aria-busy={isSaving}
                            aria-label={isSaving ? "Saving study session" : "Finish study session and log time"}
                        >
                            {isSaving ? "SAVING..." : "FINISH"}
                        </button>
                    </>
                )}
            </div>
        </div>
    );
};

export default StudyTimer;
