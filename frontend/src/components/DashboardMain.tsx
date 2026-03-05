import React, { useState, useEffect } from 'react';
import './DashboardMain.css';

import ChallengeCard from './DashboardMain/ChallengeCard';
import RevisionWidget from './DashboardMain/RevisionWidget';
import { useAnalytics } from '../contexts/AnalyticsContext';
import { useGlobal } from '../contexts/GlobalContext';
import { API_BASE_URL } from '../config';

interface WeakArea {
  subject: string;
  topic: string;
  weakness_score: number;
  source: string;
  action: string;
  trend?: 'improving' | 'declining' | 'stable';
}

interface Strength {
  stat: string;
  label: string;
  value: number;
  icon: string;
}

const DashboardMain: React.FC = () => {
  const { userStats } = useGlobal();
  const { analytics } = useAnalytics();
  const [weakAreas, setWeakAreas] = useState<WeakArea[]>([]);
  const [weakLoading, setWeakLoading] = useState(true);

  useEffect(() => {
    fetchWeakAreas();
  }, []);

  const fetchWeakAreas = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/analytics/weak-areas?limit=5`);
      if (res.ok) {
        const data = await res.json();
        setWeakAreas(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      console.error('Failed to fetch weak areas:', err);
    } finally {
      setWeakLoading(false);
    }
  };

  if (!userStats) return null;

  const stats = userStats;
  const currentLevel = analytics?.level ?? stats.level;
  const currentXP = analytics?.xp ?? stats.current_xp;
  const maxXP = analytics?.max_xp ?? stats.max_xp;
  const progressPercent = maxXP > 0 ? (currentXP / maxXP) * 100 : 0;

  // Derive strengths from stats — sorted by value, top ones are boons
  const statEntries: Strength[] = [
    { stat: 'strength', label: 'GS-I', value: stats.strength_stat, icon: '⚔️' },
    { stat: 'runic', label: 'GS-II', value: stats.runic_stat, icon: '🔮' },
    { stat: 'vitality', label: 'GS-III', value: stats.vitality_stat, icon: '💚' },
    { stat: 'luck', label: 'GS-IV', value: stats.luck_stat, icon: '🍀' },
  ];
  const sorted = [...statEntries].sort((a, b) => b.value - a.value);
  const boons = sorted.filter(s => s.value > 0).slice(0, 2); // Top 2 stats

  const trendIcon = (trend?: string) => {
    if (trend === 'improving') return '📈';
    if (trend === 'declining') return '📉';
    return '➡️';
  };

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
              <div className="stat-bar-bg">
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

          {/* Boons & Curses — now populated! */}
          <div className="boons-curses">
            <div className="boons-section">
              <h3>ACTIVE BOONS</h3>
              <p className="section-label">(STRENGTHS)</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '8px' }}>
                {boons.length > 0 ? boons.map(b => (
                  <div key={b.stat} style={{
                    display: 'flex', alignItems: 'center', gap: '8px',
                    padding: '6px 10px', borderRadius: '6px',
                    background: 'rgba(16, 185, 129, 0.08)',
                    borderLeft: '3px solid #10b981',
                  }}>
                    <span style={{ fontSize: '1.1rem' }}>{b.icon}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ color: '#10b981', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                        {b.stat} ({b.label})
                      </div>
                      <div style={{ color: '#94a3b8', fontSize: '0.7rem' }}>Level {b.value}</div>
                    </div>
                    <span style={{ color: '#10b981', fontWeight: 700, fontSize: '1rem' }}>{b.value}</span>
                  </div>
                )) : (
                  <div style={{ color: '#475569', fontSize: '0.8rem', fontStyle: 'italic' }}>
                    Complete activities to unlock boons
                  </div>
                )}
                {analytics?.streak_days && analytics.streak_days > 0 && (
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: '8px',
                    padding: '6px 10px', borderRadius: '6px',
                    background: 'rgba(245, 158, 11, 0.08)',
                    borderLeft: '3px solid #f59e0b',
                  }}>
                    <span style={{ fontSize: '1.1rem' }}>🔥</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ color: '#f59e0b', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>STREAK</div>
                      <div style={{ color: '#94a3b8', fontSize: '0.7rem' }}>{analytics.streak_days} day streak active</div>
                    </div>
                  </div>
                )}
              </div>
            </div>
            <div className="curses-section">
              <h3>CURSES</h3>
              <p className="section-label">(WEAKNESSES)</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '8px' }}>
                {weakLoading ? (
                  <div style={{ color: '#475569', fontSize: '0.8rem' }}>Scanning...</div>
                ) : weakAreas.length > 0 ? weakAreas.slice(0, 3).map((w, idx) => (
                  <div key={idx} style={{
                    display: 'flex', alignItems: 'center', gap: '8px',
                    padding: '6px 10px', borderRadius: '6px',
                    background: 'rgba(239, 68, 68, 0.06)',
                    borderLeft: '3px solid #ef4444',
                  }}>
                    <span style={{ fontSize: '1.1rem' }}>{trendIcon(w.trend)}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ color: '#ef4444', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                        {w.topic}
                      </div>
                      <div style={{ color: '#94a3b8', fontSize: '0.7rem' }}>{w.subject}</div>
                    </div>
                    <div style={{
                      color: '#ef4444', fontSize: '0.7rem', fontWeight: 600,
                      background: 'rgba(239, 68, 68, 0.1)', padding: '2px 6px', borderRadius: '4px'
                    }}>
                      {Math.round(w.weakness_score)}
                    </div>
                  </div>
                )) : (
                  <div style={{ color: '#475569', fontSize: '0.8rem', fontStyle: 'italic' }}>
                    🎉 No major weaknesses detected
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardMain;