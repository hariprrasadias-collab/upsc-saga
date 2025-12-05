// /frontend/src/components/Syllabus/SyllabusTracker.tsx
import React, { useState, useEffect, useCallback } from 'react';
import './SyllabusTracker.css';
import { brainService } from '../../services/BrainService';
import MarkdownRenderer from '../Shared/MarkdownRenderer';

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
    const [syllabus, setSyllabus] = useState<any[]>([]); // Using any[] for the new nested structure
    const [analytics, setAnalytics] = useState<Analytics | null>(null);
    const [loading, setLoading] = useState(true);

    // UI State for the tree
    const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>({
        // Initially expand the first paper
        'GS1': true
    });

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
            const res = await fetch('http://localhost:5000/api/syllabus/');
            const data = await res.json();
            setSyllabus(data);

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
        // Optimistic update for nested structure requires a recursive function
        const updateNodeStatus = (nodes: any[]): any[] => {
            return nodes.map(node => {
                if (node.id === id) {
                    return { ...node, status: newStatus };
                }
                if (node.children) {
                    return { ...node, children: updateNodeStatus(node.children) };
                }
                return node;
            });
        };
        setSyllabus(prev => updateNodeStatus(prev));

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

    const handleMarkRevised = async (id: number) => {
        // This function would also need a recursive update, but for now, we'll just refetch
        // for simplicity, as revision data isn't directly part of the new tree structure yet.
        try {
            await fetch(`http://localhost:5000/api/syllabus/${id}/revise`, {
                method: 'POST'
            });
            // Re-fetch to show updated revision info if we were displaying it
            // For now, it's a background task.
        } catch (err) {
            console.error("Failed to mark revised", err);
        }
    };

    const openNotes = (node: any) => {
        setCurrentTopicId(node.id);
        setNotesText(node.notes || '');
        setShowNotesModal(true);
    };

    const saveNotes = async () => {
        if (!currentTopicId) return;

        const updateNodeNotes = (nodes: any[]): any[] => {
            return nodes.map(node => {
                if (node.id === currentTopicId) {
                    return { ...node, notes: notesText };
                }
                if (node.children) {
                    return { ...node, children: updateNodeNotes(node.children) };
                }
                return node;
            });
        };
        setSyllabus(prev => updateNodeNotes(prev));
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

    const getProgress = (paper: string) => {
        if (!analytics) return 0;
        const total = analytics.totals.find(t => t.paper === paper)?.total || 0;
        if (total === 0) return 0;

        const completed = analytics.breakdown
            .filter(b => b.paper === paper && b.status === 'Completed')
            .reduce((acc, curr) => acc + curr.count, 0);

        return Math.round((completed / total) * 100);
    };

    const toggleNode = (nodeTitle: string) => {
        setExpandedNodes(prev => ({ ...prev, [nodeTitle]: !prev[nodeTitle] }));
    };

    if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading Syllabus...</div>;

    const TreeItem: React.FC<{ node: any; level: number }> = ({ node, level }) => {
        const isExpanded = !!expandedNodes[node.title];
        const hasChildren = node.children && node.children.length > 0;
        const isLeaf = !hasChildren;

        return (
            <div className={`tree-item level-${level}`}>
                <div className="tree-item-header" onClick={() => !isLeaf && toggleNode(node.title)}>
                    <span className="expand-icon">{isLeaf ? '●' : (isExpanded ? '▼' : '▶')}</span>
                    <span className="item-title">{node.title}</span>

                    {isLeaf && (
                        <div className="topic-actions">
                            <button
                                className={`notes-btn ${node.notes ? 'has-notes' : ''}`}
                                onClick={() => openNotes(node)}
                                title="Add/View Notes"
                            >
                                📝
                            </button>
                            <button
                                className="revise-btn"
                                onClick={() => handleMarkRevised(node.id)}
                                title="Mark as Revised"
                            >
                                ↻
                            </button>
                            <select
                                className={`status-select ${node.status.toLowerCase().replace(' ', '-')}`}
                                value={node.status}
                                onChange={(e) => handleStatusChange(node.id, e.target.value)}
                                onClick={e => e.stopPropagation()} // Prevent header click
                            >
                                {STATUS_OPTIONS.map(opt => (
                                    <option key={opt} value={opt}>{opt}</option>
                                ))}
                            </select>
                        </div>
                    )}
                </div>

                {isExpanded && hasChildren && (
                    <div className="tree-item-children">
                        {node.children.map((child: any, index: number) => (
                            <TreeItem key={child.id || `${child.title}-${index}`} node={child} level={level + 1} />
                        ))}
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="syllabus-container">
            <div className="syllabus-header">
                <div>
                    <h1>Syllabus Tracker</h1>
                    <p>Track your conquest of the UPSC syllabus, topic by topic.</p>
                </div>
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
                {analytics?.totals.map(p => (
                    <div key={p.paper} className="paper-card">
                        <div className="paper-title">{p.paper}</div>
                        <div className="progress-container">
                            <div
                                className="progress-bar"
                                style={{ width: `${getProgress(p.paper)}%` }}
                            ></div>
                        </div>
                        <div className="progress-text">{getProgress(p.paper)}% Completed</div>
                    </div>
                ))}
            </div>

            {/* TREE VIEW */}
            <div className="syllabus-tree">
                {syllabus.map((paperNode, index) => (
                    <TreeItem key={`${paperNode.title}-${index}`} node={paperNode} level={0} />
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
