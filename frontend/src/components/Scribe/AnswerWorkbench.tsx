import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';
// Force rebuild
import './Scribe.css';
import DetailedReport from './DetailedReport';

interface HistoryItem {
    id: number;
    question_text: string;
    answer_text: string;
    score: number;
    feedback_json: any;
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
    const [selectedHistoryItem, setSelectedHistoryItem] = useState<HistoryItem | null>(null);

    const fetchHistory = async () => {
        setHistoryLoading(true);
        try {
            const res = await fetch(`${API_BASE_URL}/api/scribe/history`);
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
            const res = await fetch(`${API_BASE_URL}/api/scribe/evaluate`, {
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
                                    <div
                                        key={item.id}
                                        className="history-item clickable"
                                        onClick={() => setSelectedHistoryItem(item)}
                                    >
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
                                        <div className="history-arrow">→</div>
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

            {/* History Detail Modal */}
            {selectedHistoryItem && (
                <div className="modal-overlay" onClick={() => setSelectedHistoryItem(null)}>
                    <div className="modal-content history-modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Evaluation Details</h2>
                            <button className="close-btn" onClick={() => setSelectedHistoryItem(null)} aria-label="Close"><span aria-hidden="true">×</span></button>
                        </div>
                        <div className="modal-body">
                            <div className="history-modal-section">
                                <h3>Question</h3>
                                <div className="history-modal-text">{selectedHistoryItem.question_text}</div>
                            </div>

                            <div className="history-modal-section">
                                <h3>Your Answer</h3>
                                <div className="history-modal-text answer-text">{selectedHistoryItem.answer_text}</div>
                            </div>

                            <div className="history-modal-section">
                                <h3>AI Feedback (Score: {selectedHistoryItem.score}/15)</h3>
                                <DetailedReport
                                    data={selectedHistoryItem.feedback_json}
                                    onClose={() => setSelectedHistoryItem(null)}
                                    embedded={true}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AnswerWorkbench;
