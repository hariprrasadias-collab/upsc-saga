import React from 'react';
import './Scribe.css';

interface EvaluationReportProps {
    data: {
        score: number;
        strengths: string[];
        weaknesses: string[];
        improvements: string[];
        model_comparison: string;
    };
    onClose: () => void;
}

const EvaluationReport: React.FC<EvaluationReportProps> = ({ data, onClose }) => {
    return (
        <div className="evaluation-overlay open">
            <button className="close-report-btn" onClick={onClose}>×</button>

            <div className="report-header">
                <div className="score-circle">
                    {data.score}
                </div>
                <div className="report-title">
                    <h2>EVALUATION REPORT</h2>
                    <span>AI-Powered Assessment</span>
                </div>
            </div>

            <div className="report-content">
                <div className="feedback-section">
                    <h3>⚔️ Strengths</h3>
                    <ul className="feedback-list">
                        {data.strengths.map((item, i) => (
                            <li key={i} className="strength">{item}</li>
                        ))}
                    </ul>
                </div>

                <div className="feedback-section">
                    <h3>🛡️ Weaknesses</h3>
                    <ul className="feedback-list">
                        {data.weaknesses.map((item, i) => (
                            <li key={i} className="weakness">{item}</li>
                        ))}
                    </ul>
                </div>

                <div className="feedback-section">
                    <h3>✨ Improvements</h3>
                    <ul className="feedback-list">
                        {data.improvements.map((item, i) => (
                            <li key={i} className="improvement">{item}</li>
                        ))}
                    </ul>
                </div>

                <div className="feedback-section">
                    <h3>📜 Model Comparison</h3>
                    <div className="model-comparison">
                        {data.model_comparison}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default EvaluationReport;
