// /frontend/src/components/Syllabus/SyllabusTracker.tsx
import React, { useState, useEffect, useCallback } from 'react';
import './SyllabusTracker.css';
import { brainService } from '../../services/BrainService';
import MarkdownRenderer from '../Shared/MarkdownRenderer';
import { API_BASE_URL } from '../../config';

interface Topic {
    id: number;
    paper: string;
    subject: string;
    topic: string;
    subtopic: string | null;
    status: string;
    notes: string | null;
    last_updated: string;
    revision_count?: number;
    next_revision_date?: string;
    last_revised_at?: string;
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

    // Brain Audit State
    const [brainInsight, setBrainInsight] = useState<string | null>(null);
    const [isBrainLoading, setIsBrainLoading] = useState(false);
    const [priorityIds, setPriorityIds] = useState<number[]>([]);
    const [isPrioritizing, setIsPrioritizing] = useState(false);

    const fetchData = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/syllabus/`);
            const data = await res.json();
            setTopics(data);

            const analyticsRes = await fetch(`${API_BASE_URL}/api/syllabus/analytics`);
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
            await fetch(`${API_BASE_URL}/api/syllabus/${id}/status`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus })
            });
            // Refresh analytics in background
            const analyticsRes = await fetch(`${API_BASE_URL}/api/syllabus/analytics`);
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

    const handleMarkRevised = async (id: number) => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/syllabus/${id}/revise`, {
                method: 'POST'
            });
            const data = await res.json();

            // Update local state
            setTopics(prev => prev.map(t => t.id === id ? {
                ...t,
                revision_count: data.revision_count,
                next_revision_date: data.next_revision_date
            } : t));

        } catch (err) {
            console.error("Failed to mark revised", err);
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
            await fetch(`${API_BASE_URL}/api/syllabus/${currentTopicId}/notes`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ notes: notesText })
            });
        } catch (err) {
            console.error("Failed to save notes", err);
        }
    };

    const handleBrainAudit = async () => {
        if (!analytics) return;
        setIsBrainLoading(true);
        setBrainInsight(null);

        try {
            // Construct context
            const context = {
                analytics: analytics,
                weak_areas: analytics.breakdown.filter(b => b.status === 'Not Started' && b.count > 10).map(b => b.paper),
                completion_rates: analytics.totals.map(t => {
                    const completed = analytics.breakdown.find(b => b.paper === t.paper && b.status === 'Completed')?.count || 0;
                    return `${t.paper}: ${Math.round((completed / t.total) * 100)}%`;
                })
            };

            const response = await brainService.think(
                "Analyze my syllabus progress and give me a strategic audit. Identify bottlenecks and suggest focus areas.",
                context
            );
            setBrainInsight(response.response_text);
        } catch (error) {
            setBrainInsight("Strategos is currently unavailable. Please try again later.");
        } finally {
            setIsBrainLoading(false);
        }
    };

    const handlePrioritize = async () => {
        setIsPrioritizing(true);
        try {
            const result = await brainService.executeAction('PRIORITIZE_SYLLABUS', {});
            if (result.success) {
                setPriorityIds(result.priority_ids);
                alert(`Strategos has identified ${result.priority_ids.length} high-yield topics.`);
            } else {
                alert("Prioritization failed: " + result.message);
            }
        } catch (err) {
            console.error("Prioritization error:", err);
            alert("Strategos is silent.");
        } finally {
            setIsPrioritizing(false);
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
                <div>
                    <h1>Syllabus Tracker</h1>
                    <p>Track your conquest of the UPSC syllabus, topic by topic.</p>
                </div>
                <button
                    className="brain-audit-btn"
                    onClick={handlePrioritize}
                    disabled={isPrioritizing}
                    style={{ marginRight: '10px', background: '#e74c3c' }}
                >
                    {isPrioritizing ? 'Scanning...' : '🔥 Prioritize'}
                </button>
                <button
                    className="brain-audit-btn"
                    onClick={handleBrainAudit}
                    disabled={isBrainLoading}
                >
                    {isBrainLoading ? 'Analyzing...' : '🧠 Strategos Audit'}
                </button>
            </div>

            {/* DASHBOARD */}
            <div className="syllabus-dashboard">
                {['Prelims', 'GS1', 'GS2', 'GS3', 'GS4', 'Optional'].map(paper => (
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
                        <button
                            className="paper-header"
                            onClick={() => togglePaper(paper)}
                            aria-expanded={expandedPapers[paper]}
                            aria-controls={`paper-content-${paper}`}
                        >
                            <h2>{paper}</h2>
                            <span>{expandedPapers[paper] ? '▼' : '▶'}</span>
                        </button>

                        {expandedPapers[paper] && (
                            <div id={`paper-content-${paper}`} className="subject-list">
                                {Object.entries(subjects).sort().map(([subject, subjectTopics]) => {
                                    const subjectKey = `${paper}-${subject}`;
                                    return (
                                        <div key={subjectKey} className="subject-item">
                                            <button
                                                className="subject-header"
                                                onClick={() => toggleSubject(subjectKey)}
                                                aria-expanded={expandedSubjects[subjectKey]}
                                                aria-controls={`subject-content-${subjectKey}`}
                                            >
                                                <span>{subject}</span>
                                                <span style={{ fontSize: '0.8rem', opacity: 0.6 }}>
                                                    {subjectTopics.filter(t => t.status === 'Completed').length}/{subjectTopics.length} Done
                                                </span>
                                            </button>

                                            {expandedSubjects[subjectKey] && (
                                                <div id={`subject-content-${subjectKey}`} className="topic-list">
                                                    {subjectTopics.map(topic => (
                                                        <div key={topic.id} className={`topic-item ${priorityIds.includes(topic.id) ? 'high-priority' : ''}`}>
                                                            <div className="topic-content">
                                                                <div className="topic-text">
                                                                    {priorityIds.includes(topic.id) && <span title="High Yield Topic">🔥 </span>}
                                                                    {topic.topic}
                                                                </div>
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
                                                                <button
                                                                    className="revise-btn"
                                                                    onClick={() => handleMarkRevised(topic.id)}
                                                                    title={`Mark as Revised (Count: ${topic.revision_count || 0})`}
                                                                >
                                                                    ↻
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
                                                            {topic.next_revision_date && (
                                                                <div className={`revision-badge ${new Date(topic.next_revision_date) <= new Date() ? 'due' : ''}`}>
                                                                    Next: {new Date(topic.next_revision_date).toLocaleDateString()}
                                                                </div>
                                                            )}
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

            {/* BRAIN INSIGHT MODAL */}
            {(brainInsight || isBrainLoading) && (
                <div className="notes-modal-overlay" onClick={() => !isBrainLoading && setBrainInsight(null)}>
                    <div className="notes-modal brain-modal" onClick={e => e.stopPropagation()}>
                        <h3>Strategos Strategic Audit</h3>
                        {isBrainLoading ? (
                            <div className="loading-spinner">Analyzing Syllabus Matrix...</div>
                        ) : (
                            <div className="brain-content">
                                <MarkdownRenderer content={brainInsight || ''} />
                            </div>
                        )}
                        {!isBrainLoading && (
                            <div className="modal-actions">
                                <button className="save-btn" onClick={() => setBrainInsight(null)}>Acknowledge</button>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default SyllabusTracker;
