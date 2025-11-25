import React, { useState, useEffect } from 'react';
import './Essay.css';
import EssayEditor from './EssayEditor';
import EssayEvaluation from './EssayEvaluation';

interface Submission {
    id: number;
    topic: string;
    submitted_at: string;
    score: number;
}

interface EssayWorkshopProps {
    onTaskCompleted?: (xp: number, message: string) => void;
}

const EssayWorkshop: React.FC<EssayWorkshopProps> = ({ onTaskCompleted }) => {
    const [activeTab, setActiveTab] = useState<'write' | 'history'>('write');
    const [history, setHistory] = useState<Submission[]>([]);
    const [selectedSubmission, setSelectedSubmission] = useState<any>(null);

    useEffect(() => {
        if (activeTab === 'history') {
            fetchHistory();
        }
    }, [activeTab]);

    const fetchHistory = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/essay/history');
            const data = await response.json();
            setHistory(data);
        } catch (error) {
            console.error('Error fetching history:', error);
        }
    };

    const handleViewSubmission = async (id: number) => {
        try {
            const response = await fetch(`http://localhost:5000/api/essay/${id}`);
            const data = await response.json();
            setSelectedSubmission(data);
            setActiveTab('write'); // Re-use the write tab area for viewing result
        } catch (error) {
            console.error('Error fetching submission details:', error);
        }
    };

    const handleSubmissionSuccess = (data: any) => {
        setSelectedSubmission(data);
        if (onTaskCompleted) {
            onTaskCompleted(50, 'Essay Submitted! +50 XP');
        }
    };

    return (
        <div className="essay-workshop-container">
            <header className="essay-header">
                <div className="header-content">
                    <h1>Essay Writing Workshop</h1>
                    <p>Master the art of UPSC essay writing with AI-driven evaluation</p>
                </div>
                <div className="essay-tabs">
                    <button
                        className={`tab-btn ${activeTab === 'write' && !selectedSubmission ? 'active' : ''}`}
                        onClick={() => { setActiveTab('write'); setSelectedSubmission(null); }}
                    >
                        Write New
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
                        onClick={() => setActiveTab('history')}
                    >
                        History
                    </button>
                </div>
            </header>

            <div className="essay-content">
                {activeTab === 'write' && !selectedSubmission && (
                    <EssayEditor onSubmitSuccess={handleSubmissionSuccess} />
                )}

                {activeTab === 'write' && selectedSubmission && (
                    <EssayEvaluation
                        data={selectedSubmission}
                        onBack={() => setSelectedSubmission(null)}
                    />
                )}

                {activeTab === 'history' && (
                    <div className="essay-history">
                        <h2>Past Submissions</h2>
                        <div className="history-list">
                            {history.map(sub => (
                                <div key={sub.id} className="history-card" onClick={() => handleViewSubmission(sub.id)}>
                                    <div className="history-card-header">
                                        <span className="history-date">{new Date(sub.submitted_at).toLocaleDateString()}</span>
                                        <span className="history-score">{sub.score}/250</span>
                                    </div>
                                    <h3>{sub.topic}</h3>
                                </div>
                            ))}
                            {history.length === 0 && <p className="no-history">No essays submitted yet.</p>}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default EssayWorkshop;
