import React from 'react';
import './DashboardMain.css';

import ChallengeCard from './DashboardMain/ChallengeCard';
import RevisionWidget from './DashboardMain/RevisionWidget';
import { useAnalytics } from '../contexts/AnalyticsContext';
import { useGlobal } from '../contexts/GlobalContext';

const DashboardMain: React.FC = () => {
  const { userStats } = useGlobal();
  const { analytics } = useAnalytics();

  if (!userStats) return null;

  const stats = userStats;
  const currentLevel = analytics?.level ?? stats.level;
  const currentXP = analytics?.xp ?? stats.current_xp;
  const maxXP = analytics?.max_xp ?? stats.max_xp;
  const progressPercent = maxXP > 0 ? (currentXP / maxXP) * 100 : 0;

  return (
    <div className="dashboard-main">

      <div className="dashboard-content">
        <div className="dashboard-column-left">
          <ChallengeCard />
          <RevisionWidget />
        </div>

        <div className="stats-panel-left">
          <div className="stat-level"><h3>LEVEL {currentLevel}</h3></div>
          <div className="stat-row">
            <div className="stat-label">PROGRESS</div>
            <div className="stat-bar-container">
              <div
                className="stat-bar-bg"
                role="progressbar"
                aria-label="Level Progress"
                aria-valuenow={currentXP}
                aria-valuemin={0}
                aria-valuemax={maxXP}
              >
                <div className="stat-bar-fill" style={{ width: `${progressPercent}%` }} />
              </div>
            </div>
          </div>
          <div className="xp-text">XP: {currentXP} / {maxXP}</div>
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

        <div className="center-panel">
          <div className="character-section">
            <div className="character-art" />
            <div className="progress-circle-container">
              <svg className="progress-circle" viewBox="0 0 200 200">
                <defs>
                  <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#5fb3e8" />
                    <stop offset="50%" stopColor="#a8d5e8" />
                    <stop offset="100%" stopColor="#5fb3e8" />
                  </linearGradient>
                </defs>
                <circle cx="100" cy="100" r="90" className="circle-bg" />
                <circle cx="100" cy="100" r="90" className="circle-fill"
                  style={{ strokeDasharray: `${(progressPercent / 100) * 565} 565` }} />
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