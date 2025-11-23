import React from 'react';
import './LevelUpModal.css';

interface LevelUpModalProps {
    newLevel: number;
    onClose: () => void;
}

const LevelUpModal: React.FC<LevelUpModalProps> = ({ newLevel, onClose }) => {
    return (
        <div className="levelup-overlay">
            <div className="levelup-content">
                <h1 className="levelup-title">LEVEL UP</h1>
                <h2 className="levelup-sub">YOU ARE NOW LEVEL {newLevel}</h2>
                
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