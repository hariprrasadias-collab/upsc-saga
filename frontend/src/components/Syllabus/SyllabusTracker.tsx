// /frontend/src/components/Syllabus/SyllabusTracker.tsx
import React, { useState, useEffect, useCallback } from 'react';
import './SyllabusTracker.css';

interface Topic {
    id: number;
    paper: string;
    subject: string;
    topic: string;
    subtopic: string | null;
    status: string;
    notes: string | null;
    last_updated: string;
}

interface Analytics {
    totals: { paper: string; total: number }[];
    breakdown: { paper: string; status: string; count: number }[];
}

const STATUS_OPTIONS = [
    'Not Started',
    'Reading',
    'Notes Done',
    'Revision 1',
    'Revision 2',
    'Completed'
];

interface SyllabusTrackerProps {
    onTaskCompleted?: () => void;
}

const SyllabusTracker: React.FC<SyllabusTrackerProps> = ({ onTaskCompleted }) => {
    const [topics, setTopics] = useState<Topic[]>([]);
    const [analytics, setAnalytics] = useState<Analytics | null>(null);
    const [loading, setLoading] = useState(true);

    // UI State
    const [expandedPapers, setExpandedPapers] = useState<Record<string, boolean>>({ 'GS1': true });
    const [expandedSubjects, setExpandedSubjects] = useState<Record<string, boolean>>({});

    // Notes Modal
    const [showNotesModal, setShowNotesModal] = useState(false);
    const [currentTopicId, setCurrentTopicId] = useState<number | null>(null);
    const [notesText, setNotesText] = useState('');

    const fetchData = useCallback(async () => {
        try {
            const res = await fetch('http://localhost:5000/api/syllabus/');
            const data = await res.json();
            setTopics(data);

            const analyticsRes = await fetch('http://localhost:5000/api/syllabus/analytics');
            const analyticsData = await analyticsRes.json();
            setAnalytics(analyticsData);
        } catch (err) {
            console.error("Failed to load syllabus", err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleStatusChange = async (id: number, newStatus: string) => {
        // Optimistic update
        setTopics(prev => prev.map(t => t.id === id ? { ...t, status: newStatus } : t));

        try {
            await fetch(`http://localhost:5000/api/syllabus/${id}/status`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus })
            });
            // Refresh analytics in background
            const analyticsRes = await fetch('http://localhost:5000/api/syllabus/analytics');
            const analyticsData = await analyticsRes.json();
            setAnalytics(analyticsData);

            if (newStatus === 'Completed' && onTaskCompleted) {
                onTaskCompleted();
            }
        } catch (err) {
            console.error("Failed to update status", err);
            fetchData(); // Revert on error
        }
    };

    const openNotes = (topic: Topic) => {
        setCurrentTopicId(topic.id);
        setNotesText(topic.notes || '');
        setShowNotesModal(true);
    };

    const saveNotes = async () => {
        if (!currentTopicId) return;

        // Optimistic update
        setTopics(prev => prev.map(t => t.id === currentTopicId ? { ...t, notes: notesText } : t));
        setShowNotesModal(false);

        try {
            await fetch(`http://localhost:5000/api/syllabus/${currentTopicId}/notes`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ notes: notesText })
            });
        } catch (err) {
            console.error("Failed to save notes", err);
        }
    };

    // Group Data
    const groupedData = React.useMemo(() => {
        const groups: Record<string, Record<string, Topic[]>> = {};

        topics.forEach(t => {
            if (!groups[t.paper]) groups[t.paper] = {};
            if (!groups[t.paper][t.subject]) groups[t.paper][t.subject] = [];
            groups[t.paper][t.subject].push(t);
        });

        return groups;
    }, [topics]);

    const getProgress = (paper: string) => {
        if (!analytics) return 0;
        const total = analytics.totals.find(t => t.paper === paper)?.total || 0;
        if (total === 0) return 0;

        // Count completed or in progress (weighted?)
        // Simple count: anything not 'Not Started' counts as some progress?
        // Let's do: Completed = 100%, Revision 2 = 90%, Revision 1 = 75%, Notes Done = 50%, Reading = 25%
        // Or just simple count of 'Completed' for the bar?
        // Let's do simple count of 'Completed' for now to be strict.

        const completed = analytics.breakdown
            .filter(b => b.paper === paper && b.status === 'Completed')
            .reduce((acc, curr) => acc + curr.count, 0);

        return Math.round((completed / total) * 100);
    };

    const togglePaper = (paper: string) => {
        setExpandedPapers(prev => ({ ...prev, [paper]: !prev[paper] }));
    };

    const toggleSubject = (subjectKey: string) => {
        setExpandedSubjects(prev => ({ ...prev, [subjectKey]: !prev[subjectKey] }));
    };

    if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading Syllabus...</div>;

    return (
        <div className="syllabus-container">
            <div className="syllabus-header">
                <h1>Syllabus Tracker</h1>
                <p>Track your conquest of the UPSC syllabus, topic by topic.</p>
            </div>

            {/* DASHBOARD */}
            <div className="syllabus-dashboard">
                {['GS1', 'GS2', 'GS3', 'GS4'].map(paper => (
                    <div key={paper} className="paper-card">
                        <div className="paper-title">{paper}</div>
                        <div className="progress-container">
                            <div
                                className="progress-bar"
                                style={{ width: `${getProgress(paper)}%` }}
                            ></div>
                        </div>
                        <div className="progress-text">{getProgress(paper)}% Completed</div>
                    </div>
                ))}
            </div>

            {/* TREE VIEW */}
            <div className="syllabus-tree">
                {Object.entries(groupedData).sort().map(([paper, subjects]) => (
                    <div key={paper} className="paper-section">
                        <div className="paper-header" onClick={() => togglePaper(paper)}>
                            <h2>{paper}</h2>
                            <span>{expandedPapers[paper] ? '▼' : '▶'}</span>
                        </div>

                        {expandedPapers[paper] && (
                            <div className="subject-list">
                                {Object.entries(subjects).sort().map(([subject, subjectTopics]) => {
                                    const subjectKey = `${paper}-${subject}`;
                                    return (
                                        <div key={subjectKey} className="subject-item">
                                            <div className="subject-header" onClick={() => toggleSubject(subjectKey)}>
                                                <span>{subject}</span>
                                                <span style={{ fontSize: '0.8rem', opacity: 0.6 }}>
                                                    {subjectTopics.filter(t => t.status === 'Completed').length}/{subjectTopics.length} Done
                                                </span>
                                            </div>

                                            {expandedSubjects[subjectKey] && (
                                                <div className="topic-list">
                                                    {subjectTopics.map(topic => (
                                                        <div key={topic.id} className="topic-item">
                                                            <div className="topic-content">
                                                                <div className="topic-text">{topic.topic}</div>
                                                                {topic.subtopic && (
                                                                    <div className="topic-meta">Subtopic: {topic.subtopic}</div>
                                                                )}
                                                            </div>
                                                            <div className="topic-actions">
                                                                <button
                                                                    className={`notes-btn ${topic.notes ? 'has-notes' : ''}`}
                                                                    onClick={() => openNotes(topic)}
                                                                    title="Add/View Notes"
                                                                >
                                                                    📝
                                                                </button>
                                                                <select
                                                                    className={`status-select ${topic.status.toLowerCase().replace(' ', '-')}`}
                                                                    value={topic.status}
                                                                    onChange={(e) => handleStatusChange(topic.id, e.target.value)}
                                                                >
                                                                    {STATUS_OPTIONS.map(opt => (
                                                                        <option key={opt} value={opt}>{opt}</option>
                                                                    ))}
                                                                </select>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {/* NOTES MODAL */}
            {showNotesModal && (
                <div className="notes-modal-overlay">
                    <div className="notes-modal">
                        <h3>Topic Notes</h3>
                        <textarea
                            className="notes-textarea"
                            value={notesText}
                            onChange={(e) => setNotesText(e.target.value)}
                            placeholder="Add your notes, strategy, or resource links here..."
                        />
                        <div className="modal-actions">
                            <button className="cancel-btn" onClick={() => setShowNotesModal(false)}>Cancel</button>
                            <button className="save-btn" onClick={saveNotes}>Save Notes</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SyllabusTracker;
