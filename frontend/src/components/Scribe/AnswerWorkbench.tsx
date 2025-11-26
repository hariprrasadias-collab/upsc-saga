import React, { useState, useEffect } from 'react';
// Force rebuild
import './Scribe.css';
import DetailedReport from './DetailedReport';

interface HistoryItem {
    id: number;
    question_text: string;
    score: number;
    created_at: string;
}

const AnswerWorkbench: React.FC = () => {
    const [activeTab, setActiveTab] = useState<'write' | 'history'>('write');
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const [loading, setLoading] = useState(false);
    const [evaluation, setEvaluation] = useState<any>(null);
    const [history, setHistory] = useState<HistoryItem[]>([]);
    const [historyLoading, setHistoryLoading] = useState(false);

    const fetchHistory = async () => {
        setHistoryLoading(true);
        try {
            const res = await fetch('http://localhost:5000/api/scribe/history');
            const data = await res.json();
            if (res.ok) {
                setHistory(data);
            }
        } catch (err) {
            console.error("Failed to fetch history:", err);
        } finally {
            setHistoryLoading(false);
        }
    };

    useEffect(() => {
        if (activeTab === 'history') {
            fetchHistory();
        }
    }, [activeTab]);

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
                // Refresh history if we switch tabs later
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
                <h1 className="scribe-title">THE SCRIBE 2.0</h1>
                <div className="scribe-tabs">
                    <button
                        className={`tab-btn ${activeTab === 'write' ? 'active' : ''}`}
                        onClick={() => setActiveTab('write')}
                    >
                        Write
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
                        onClick={() => setActiveTab('history')}
                    >
                        History
                    </button>
                </div>
                <div className="runes-decoration"></div>
            </div>

            <div className="scribe-content">
                {activeTab === 'write' ? (
                    <div className="scribe-workbench">
                        {/* Left Panel: Question */}
                        <div className="question-panel">
                            <h3 className="panel-title">Question</h3>
                            <textarea
                                className="question-textarea"
                                placeholder="Type or paste your UPSC Mains question here..."
                                value={question}
                                onChange={(e) => setQuestion(e.target.value)}
                            />
                        </div>

                        {/* Right Panel: Writing Area */}
                        <div className="writing-panel">
                            <h3 className="panel-title">Your Answer</h3>
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
                                <DetailedReport
                                    data={evaluation}
                                    onClose={() => setEvaluation(null)}
                                />
                            )}
                        </div>
                    </div>
                ) : (
                    <div className="history-panel">
                        <div className="history-list">
                            {historyLoading ? (
                                <div className="loading-text">Loading archives...</div>
                            ) : history.length === 0 ? (
                                <div className="empty-text">No past evaluations found.</div>
                            ) : (
                                history.map(item => (
                                    <div key={item.id} className="history-item">
                                        <div className="history-score-circle" style={{
                                            borderColor: item.score >= 8 ? '#4ade80' : item.score >= 5 ? '#f59e0b' : '#f44336',
                                            color: item.score >= 8 ? '#4ade80' : item.score >= 5 ? '#f59e0b' : '#f44336'
                                        }}>
                                            {item.score}
                                        </div>
                                        <div className="history-details">
                                            <div className="history-question">{item.question_text}</div>
                                            <div className="history-date">{new Date(item.created_at).toLocaleDateString()}</div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>

                        {/* Simple Trend Chart */}
                        <div className="trend-chart-container">
                            <h3>Performance Trend</h3>
                            <div className="trend-bars">
                                {history.slice(0, 10).reverse().map((item, i) => (
                                    <div key={i} className="trend-bar-wrapper" title={`Score: ${item.score}`}>
                                        <div
                                            className="trend-bar"
                                            style={{
                                                height: `${(item.score / 15) * 100}%`, // Adjusted for max score 15
                                                backgroundColor: item.score >= 8 ? '#4ade80' : item.score >= 5 ? '#f59e0b' : '#f44336'
                                            }}
                                        ></div>
                                        <span className="trend-label">{i + 1}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AnswerWorkbench;
