import React, { useState, useEffect, useRef } from 'react';
import './LevelUpModal.css';

interface LevelUpModalProps {
    newLevel: number;
    lore?: string;
    onClose: () => void;
}

const LevelUpModal: React.FC<LevelUpModalProps> = ({ newLevel, lore, onClose }) => {
    const [displayedLore, setDisplayedLore] = useState('');
    const continueBtnRef = useRef<HTMLButtonElement>(null);

    // Focus management and Keyboard support
    useEffect(() => {
        // Focus the primary action on mount for accessibility
        continueBtnRef.current?.focus();

        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') {
                onClose();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [onClose]);

    // Typing effect for lore
    useEffect(() => {
        if (!lore) return;
        let i = 0;
        const interval = setInterval(() => {
            setDisplayedLore(lore.substring(0, i));
            i++;
            if (i > lore.length) clearInterval(interval);
        }, 30);
        return () => clearInterval(interval);
    }, [lore]);

    // Screen reader only style
    const srOnly: React.CSSProperties = {
        position: 'absolute',
        width: '1px',
        height: '1px',
        padding: 0,
        margin: '-1px',
        overflow: 'hidden',
        clip: 'rect(0, 0, 0, 0)',
        whiteSpace: 'nowrap',
        border: 0
    };

    return (
        <div
            className="levelup-overlay"
            role="dialog"
            aria-modal="true"
            aria-labelledby="levelup-heading"
        >
            <div className="levelup-content">
                <h1 id="levelup-heading" className="levelup-title">LEVEL UP</h1>
                <h2 className="levelup-sub">YOU ARE NOW LEVEL {newLevel}</h2>
                
                {lore && (
                    <div className="levelup-lore">
                        <p aria-hidden="true">{displayedLore}</p>
                        <p style={srOnly}>{lore}</p>
                    </div>
                )}

                <div className="levelup-rewards">
                    <div className="reward-badge">+ Max HP (Study Stamina)</div>
                    <div className="reward-badge">+ Stat Point Unlocked</div>
                </div>

                <button
                    ref={continueBtnRef}
                    className="continue-btn"
                    onClick={onClose}
                >
                    CONTINUE THE JOURNEY
                </button>
            </div>
        </div>
    );
};

export default LevelUpModal;
