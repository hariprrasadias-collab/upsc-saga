// /frontend/src/components/SpartanRage/SpartanRage.tsx
import React, { useState, useEffect } from 'react';
import './SpartanRage.css';

interface SpartanRageProps {
    onToggleRage: (isActive: boolean) => void;
}

const SpartanRage: React.FC<SpartanRageProps> = ({ onToggleRage }) => {
    const [isActive, setIsActive] = useState(false);
    const [timeLeft, setTimeLeft] = useState(0);

    // Timer countdown effect
    useEffect(() => {
        if (!isActive || timeLeft <= 0) return;

        const interval = setInterval(() => {
            setTimeLeft((prev) => Math.max(0, prev - 1));
        }, 1000);

        return () => clearInterval(interval);
    }, [isActive, timeLeft]);

    // Timer expiration effect - setState is intentional for timer completion
    useEffect(() => {
        if (!isActive) return;

        if (timeLeft === 0) {
            // eslint-disable-next-line react-hooks/exhaustive-deps
            setIsActive(false);
            onToggleRage(false);
        }
    }, [timeLeft, isActive, onToggleRage]);

    const toggleRage = () => {
        const newState = !isActive;
        setIsActive(newState);
        onToggleRage(newState);
        if (newState) setTimeLeft(50 * 60);
    };

    const formatTime = (seconds: number) => {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${m}:${s < 10 ? '0' : ''}${s}`;
    };

    return (
        <div className="rage-container">
            {isActive && <div className="rage-timer-display">{formatTime(timeLeft)}</div>}
            <button
                className={`rage-button ${isActive ? 'active' : ''}`}
                onClick={toggleRage}
            >
                {isActive ? "RAGE ACTIVE" : "L3 + R3 FOCUS"}
            </button>
        </div>
    );
};

export default SpartanRage;