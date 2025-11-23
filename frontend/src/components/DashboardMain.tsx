// /frontend/src/components/DashboardMain.tsx
import React from 'react';
import './DashboardMain.css';
import type { UserStats } from '../App';

interface DashboardMainProps {
  stats: UserStats;
}

const DashboardMain: React.FC<DashboardMainProps> = ({
  stats
}) => {

  // Calculate progress percentage safely
  const progressPercent = stats.max_xp > 0
    ? (stats.current_xp / stats.max_xp) * 100
    : 0;

  return (
    <div className="dashboard-main">
      <div className="dashboard-header">
        <h1 className="header-title">CHARACTER</h1>
        <div className="runes-decoration"></div>
      </div>

      <div className="dashboard-content">
        {/* Left Stats Panel */}
        <div className="stats-panel-left">
          <div className="stat-level">
            <h3>LEVEL {stats.level}</h3>
          </div>
          <div className="stat-row">
            <div className="stat-label">PROGRESS</div>
            <div className="stat-bar-container">
              <div className="stat-bar-bg">
                <div className="stat-bar-fill" style={{ width: `${progressPercent}%` }}></div>
              </div>
            </div>
          </div>
          <div className="xp-text">XP: {stats.current_xp} / {stats.max_xp}</div>

          <div className="stats-list">
            <div className="stat-item strength">
              <img src="/stat_strength.png" alt="Strength" className="stat-icon" />
              <div className="stat-info">
                <div className="stat-name">STRENGTH</div>
                <div className="stat-label-code">GS-I</div>
              </div>
              <div className="stat-value">{stats.strength_stat}</div>
            </div>
            <div className="stat-item runic">
              <img src="/stat_runic.png" alt="Runic" className="stat-icon" />
              <div className="stat-info">
                <div className="stat-name">RUNIC</div>
                <div className="stat-label-code">GS-II</div>
              </div>
              <div className="stat-value">{stats.runic_stat}</div>
            </div>
            <div className="stat-item vitality">
              <img src="/stat_vitality.png" alt="Vitality" className="stat-icon" />
              <div className="stat-info">
                <div className="stat-name">VITALITY</div>
                <div className="stat-label-code">GS-III</div>
              </div>
              <div className="stat-value">{stats.vitality_stat}</div>
            </div>
            <div className="stat-item luck">
              <img src="/stat_luck.png" alt="Luck" className="stat-icon" />
              <div className="stat-info">
                <div className="stat-name">LUCK</div>
                <div className="stat-label-code">GS-IV</div>
              </div>
              <div className="stat-value">{stats.luck_stat}</div>
            </div>
          </div>
        </div>

        {/* Center Panel - Character & Circular Progress */}
        <div className="center-panel">
          <div className="character-section">
            <div className="character-art"></div>
            <div className="progress-circle-container">
              <svg className="progress-circle" viewBox="0 0 200 200">
                <defs>
                  <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#5fb3e8" />
                    <stop offset="50%" stopColor="#a8d5e8" />
                    <stop offset="100%" stopColor="#5fb3e8" />
                  </linearGradient>
                </defs>
                <circle cx="100" cy="100" r="90" className="circle-bg"></circle>
                <circle
                  cx="100"
                  cy="100"
                  r="90"
                  className="circle-fill"
                  style={{ strokeDasharray: `${(progressPercent / 100) * 565} 565` }}
                ></circle>
                <text x="100" y="110" className="progress-text">{Math.round(progressPercent)}%</text>
              </svg>
            </div>
            <h2 className="character-title">UPSC ASPIRANT</h2>
          </div>

          <div className="boons-curses">
            <div className="boons-section">
              <h3>ACTIVE BOONS</h3>
              <p className="section-label">(STRENGTHS)</p>
            </div>
            <div className="curses-section">
              <h3>CURSES</h3>
              <p className="section-label">(WEAKNESSES)</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardMain;