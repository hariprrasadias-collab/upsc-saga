import React from 'react';
import './OracleDashboard.css';

interface OracleDashboardProps {
    data: any;
}

const OracleDashboard: React.FC<OracleDashboardProps> = ({ data }) => {
    if (!data) return null;

    return (
        <div className="oracle-dashboard">
            <h2 className="section-title">🧠 Oracle's Vision (Predictive Insights)</h2>

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
                                strokeDasharray={`${(data.exam_readiness?.overall_score || 0) * 5.03} 503`}
                                strokeLinecap="round"
                                transform="rotate(-90 100 100)"
                            />
                            <text x="100" y="100" textAnchor="middle" dy=".3em" fontSize="40" fill="#d4a574">
                                {data.exam_readiness?.overall_score || 0}%
                            </text>
                        </svg>
                    </div>
                    <div className="readiness-breakdown">
                        {data.exam_readiness?.breakdown && Object.entries(data.exam_readiness.breakdown).map(([key, value]: [string, any]) => (
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
                            {data.success_probability?.probability || 0}%
                        </div>
                        <div className="probability-bar">
                            <div
                                className="probability-fill"
                                style={{ width: `${data.success_probability?.probability || 0}%` }}
                            ></div>
                        </div>
                        <div className="probability-info">
                            <span className={`confidence confidence-${data.success_probability?.confidence}`}>
                                {data.success_probability?.confidence} confidence
                            </span>
                            <span className={`trend trend-${data.success_probability?.trend}`}>
                                {data.success_probability?.trend}
                            </span>
                        </div>
                        <p className="probability-message">{data.success_probability?.message}</p>
                    </div>
                </div>

                {/* Optimal Study Time */}
                <div className="predictive-card study-time-card">
                    <h3>⏰ Optimal Study Time</h3>
                    {data.optimal_study_time?.peak_hours ? (
                        <>
                            <div className="study-time-recommendation">
                                {data.optimal_study_time.recommendation}
                            </div>
                            <div className="peak-hours">
                                {data.optimal_study_time.formatted_times?.map((time: string, i: number) => (
                                    <div key={i} className="peak-hour-badge">{time}</div>
                                ))}
                            </div>
                            <p className="study-time-suggestion">{data.optimal_study_time.suggestion}</p>
                        </>
                    ) : (
                        <p className="no-data">{data.optimal_study_time?.message || 'Not enough data'}</p>
                    )}
                </div>

                {/* Study Analytics */}
                <div className="predictive-card study-analytics-card">
                    <h3>⏳ Chronos Analytics</h3>
                    <div className="analytics-content">
                        <div className="stat-row">
                            <span className="stat-label">Total Focus Time</span>
                            <span className="stat-value highlight">
                                {data.study_analytics?.total_hours || '0h 0m'}
                            </span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">Sessions Conquered</span>
                            <span className="stat-value">
                                {data.study_analytics?.sessions_completed || 0}
                            </span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">Efficiency</span>
                            <span className="stat-value">
                                {data.study_analytics?.efficiency || '100%'}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default OracleDashboard;
