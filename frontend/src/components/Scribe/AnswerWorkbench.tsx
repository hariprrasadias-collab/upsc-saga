import React, { useState } from 'react';
import './Scribe.css';
import EvaluationReport from './EvaluationReport';

const AnswerWorkbench: React.FC = () => {
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const [loading, setLoading] = useState(false);
    const [evaluation, setEvaluation] = useState<any>(null);

    const handleEvaluate = async () => {
        if (!question.trim() || !answer.trim()) return;

        setLoading(true);
        try {
            const res = await fetch('http://localhost:5000/api/scribe/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question, answer })
            });
            const data = await res.json();

            if (res.ok) {
                setEvaluation(data.feedback);
            } else {
                console.error("Evaluation failed:", data.error);
                alert("Failed to evaluate answer. Please try again.");
            }
        } catch (err) {
            console.error("Network error:", err);
            alert("Network error. Please check your connection.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="scribe-container">
            <div className="scribe-header">
                <h1 className="scribe-title">THE SCRIBE</h1>
                <div className="runes-decoration"></div>
            </div>

            <div className="scribe-workbench">
                {/* Left Panel: Question */}
                <div className="question-panel">
                    <h3 className="panel-title">Question</h3>
                    <div className="question-input-group">
                        <label>Enter Question Text</label>
                        <textarea
                            className="question-textarea"
                            placeholder="Type or paste your UPSC Mains question here..."
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                        />
                    </div>

                    {/* Future: Add PYQ Selector here */}
                </div>

                {/* Right Panel: Writing Area */}
                <div className="writing-panel">
                    <textarea
                        className="writing-area"
                        placeholder="Begin your answer here, aspirant..."
                        value={answer}
                        onChange={(e) => setAnswer(e.target.value)}
                    />

                    <div className="toolbar">
                        <button
                            className="evaluate-btn"
                            onClick={handleEvaluate}
                            disabled={loading || !question || !answer}
                        >
                            {loading ? 'Consulting the Oracle...' : 'Evaluate Answer'}
                        </button>
                    </div>

                    {evaluation && (
                        <EvaluationReport
                            data={evaluation}
                            onClose={() => setEvaluation(null)}
                        />
                    )}
                </div>
            </div>
        </div>
    );
};

export default AnswerWorkbench;
