import React from 'react';
import './LevelUpModal.css';

import { useState, useEffect, useRef } from 'react';

interface LevelUpModalProps {
    newLevel: number;
    lore?: string;
    onClose: () => void;
}

const LevelUpModal: React.FC<LevelUpModalProps> = ({ newLevel, lore, onClose }) => {
    const [displayedLore, setDisplayedLore] = useState('');
    const modalRef = useRef<HTMLDivElement>(null);

    // Focus management and Escape key listener
    useEffect(() => {
        // Focus the modal container on mount so screen readers announce it
        if (modalRef.current) {
            modalRef.current.focus();
        }

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

    return (
        <div
            className="levelup-overlay"
            role="dialog"
            aria-modal="true"
            aria-labelledby="levelup-title"
            tabIndex={-1}
            ref={modalRef}
        >
            <div className="levelup-content">
                <h1 id="levelup-title" className="levelup-title">LEVEL UP</h1>
                <h2 className="levelup-sub">YOU ARE NOW LEVEL {newLevel}</h2>
                
                {lore && (
                    <div className="levelup-lore">
                        <p aria-hidden="true">{displayedLore}</p>
                        <span className="sr-only">{lore}</span>
                    </div>
                )}

                <div className="levelup-rewards">
                    <div className="reward-badge">+ Max HP (Study Stamina)</div>
                    <div className="reward-badge">+ Stat Point Unlocked</div>
                </div>

                <button className="continue-btn" onClick={onClose}>
                    CONTINUE THE JOURNEY
                </button>
            </div>
        </div>
    );
};

export default LevelUpModal;