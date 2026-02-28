import { API_BASE_URL } from '../../config';

// Analytics Dashboard - Phase 2 Feature #2
import React, { useState, useEffect } from 'react';
import './Analytics.css';
import './BurnoutAlert.css';
import {
    LineChart, Line, BarChart, Bar,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

import { useAnalytics } from '../../contexts/AnalyticsContext';
import OracleDashboard from './OracleDashboard';
import SubjectRadar from './SubjectRadar';
import PerformanceScatter from './PerformanceScatter';
import FocusAreasPanel from './FocusAreasPanel';

interface AnalyticsDashboardProps {
    onNavigate?: (tab: string) => void;
}

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ onNavigate }) => {
    const { analytics: overview, loading: contextLoading } = useAnalytics();
    // ... existing state ...
    const [timeframe, setTimeframe] = useState<'7d' | '30d' | 'all'>('30d');
    const [subjectData, setSubjectData] = useState<any[]>([]);
    const [mockTrends, setMockTrends] = useState<any>(null);
    const [weakAreas, setWeakAreas] = useState<any[]>([]);
    const [performanceData, setPerformanceData] = useState<any[]>([]);
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
            const [subjectRes, mockRes, weakRes, predictiveRes, perfRes] = await Promise.all([
                fetch(`${API_BASE_URL}/api/analytics/subject-wise`),
                fetch(`${API_BASE_URL}/api/analytics/mock-tests`),
                fetch(`${API_BASE_URL}/api/analytics/weak-areas?limit=5`),
                fetch(`${API_BASE_URL}/api/analytics/predictive/all`),
                fetch(`${API_BASE_URL}/api/analytics/performance-scatter`)
            ]);

            const _subjectData = await subjectRes.json();
            const _mockData = await mockRes.json();
            const _weakData = await weakRes.json();
            const _predictiveAnalytics = await predictiveRes.json();
            const _perfData = await perfRes.json();

            const subjectData = _subjectData.success === false ? [] : _subjectData.data || _subjectData;
            const mockData = _mockData.success === false ? null : _mockData.data || _mockData;
            const weakData = _weakData.success === false ? [] : _weakData.data || _weakData;
            const predictiveAnalytics = _predictiveAnalytics.success === false ? null : _predictiveAnalytics.data || _predictiveAnalytics;
            const perfData = _perfData.success === false ? [] : _perfData.data || _perfData;

            setSubjectData(Array.isArray(subjectData) ? subjectData : []);
            setMockTrends(mockData);
            setWeakAreas(weakData?.weak_areas || (Array.isArray(weakData) ? weakData : []));
            setPredictiveData(predictiveAnalytics);
            setPerformanceData(Array.isArray(perfData) ? perfData : []);

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

    if ((loading || contextLoading) && !overview) return <div className="analytics-loading">Loading analytics...</div>;

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
                <OracleDashboard data={predictiveData} />
            )}

            {/* Subject-Wise Performance */}

            {/* Charts Grid */}
            <div className="charts-grid">
                {/* Subject Performance Radar */}
                <SubjectRadar data={subjectData} />

                {/* Performance Scatter Plot */}
                <PerformanceScatter data={performanceData} />

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
                <FocusAreasPanel areas={weakAreas} onNavigate={onNavigate} />
            </div>
        </div>
    );
};

export default AnalyticsDashboard;
