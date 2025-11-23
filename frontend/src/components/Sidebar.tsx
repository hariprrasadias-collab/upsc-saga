// /frontend/src/components/Sidebar.tsx
import React, { useState } from 'react';
import './Sidebar.css';
import type { UserStats } from '../App';
// Make sure you created the file frontend/src/utils/AudioManager.ts from the previous step!
import { audioManager } from '../util/AudioManager';

interface SidebarProps {
  currentTab: string;
  onTabChange: (tab: string) => void;
  userStats: UserStats | null;
  ankiDueCount: number;
}

const Sidebar: React.FC<SidebarProps> = ({ currentTab, onTabChange, userStats, ankiDueCount }) => {
  // Initialize state based on the manager
  const [isMuted, setIsMuted] = useState(audioManager.getMuteStatus());

  const handleTabClick = (tab: string) => {
    audioManager.play('click'); // Play sound effect
    onTabChange(tab);
  };

  const toggleSound = () => {
    const muted = audioManager.toggleMute();
    setIsMuted(muted);
  };

  return (
    <div className="sidebar-container">
      <div className="sidebar-header">
        {/* Logo/Title */}
        <img src="/logo.png" alt="Logo" className="sidebar-logo" style={{display:'none'}} /> 
        <h1 className="app-title">UPSC SAGA</h1>
        
        {/* USER SUMMARY (Level & Money) */}
        {userStats && (
            <div className="sidebar-user-summary">
                <div className="summary-level">LVL {userStats.level}</div>
                <div className="summary-currency">
                    <span className="coin-icon"></span> 
                    {userStats.hacksilver} HS
                </div>
            </div>
        )}

        {/* MUTE TOGGLE */}
        <button 
            onClick={toggleSound}
            style={{
                background: 'transparent',
                border: '1px solid var(--color-border-primary)',
                color: 'var(--color-text-secondary)',
                marginTop: '10px',
                cursor: 'pointer',
                padding: '5px 10px',
                fontSize: '0.8rem',
                width: '100%',
                borderRadius: '4px',
                textTransform: 'uppercase'
            }}
        >
            {isMuted ? "🔇 UNMUTE AUDIO" : "🔊 MUTE AUDIO"}
        </button>
      </div>

      {/* NAVIGATION */}
      <nav className="sidebar-nav">
        <ul>
          <li className={currentTab === 'dashboard' ? 'active' : ''}>
            <button onClick={() => handleTabClick('dashboard')}>Dashboard</button>
          </li>
          <li className={currentTab === 'war-map' ? 'active' : ''}>
            <button onClick={() => handleTabClick('war-map')}>War Map</button>
          </li>
          <li className={currentTab === 'quests' ? 'active' : ''}>
            <button onClick={() => handleTabClick('quests')}>Quests</button>
          </li>
          <li className={currentTab === 'codex' ? 'active' : ''}>
            <button onClick={() => handleTabClick('codex')}>Codex</button>
          </li>
          <li className={currentTab === 'lore-tablets' ? 'active' : ''}>
            <button onClick={() => handleTabClick('lore-tablets')}>Lore Tablets</button>
          </li>
          <li className={currentTab === 'arena' ? 'active' : ''}>
            <button onClick={() => handleTabClick('arena')}>Arena</button>
          </li>
          <li className={currentTab === 'armory' ? 'active' : ''}>
            <button onClick={() => handleTabClick('armory')} style={{color: '#cd7f32'}}>Armory</button>
          </li>
          <li className={currentTab === 'seer' ? 'active' : ''}>
            <button onClick={() => handleTabClick('seer')} style={{color: '#7fdbff'}}>The Seer</button>
          </li>
          <li className={currentTab === 'ravens' ? 'active' : ''}>
            <button onClick={() => handleTabClick('ravens')}>The Ravens</button>
          </li>
          {/* In Sidebar.tsx navigation list */}
          <li className={currentTab === 'dojo' ? 'active' : ''}>
            <button onClick={() => handleTabClick('dojo')}>The Dojo (Anki)</button>
          </li>
        </ul>
      </nav>

      <div className="sidebar-footer">
        {ankiDueCount > 0 && (
            <div className="anki-alert">
                Anki Cards Due: {ankiDueCount}
            </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;