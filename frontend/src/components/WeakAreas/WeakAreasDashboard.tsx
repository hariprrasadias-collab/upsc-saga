import React, { useState, useEffect } from 'react';
import './WeakAreasDashboard.css';

interface WeakArea {
    topic: string;
    subject: string;
    total_attempts: number;
    correct_attempts: number;
    accuracy_rate: number;
    weakness_score: number;
}

interface DashboardStats {
    total_attempts: number;
    overall_accuracy: number;
    subject_breakdown: Array<{ subject: string; attempts: number; accuracy: number }>;
    weak_topics_count: number;
}

const WeakAreasDashboard: React.FC = () => {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [weakAreas, setWeakAreas] = useState<WeakArea[]>([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
        fetchDashboard();
    }, []);

    const fetchDashboard = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:5000/api/weak-areas/dashboard');
            const data = await response.json();

            if (data.success) {
                setStats(data.stats);
                setWeakAreas(data.weak_areas);
            }
        } catch (error) {
            console.error('Error fetching dashboard:', error);
        } finally {
            setLoading(false);
        }
    };

    const generatePractice = async () => {
        setGenerating(true);
        try {
            const response = await fetch('http://localhost:5000/api/weak-areas/practice', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ count: 10 })
            });

            const data = await response.json();

            if (data.success) {
                alert(`Generated ${data.count} practice questions from weak topics!`);
                // TODO: Navigate to practice quiz
            } else {
                alert(data.error || 'Failed to generate practice set');
            }
        } catch (error) {
            console.error('Error generating practice:', error);
        } finally {
            setGenerating(false);
        }
    };

    const getWeaknessColor = (score: number): string => {
        if (score >= 70) return '#ef4444';  // Critical - Red
        if (score >= 50) return '#f59e0b';  // Warning - Amber
        if (score >= 30) return '#3b82f6';  // Moderate - Blue
        return '#10b981';  // Good - Green
    };

    const getScoreLabel = (score: number): string => {
        if (score >= 70) return 'Critical';
        if (score >= 50) return 'Weak';
        if (score >= 30) return 'Moderate';
        return 'Strong';
    };

    return (
        <div className="weak-areas-dashboard">
            <div className="dashboard-header">
                <div>
                    <h1>🎯 Weak Areas Dashboard</h1>
                    <p>Identify your weak topics and improve with targeted practice</p>
                </div>
                <button onClick={generatePractice} disabled={generating} className="practice-btn">
                    {generating ? '⏳ Generating...' : '🎓 Generate Practice Quiz'}
                </button>
            </div>

            {loading ? (
                <div className="loading-state">Analyzing your performance...</div>
            ) : stats ? (
                <>
                    {/* Stats Cards */}
                    <div className="stats-grid">
                        <div className="stat-card">
                            <div className="stat-icon">📝</div>
                            <div className="stat-content">
                                <div className="stat-value">{stats.total_attempts}</div>
                                <div className="stat-label">Total Attempts</div>
                            </div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-icon">✅</div>
                            <div className="stat-content">
                                <div className="stat-value">{stats.overall_accuracy}%</div>
                                <div className="stat-label">Overall Accuracy</div>
                            </div>
                        </div>

                        <div className="stat-card highlight">
                            <div className="stat-icon">⚠️</div>
                            <div className="stat-content">
                                <div className="stat-value">{stats.weak_topics_count}</div>
                                <div className="stat-label">Weak Topics</div>
                            </div>
                        </div>
                    </div>

                    {/* Weak Areas Heatmap */}
                    <div className="section">
                        <h2>🔥 Top Weak Areas</h2>
                        {weakAreas.length > 0 ? (
                            <div className="weak-areas-grid">
                                {weakAreas.map((area, idx) => (
                                    <div key={idx} className="weak-area-card"
                                        style={{ borderLeftColor: getWeaknessColor(area.weakness_score) }}>
                                        <div className="weak-area-header">
                                            <div className="rank-badge" style={{ background: getWeaknessColor(area.weakness_score) }}>
                                                #{idx + 1}
                                            </div>
                                            <div className="weakness-score">
                                                <span className="score-value" style={{ color: getWeaknessColor(area.weakness_score) }}>
                                                    {Math.round(area.weakness_score)}
                                                </span>
                                                <span className="score-label">{getScoreLabel(area.weakness_score)}</span>
                                            </div>
                                        </div>

                                        <h3>{area.topic}</h3>
                                        <div className="subject-tag">{area.subject}</div>

                                        <div className="metrics-row">
                                            <div className="metric">
                                                <span className="metric-label">Attempts</span>
                                                <span className="metric-value">{area.total_attempts}</span>
                                            </div>
                                            <div className="metric">
                                                <span className="metric-label">Accuracy</span>
                                                <span className="metric-value">
                                                    {Math.round(area.accuracy_rate * 100)}%
                                                </span>
                                            </div>
                                            <div className="metric">
                                                <span className="metric-label">Correct</span>
                                                <span className="metric-value">
                                                    {area.correct_attempts}/{area.total_attempts}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="empty-state">
                                Complete some quizzes to see your weak areas!
                            </div>
                        )}
                    </div>

                    {/* Subject Breakdown */}
                    {stats.subject_breakdown.length > 0 && (
                        <div className="section">
                            <h2>📊 Subject-wise Performance</h2>
                            <div className="subject-bars">
                                {stats.subject_breakdown.map((subj, idx) => (
                                    <div key={idx} className="subject-bar-item">
                                        <div className="subject-name">{subj.subject}</div>
                                        <div className="bar-container">
                                            <div className="bar-fill"
                                                style={{
                                                    width: `${subj.accuracy * 100}%`,
                                                    background: subj.accuracy > 0.7 ? '#10b981' : subj.accuracy > 0.5 ? '#f59e0b' : '#ef4444'
                                                }}>
                                            </div>
                                        </div>
                                        <div className="subject-stats">
                                            <span>{Math.round(subj.accuracy * 100)}%</span>
                                            <span className="attempts-count">{subj.attempts} qs</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </>
            ) : (
                <div className="empty-state">
                    No performance data yet. Start practicing to track your weak areas!
                </div>
            )}
        </div>
    );
};

export default WeakAreasDashboard;
