import React from 'react';
import './Scribe.css';

interface DetailedReportProps {
    data: {
        score: number;
        introduction_quality: string;
        body_quality: string;
        conclusion_quality: string;
        strengths: string[];
        weaknesses: string[];
        missing_keywords: string[];
        improvement_roadmap: string[];
        model_answer_structure: string;
    };
    onClose: () => void;
    embedded?: boolean;
}

const DetailedReport: React.FC<DetailedReportProps> = ({ data, onClose }) => {
    const getScoreColor = (score: number) => {
        if (score >= 8) return '#4ade80'; // Green
        if (score >= 5) return '#f59e0b'; // Orange
        return '#f44336'; // Red
    };

    return (
        <div className="report-overlay">
            <div className="report-modal">
                <div className="report-header">
                    <h2>Examiner's Evaluation</h2>
                    <button className="close-btn" onClick={onClose} aria-label="Close"><span aria-hidden="true">×</span></button>
                </div>

                <div className="report-content">
                    {/* Score Section */}
                    <div className="score-section">
                        <div className="score-circle" style={{ borderColor: getScoreColor(data.score), color: getScoreColor(data.score) }}>
                            <span className="score-value">{data.score}</span>
                            <span className="score-max">/ 15</span>
                        </div>
                        <div className="score-label">Overall Score</div>
                    </div>

                    {/* Structure Analysis */}
                    <div className="analysis-grid">
                        <div className="analysis-card">
                            <h3>Introduction</h3>
                            <p>{data.introduction_quality}</p>
                        </div>
                        <div className="analysis-card">
                            <h3>Body Content</h3>
                            <p>{data.body_quality}</p>
                        </div>
                        <div className="analysis-card">
                            <h3>Conclusion</h3>
                            <p>{data.conclusion_quality}</p>
                        </div>
                    </div>

                    {/* Strengths & Weaknesses */}
                    <div className="sw-grid">
                        <div className="sw-column strengths">
                            <h3>✅ Strengths</h3>
                            <ul>
                                {data.strengths.map((item, i) => <li key={i}>{item}</li>)}
                            </ul>
                        </div>
                        <div className="sw-column weaknesses">
                            <h3>⚠️ Areas for Improvement</h3>
                            <ul>
                                {data.weaknesses.map((item, i) => <li key={i}>{item}</li>)}
                            </ul>
                        </div>
                    </div>

                    {/* Missing Keywords */}
                    {data.missing_keywords && data.missing_keywords.length > 0 && (
                        <div className="keywords-section">
                            <h3>🔑 Missing Keywords</h3>
                            <div className="keywords-list">
                                {data.missing_keywords.map((kw, i) => (
                                    <span key={i} className="keyword-tag">{kw}</span>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Roadmap */}
                    <div className="roadmap-section">
                        <h3>🚀 Improvement Roadmap</h3>
                        <ul className="roadmap-list">
                            {data.improvement_roadmap.map((step, i) => (
                                <li key={i}>{step}</li>
                            ))}
                        </ul>
                    </div>

                    {/* Model Structure */}
                    <div className="model-structure-section">
                        <h3>📐 Ideal Answer Structure</h3>
                        <p>{data.model_answer_structure}</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DetailedReport;
