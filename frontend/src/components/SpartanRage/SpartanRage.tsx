// /frontend/src/components/SpartanRage/SpartanRage.tsx
import React, { useState, useEffect } from 'react';
import './SpartanRage.css';
import { useGlobal } from '../../contexts/GlobalContext';

const SpartanRage: React.FC = () => {
    const { isRageMode, setIsRageMode } = useGlobal();
    const [timeLeft, setTimeLeft] = useState(0);

    // Timer countdown effect
    useEffect(() => {
        if (!isRageMode || timeLeft <= 0) return;

        const interval = setInterval(() => {
            setTimeLeft((prev) => Math.max(0, prev - 1));
        }, 1000);

        return () => clearInterval(interval);
    }, [isRageMode, timeLeft]);

    // Timer expiration effect
    useEffect(() => {
        if (!isRageMode) return;

        if (timeLeft === 0) {
            setIsRageMode(false);
        }
    }, [timeLeft, isRageMode, setIsRageMode]);

    const toggleRage = () => {
        const newState = !isRageMode;
        setIsRageMode(newState);
        if (newState) setTimeLeft(50 * 60);
    };

    const formatTime = (seconds: number) => {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${m}:${s < 10 ? '0' : ''}${s}`;
    };

    return (
        <div className="rage-container">
            {isRageMode && <div className="rage-timer-display">{formatTime(timeLeft)}</div>}
            <button
                className={`rage-button ${isRageMode ? 'active' : ''}`}
                onClick={toggleRage}
            >
                {isRageMode ? "RAGE ACTIVE" : "L3 + R3 FOCUS"}
            </button>
        </div>
    );
};

export default SpartanRage;