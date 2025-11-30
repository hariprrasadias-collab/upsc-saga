import React, { useState, useEffect, useRef } from 'react';
import './RitualsPanel.css'; // Reuse existing styles or add new ones

const StudyTimer: React.FC = () => {
    const [seconds, setSeconds] = useState(0);
    const [isActive, setIsActive] = useState(false);
    const [isPaused, setIsPaused] = useState(false);
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
            alert("Session too short to log (min 1 minute).");
            setSeconds(0);
            return;
        }

        const minutes = Math.floor(seconds / 60);
        try {
            const res = await fetch('http://localhost:5000/api/tasks/log-study', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ minutes })
            });

            if (res.ok) {
                const data = await res.json();
                alert(`Study session logged! +${data.xp_earned} XP`);
                // Ideally trigger a global refresh here
                window.location.reload();
            }
        } catch (err) {
            console.error('Error logging study:', err);
        }

        setSeconds(0);
    };

    const formatTime = (totalSeconds: number) => {
        const h = Math.floor(totalSeconds / 3600);
        const m = Math.floor((totalSeconds % 3600) / 60);
        const s = totalSeconds % 60;
        return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    };

    return (
        <div className="study-timer">
            <h3>⏱️ Focus Timer</h3>
            <div className="timer-display">{formatTime(seconds)}</div>
            <div className="timer-controls">
                {!isActive ? (
                    <button className="timer-btn start" onClick={handleStart}>START</button>
                ) : (
                    <>
                        {isPaused ? (
                            <button className="timer-btn resume" onClick={handleStart}>RESUME</button>
                        ) : (
                            <button className="timer-btn pause" onClick={handlePause}>PAUSE</button>
                        )}
                        <button className="timer-btn stop" onClick={handleStop}>FINISH</button>
                    </>
                )}
            </div>
        </div>
    );
};

export default StudyTimer;
