import React, { memo } from 'react';
import type { Topic } from './types';
import { STATUS_OPTIONS } from './types';

interface TopicItemProps {
    topic: Topic;
    isPriority: boolean;
    onStatusChange: (id: number, newStatus: string) => void;
    onMarkRevised: (id: number) => void;
    onOpenNotes: (topic: Topic) => void;
}

const TopicItem: React.FC<TopicItemProps> = memo(({
    topic,
    isPriority,
    onStatusChange,
    onMarkRevised,
    onOpenNotes
}) => {
    // Optimization: Check has_notes flag if available, fallback to notes length
    const hasNotes = topic.has_notes !== undefined ? topic.has_notes : (topic.notes && topic.notes.length > 0);

    return (
        <div className={`topic-item ${isPriority ? 'high-priority' : ''}`}>
            <div className="topic-content">
                <div className="topic-text">
                    {isPriority && <span title="High Yield Topic">🔥 </span>}
                    {topic.topic}
                </div>
                {topic.subtopic && (
                    <div className="topic-meta">Subtopic: {topic.subtopic}</div>
                )}
            </div>
            <div className="topic-actions">
                <button
                    className={`notes-btn ${hasNotes ? 'has-notes' : ''}`}
                    onClick={() => onOpenNotes(topic)}
                    title="Add/View Notes"
                    aria-label={`Notes for ${topic.topic}`}
                >
                    📝
                </button>
                <button
                    className="revise-btn"
                    onClick={() => onMarkRevised(topic.id)}
                    title={`Mark as Revised (Count: ${topic.revision_count || 0})`}
                    aria-label={`Mark ${topic.topic} as Revised`}
                >
                    ↻
                </button>
                <select
                    className={`status-select ${topic.status.toLowerCase().replace(' ', '-')}`}
                    value={topic.status}
                    onChange={(e) => onStatusChange(topic.id, e.target.value)}
                    aria-label={`Status for ${topic.topic}`}
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

// Add display name for debugging
TopicItem.displayName = 'TopicItem';

export default TopicItem;
