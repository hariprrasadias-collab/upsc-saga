// /frontend/src/components/Syllabus/SyllabusTracker.tsx
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import './SyllabusTracker.css';
import { brainService } from '../../services/BrainService';
import MarkdownRenderer from '../Shared/MarkdownRenderer';
import { API_BASE_URL } from '../../config';
import TopicItem from './TopicItem';
import type { Topic } from './types';

interface Analytics {
    totals: { paper: string; total: number }[];
    breakdown: { paper: string; status: string; count: number }[];
}

interface SyllabusTrackerProps {
    onTaskCompleted?: () => void;
}

const SyllabusTracker: React.FC<SyllabusTrackerProps> = ({ onTaskCompleted }) => {
    const [topics, setTopics] = useState<Topic[]>([]);
    // Analytics is now derived from topics
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

    // Fetch only syllabus data, no separate analytics call
    const fetchData = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/syllabus/`);
            const data = await res.json();
            setTopics(data);
        } catch (err) {
            console.error("Failed to load syllabus", err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    // Derive analytics client-side
    const analytics: Analytics | null = useMemo(() => {
        if (!topics.length) return null;

        const totalsMap: Record<string, number> = {};
        const breakdownMap: Record<string, Record<string, number>> = {};

        topics.forEach(t => {
            // Totals
            totalsMap[t.paper] = (totalsMap[t.paper] || 0) + 1;

            // Breakdown
            if (!breakdownMap[t.paper]) breakdownMap[t.paper] = {};
            breakdownMap[t.paper][t.status] = (breakdownMap[t.paper][t.status] || 0) + 1;
        });

        const totals = Object.entries(totalsMap).map(([paper, total]) => ({ paper, total }));
        const breakdown: { paper: string; status: string; count: number }[] = [];

        Object.entries(breakdownMap).forEach(([paper, statuses]) => {
            Object.entries(statuses).forEach(([status, count]) => {
                breakdown.push({ paper, status, count });
            });
        });

        return { totals, breakdown };
    }, [topics]);

    const handleStatusChange = useCallback(async (id: number, newStatus: string) => {
        // Optimistic update
        setTopics(prev => prev.map(t => t.id === id ? { ...t, status: newStatus } : t));

        try {
            await fetch(`${API_BASE_URL}/api/syllabus/${id}/status`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus })
            });
            // No need to fetch analytics, it's derived from topics

            if (newStatus === 'Completed' && onTaskCompleted) {
                onTaskCompleted();
            }
        } catch (err) {
            console.error("Failed to update status", err);
            fetchData(); // Revert on error
        }
    }, [fetchData, onTaskCompleted]);

    const handleMarkRevised = useCallback(async (id: number) => {
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
    }, []);

    const openNotes = useCallback(async (topic: Topic) => {
        setCurrentTopicId(topic.id);
        setShowNotesModal(true);

        if (topic.notes !== undefined) {
            setNotesText(topic.notes || '');
            return;
        }

        if (!topic.has_notes) {
            setNotesText('');
            // Update local state to prevent future checks
            setTopics(prev => prev.map(t => t.id === topic.id ? { ...t, notes: '' } : t));
            return;
        }

        setNotesText('Loading notes...');

        try {
            const res = await fetch(`${API_BASE_URL}/api/syllabus/${topic.id}/notes`);
            if (res.ok) {
                const data = await res.json();
                const noteContent = data.notes || '';
                setNotesText(noteContent);
                // Cache it locally
                setTopics(prev => prev.map(t => t.id === topic.id ? { ...t, notes: noteContent } : t));
            } else {
                setNotesText('Error loading notes');
            }
        } catch (err) {
            console.error("Failed to fetch notes", err);
            setNotesText('Error loading notes');
        }
    }, []);

    const saveNotes = async () => {
        if (!currentTopicId) return;

        // Optimistic update
        const hasNotes = !!notesText && notesText.length > 0;
        setTopics(prev => prev.map(t => t.id === currentTopicId ? {
            ...t,
            notes: notesText,
            has_notes: hasNotes ? 1 : 0
        } : t));
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
            console.error(error); // Log error instead of unused var
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
    const groupedData = useMemo(() => {
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
                                                        <TopicItem
                                                            key={topic.id}
                                                            topic={topic}
                                                            isPriority={priorityIds.includes(topic.id)}
                                                            onStatusChange={handleStatusChange}
                                                            onMarkRevised={handleMarkRevised}
                                                            onOpenNotes={openNotes}
                                                        />
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
