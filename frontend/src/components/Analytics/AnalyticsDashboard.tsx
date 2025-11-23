// Analytics Dashboard - Phase 2 Feature #2
import React, { useState, useEffect } from 'react';
import './Analytics.css';
import {
    LineChart, Line, BarChart, Bar, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const AnalyticsDashboard: React.FC = () => {
    const [timeframe, setTimeframe] = useState<'7d' | '30d' | 'all'>('30d');
    const [overview, setOverview] = useState<any>(null);
    const [subjectData, setSubjectData] = useState<any[]>([]);
    const [mockTrends, setMockTrends] = useState<any>(null);
    const [weakAreas, setWeakAreas] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAnalytics();
    }, [timeframe]);

    const fetchAnalytics = async () => {
        try {
            setLoading(true);

            // Fetch all analytics data in parallel
            const [overviewRes, subjectRes, mockRes, weakRes] = await Promise.all([
                fetch(`http://localhost:5000/api/analytics/overview?timeframe=${timeframe}`),
                fetch('http://localhost:5000/api/analytics/subject-wise'),
                fetch('http://localhost:5000/api/analytics/mock-tests'),
                fetch('http://localhost:5000/api/analytics/weak-areas?limit=5')
            ]);

            const overviewData = await overviewRes.json();
            const subjectData = await subjectRes.json();
            const mockData = await mockRes.json();
            const weakData = await weakRes.json();

            setOverview(overviewData);
            setSubjectData(subjectData);
            setMockTrends(mockData);
            setWeakAreas(weakData);
            setLoading(false);
        } catch (err) {
            console.error('Failed to fetch analytics:', err);
            setLoading(false);
        }
    };

    if (loading) return <div className="analytics-loading">Loading analytics...</div>;

    return (
        <div className="analytics-dashboard">
            {/* Header with Timeframe Selector */}
            <div className="analytics-header">
                <h1>📊 Performance Analytics</h1>
                <div className="timeframe-selector">
                    <button
                        className={timeframe === '7d' ? 'active' : ''}
                        onClick={() => setTimeframe('7d')}
                    >
                        7 Days
                    </button>
                    <button
                        className={timeframe === '30d' ? 'active' : ''}
                        onClick={() => setTimeframe('30d')}
                    >
                        30 Days
                    </button>
                    <button
                        className={timeframe === 'all' ? 'active' : ''}
                        onClick={() => setTimeframe('all')}
                    >
                        All Time
                    </button>
                </div>
            </div>

            {/* Overview Cards */}
            {overview && (
                <div className="overview-cards">
                    <div className="stat-card study-hours">
                        <div className="stat-icon">⏱️</div>
                        <div className="stat-content">
                            <div className="stat-value">{overview.study_hours}h</div>
                            <div className="stat-label">Study Hours</div>
                        </div>
                    </div>
                    <div className="stat-card xp-earned">
                        <div className="stat-icon">⚡</div>
                        <div className="stat-content">
                            <div className="stat-value">{overview.xp}</div>
                            <div className="stat-label">XP Earned</div>
                            <div className="stat-subtitle">Level {overview.level}</div>
                        </div>
                    </div>
                    <div className="stat-card streak">
                        <div className="stat-icon">🔥</div>
                        <div className="stat-content">
                            <div className="stat-value">{overview.streak_days}</div>
                            <div className="stat-label">Day Streak</div>
                        </div>
                    </div>
                    <div className="stat-card activities">
                        <div className="stat-icon">✅</div>
                        <div className="stat-content">
                            <div className="stat-value">{overview.activities_completed}</div>
                            <div className="stat-label">Activities</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Charts Grid */}
            <div className="charts-grid">
                {/* Subject Performance Radar */}
                <div className="chart-container radar-container">
                    <h3>Subject Performance</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <RadarChart data={subjectData}>
                            <PolarGrid />
                            <PolarAngleAxis dataKey="subject" />
                            <PolarRadiusAxis angle={90} domain={[0, 100]} />
                            <Radar name="Mock Avg" dataKey="mock_avg" stroke="#3498db" fill="#3498db" fillOpacity={0.6} />
                            <Radar name="Answer Avg" dataKey="answer_avg" stroke="#2ecc71" fill="#2ecc71" fillOpacity={0.6} />
                            <Radar name="Syllabus %" dataKey="syllabus_pct" stroke="#9b59b6" fill="#9b59b6" fillOpacity={0.6} />
                            <Tooltip />
                            <Legend />
                        </RadarChart>
                    </ResponsiveContainer>
                </div>

                {/* Mock Test Trends */}
                {mockTrends && mockTrends.trends && (
                    <div className="chart-container trends-container">
                        <h3>Mock Test Score Trends</h3>
                        <div className="improvement-badge">
                            {mockTrends.improvement_rate > 0 ? '📈' : '📉'}
                            {' '}{Math.abs(mockTrends.improvement_rate)}%
                            {mockTrends.improvement_rate > 0 ? ' improvement' : ' decline'}
                        </div>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={mockTrends.trends}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="date" />
                                <YAxis domain={[0, 100]} />
                                <Tooltip />
                                <Legend />
                                <Line type="monotone" dataKey="score" stroke="#3498db" strokeWidth={2} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                )}

                {/* Subject-wise Mock Stats */}
                {mockTrends && mockTrends.subject_stats && (
                    <div className="chart-container bar-container">
                        <h3>Subject-wise Test Performance</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={mockTrends.subject_stats}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="subject" />
                                <YAxis domain={[0, 100]} />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="avg_score" fill="#2ecc71" name="Average Score" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                )}

                {/* Weak Areas Panel */}
                <div className="weak-areas-panel">
                    <h3>🎯 Focus Areas</h3>
                    {weakAreas.length > 0 ? (
                        <div className="weak-areas-list">
                            {weakAreas.map((area, idx) => (
                                <div key={idx} className="weak-area-item">
                                    <div className="severity-indicator" style={{
                                        background: area.weakness_score > 70 ? '#e74c3c' :
                                            area.weakness_score > 40 ? '#f39c12' : '#2ecc71'
                                    }}></div>
                                    <div className="weak-area-content">
                                        <div className="weak-area-topic">{area.topic}</div>
                                        <div className="weak-area-action">💡 {area.action}</div>
                                        <div className="weak-area-source">Source: {area.source}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="no-weak-areas">🎉 Great job! No major weak areas identified.</div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AnalyticsDashboard;
