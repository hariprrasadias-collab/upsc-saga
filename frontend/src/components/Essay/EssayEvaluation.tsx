import React from 'react';

interface EvaluationData {
    id: number;
    topic: string;
    score: number;
    evaluation: {
        strengths: string[];
        weaknesses: string[];
        suggestions: string[];
        model_structure: {
            introduction: string;
            body_paragraphs: string[];
            conclusion: string;
        };
        overall_feedback: string;
    };
}

interface EssayEvaluationProps {
    data: EvaluationData;
    onBack: () => void;
}

const EssayEvaluation: React.FC<EssayEvaluationProps> = ({ data, onBack }) => {
    const { score, evaluation, topic } = data;

    const getScoreColor = (s: number) => {
        if (s >= 150) return '#4caf50'; // Excellent
        if (s >= 120) return '#ff9800'; // Good
        return '#f44336'; // Needs Improvement
    };

    return (
        <div className="essay-evaluation">
            <div className="evaluation-header">
                <button className="back-btn" onClick={onBack}>← Back to Editor</button>
                <h2>Evaluation Report</h2>
            </div>

            <div className="score-card">
                <div className="score-circle" style={{ borderColor: getScoreColor(score) }}>
                    <span className="score-value">{score}</span>
                    <span className="score-max">/ 250</span>
                </div>
                <div className="topic-info">
                    <h3>{topic}</h3>
                    <p className="overall-feedback">{evaluation.overall_feedback}</p>
                </div>
            </div>

            <div className="feedback-grid">
                <div className="feedback-section strengths">
                    <h3>💪 Strengths</h3>
                    <ul>
                        {evaluation.strengths.map((item, i) => (
                            <li key={i}>{item}</li>
                        ))}
                    </ul>
                </div>

                <div className="feedback-section weaknesses">
                    <h3>⚠️ Areas for Improvement</h3>
                    <ul>
                        {evaluation.weaknesses.map((item, i) => (
                            <li key={i}>{item}</li>
                        ))}
                    </ul>
                </div>
            </div>

            <div className="suggestions-section">
                <h3>💡 Key Suggestions</h3>
                <ul>
                    {evaluation.suggestions.map((item, i) => (
                        <li key={i}>{item}</li>
                    ))}
                </ul>
            </div>

            <div className="model-structure">
                <h3>🏗️ Model Essay Structure</h3>
                <div className="structure-item">
                    <h4>Introduction</h4>
                    <p>{evaluation.model_structure.introduction}</p>
                </div>
                <div className="structure-item">
                    <h4>Body Paragraphs</h4>
                    <ul>
                        {evaluation.model_structure.body_paragraphs.map((para, i) => (
                            <li key={i}>{para}</li>
                        ))}
                    </ul>
                </div>
                <div className="structure-item">
                    <h4>Conclusion</h4>
                    <p>{evaluation.model_structure.conclusion}</p>
                </div>
            </div>
        </div>
    );
};

export default EssayEvaluation;
