import React from 'react';

export interface Topic {
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

export const STATUS_OPTIONS = [
    'Not Started',
    'Reading',
    'Notes Done',
    'Revision 1',
    'Revision 2',
    'Completed'
];

interface TopicItemProps {
    topic: Topic;
    isHighPriority: boolean;
    openNotes: (topic: Topic) => void;
    handleMarkRevised: (id: number) => void;
    handleStatusChange: (id: number, status: string) => void;
}

const TopicItem: React.FC<TopicItemProps> = React.memo(({
    topic,
    isHighPriority,
    openNotes,
    handleMarkRevised,
    handleStatusChange
}) => {
    return (
        <div className={`topic-item ${isHighPriority ? 'high-priority' : ''}`}>
            <div className="topic-content">
                <div className="topic-text">
                    {isHighPriority && <span title="High Yield Topic">🔥 </span>}
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
                    type="button"
                >
                    📝
                </button>
                <button
                    className="revise-btn"
                    onClick={() => handleMarkRevised(topic.id)}
                    title={`Mark as Revised (Count: ${topic.revision_count || 0})`}
                    type="button"
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
    );
});

export default TopicItem;
