// Analytics Dashboard - Phase 2 Feature #2
import React, { useState, useEffect } from 'react';
import './Analytics.css';
import './BurnoutAlert.css';
import {
    LineChart, Line, BarChart, Bar, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

import { useAnalytics } from '../../contexts/AnalyticsContext';

const AnalyticsDashboard: React.FC = () => {
    const { analytics: overview, loading: contextLoading } = useAnalytics();
    const [timeframe, setTimeframe] = useState<'7d' | '30d' | 'all'>('30d');
    // const [overview, setOverview] = useState<any>(null); // Removed local state
    const [subjectData, setSubjectData] = useState<any[]>([]);
    const [mockTrends, setMockTrends] = useState<any>(null);
    const [weakAreas, setWeakAreas] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    // Predictive Analytics State
    const [predictiveData, setPredictiveData] = useState<any>(null);
    const [showBurnoutAlert, setShowBurnoutAlert] = useState(false);

    useEffect(() => {
        fetchAnalytics();
    }, [timeframe]);

    const fetchAnalytics = async () => {
        try {
            setLoading(true);

            // Fetch remaining analytics data in parallel
            const [subjectRes, mockRes, weakRes, predictiveRes] = await Promise.all([
                fetch('http://localhost:5000/api/analytics/subject-wise'),
                fetch('http://localhost:5000/api/analytics/mock-tests'),
                fetch('http://localhost:5000/api/analytics/weak-areas?limit=5'),
                fetch('http://localhost:5000/api/analytics/predictive/all')
            ]);

            const subjectData = await subjectRes.json();
            const mockData = await mockRes.json();
            const weakData = await weakRes.json();
            const predictiveAnalytics = await predictiveRes.json();

            setSubjectData(subjectData);
            setMockTrends(mockData);
            setWeakAreas(weakData);
            setPredictiveData(predictiveAnalytics);

            // Show burnout alert if high risk
            if (predictiveAnalytics?.burnout_detection?.burnout_risk === 'high') {
                setShowBurnoutAlert(true);
            }

            setLoading(false);
        } catch (err) {
            console.error('Failed to fetch analytics:', err);
            setLoading(false);
        }
    };

    if (loading && !overview) return <div className="analytics-loading">Loading analytics...</div>;

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


            {/* Burnout Alert */}
            {showBurnoutAlert && predictiveData?.burnout_detection && (
                <div className="burnout-alert">
                    <div className="alert-icon">⚠️</div>
                    <div className="alert-content">
                        <h3 className="alert-title">{predictiveData.burnout_detection.message}</h3>
                        <div className="alert-recommendations">
                            <strong>Recommendations:</strong>
                            <ul>
                                {predictiveData.burnout_detection.recommendations?.map((rec: string, i: number) => (
                                    <li key={i}>{rec}</li>
                                ))}
                            </ul>
                        </div>
                        <div className="alert-stats">
                            <span>Avg Study Hours: {predictiveData.burnout_detection.avg_study_hours}h/day</span>
                        </div>
                    </div>
                    <button className="alert-dismiss" onClick={() => setShowBurnoutAlert(false)} aria-label="Dismiss alert">
                        ×
                    </button>
                </div>
            )}


            {/* Predictive Analytics Section */}
            {predictiveData && (
                <div className="predictive-analytics-section">
                    <h2 className="section-title">🧠 Predictive Insights</h2>

                    <div className="predictive-grid">
                        {/* Exam Readiness Score */}
                        <div className="predictive-card readiness-card">
                            <h3>📊 Exam Readiness</h3>
                            <div className="readiness-gauge">
                                <svg width="200" height="200" viewBox="0 0 200 200">
                                    <circle
                                        cx="100"
                                        cy="100"
                                        r="80"
                                        fill="none"
                                        stroke="#333"
                                        strokeWidth="15"
                                    />
                                    <circle
                                        cx="100"
                                        cy="100"
                                        r="80"
                                        fill="none"
                                        stroke="#d4a574"
                                        strokeWidth="15"
                                        strokeDasharray={`${(predictiveData.exam_readiness?.overall_score || 0) * 5.03} 503`}
                                        strokeLinecap="round"
                                        transform="rotate(-90 100 100)"
                                    />
                                    <text x="100" y="100" textAnchor="middle" dy=".3em" fontSize="40" fill="#d4a574">
                                        {predictiveData.exam_readiness?.overall_score || 0}%
                                    </text>
                                </svg>
                            </div>
                            <div className="readiness-breakdown">
                                {predictiveData.exam_readiness?.breakdown && Object.entries(predictiveData.exam_readiness.breakdown).map(([key, value]: [string, any]) => (
                                    <div key={key} className="breakdown-item">
                                        <span>{key.replace('_', ' ')}</span>
                                        <span className="breakdown-bar">
                                            <div style={{ width: `${value * 4}%`, background: '#d4a574' }}></div>
                                        </span>
                                        <span>{value.toFixed(1)}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Success Probability */}
                        <div className="predictive-card probability-card">
                            <h3>🎯 Success Probability</h3>
                            <div className="probability-meter">
                                <div className="probability-value">
                                    {predictiveData.success_probability?.probability || 0}%
                                </div>
                                <div className="probability-bar">
                                    <div
                                        className="probability-fill"
                                        style={{ width: `${predictiveData.success_probability?.probability || 0}%` }}
                                    ></div>
                                </div>
                                <div className="probability-info">
                                    <span className={`confidence confidence-${predictiveData.success_probability?.confidence}`}>
                                        {predictiveData.success_probability?.confidence} confidence
                                    </span>
                                    <span className={`trend trend-${predictiveData.success_probability?.trend}`}>
                                        {predictiveData.success_probability?.trend}
                                    </span>
                                </div>
                                <p className="probability-message">{predictiveData.success_probability?.message}</p>
                            </div>
                        </div>

                        {/* Optimal Study Time */}
                        <div className="predictive-card study-time-card">
                            <h3>⏰ Optimal Study Time</h3>
                            {predictiveData.optimal_study_time?.peak_hours ? (
                                <>
                                    <div className="study-time-recommendation">
                                        {predictiveData.optimal_study_time.recommendation}
                                    </div>
                                    <div className="peak-hours">
                                        {predictiveData.optimal_study_time.formatted_times?.map((time: string, i: number) => (
                                            <div key={i} className="peak-hour-badge">{time}</div>
                                        ))}
                                    </div>
                                    <p className="study-time-suggestion">{predictiveData.optimal_study_time.suggestion}</p>
                                </>
                            ) : (
                                <p className="no-data">{predictiveData.optimal_study_time?.message || 'Not enough data'}</p>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Subject-Wise Performance */}

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
