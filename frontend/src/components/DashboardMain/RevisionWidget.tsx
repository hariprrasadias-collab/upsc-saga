import React, { useState, useEffect } from 'react';
import './RevisionWidget.css';

interface DueTopic {
    id: number;
    title: string;
    subject: string;
    paper: string;
    revision_count: number;
    next_revision_date: string;
}

const RevisionWidget: React.FC = () => {
    const [dueTopics, setDueTopics] = useState<DueTopic[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchDueTopics = async () => {
        try {
            const res = await fetch('http://localhost:5000/api/syllabus/due');
            const data = await res.json();
            setDueTopics(data);
        } catch (err) {
            console.error('Failed to load due revisions', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDueTopics();
    }, []);

    const handleQuickRevise = async (id: number) => {
        try {
            await fetch(`http://localhost:5000/api/syllabus/${id}/revise`, {
                method: 'POST',
            });
            setDueTopics(prev => prev.filter(t => t.id !== id));
        } catch (err) {
            console.error('Failed to revise', err);
        }
    };

    if (loading) return <div className="revision-widget loading">Loading Revisions...</div>;

    return (
        <div className="revision-widget">
            <div className="widget-header">
                <h3>📅 Revision Targets</h3>
                <span className="due-count">{dueTopics.length} Due</span>
            </div>

            {dueTopics.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">🎉</div>
                    <p>All caught up! No revisions due today.</p>
                </div>
            ) : (
                <div className="due-list">
                    {dueTopics.slice(0, 5).map(topic => (
                        <div key={topic.id} className="due-item">
                            <div className="due-info">
                                <div className="due-subject">{topic.paper} • {topic.subject}</div>
                                <div className="due-title">{topic.title}</div>
                            </div>
                            <button
                                className="quick-revise-btn"
                                onClick={() => handleQuickRevise(topic.id)}
                                title="Mark Revised"
                            >
                                ✓
                            </button>
                        </div>
                    ))}
                    {dueTopics.length > 5 && (
                        <div className="more-count">
                            + {dueTopics.length - 5} more topics due
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default RevisionWidget;
