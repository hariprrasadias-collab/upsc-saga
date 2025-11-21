// /frontend/src/components/Sidebar.tsx
import React from 'react';
import './Sidebar.css'; // Make sure this CSS file exists
import type { UserStats } from '../App';

interface SidebarProps {
  currentTab: string;
  onTabChange: (tab: string) => void;
  userStats: UserStats | null;
  ankiDueCount: number
}

const Sidebar: React.FC<SidebarProps> = ({ currentTab, onTabChange }) => {
  return (
    <div className="sidebar-container">
      <div className="sidebar-header">
        <img src="/logo.png" alt="UPSC Saga Logo" className="sidebar-logo" /> {/* Adjust path to your logo */}
        <h1 className="app-title">UPSC SAGA</h1>
      </div>
      <nav className="sidebar-nav">
        <ul>
          <li className={currentTab === 'dashboard' ? 'active' : ''}>
            <button onClick={() => onTabChange('dashboard')}>
              Dashboard
            </button>
          </li>
          <li className={currentTab === 'war-map' ? 'active' : ''}>
            <button onClick={() => onTabChange('war-map')}>
              War Map
            </button>
          </li>
          <li className={currentTab === 'quests' ? 'active' : ''}>
            <button onClick={() => onTabChange('quests')}>
              Quests
            </button>
          </li>
          <li className={currentTab === 'codex' ? 'active' : ''}>
            <button onClick={() => onTabChange('codex')}>
              Codex
            </button>
          </li>
          <li className={currentTab === 'lore-tablets' ? 'active' : ''}>
            <button onClick={() => onTabChange('lore-tablets')}>
              Lore Tablets
            </button>
          </li>
        </ul>
      </nav>
      {/* Optional: Add a footer or user info */}
      <div className="sidebar-footer">
        {/* <p>&copy; 2023 UPSC Saga</p> */}
      </div>
    </div>
  );
};

export default Sidebar;