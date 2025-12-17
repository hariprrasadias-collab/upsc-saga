import React from 'react';
import { type Topic, STATUS_OPTIONS } from './types';

interface TopicItemProps {
    topic: Topic;
    isHighPriority: boolean;
    onStatusChange: (id: number, newStatus: string) => void;
    onMarkRevised: (id: number) => void;
    onOpenNotes: (topic: Topic) => void;
}

const TopicItem: React.FC<TopicItemProps> = React.memo(({
    topic,
    isHighPriority,
    onStatusChange,
    onMarkRevised,
    onOpenNotes
}) => {
    // Determine the subtopic text to display, handling both field names
    const subtopicText = topic.subtopic || topic.sub_topic;

    return (
        <div className={`topic-item ${isHighPriority ? 'high-priority' : ''}`}>
            <div className="topic-content">
                <div className="topic-text">
                    {isHighPriority && <span title="High Yield Topic">🔥 </span>}
                    {topic.topic}
                </div>
                {subtopicText && (
                    <div className="topic-meta">Subtopic: {subtopicText}</div>
                )}
            </div>
            <div className="topic-actions">
                <button
                    className={`notes-btn ${topic.notes ? 'has-notes' : ''}`}
                    onClick={() => onOpenNotes(topic)}
                    title="Add/View Notes"
                >
                    📝
                </button>
                <button
                    className="revise-btn"
                    onClick={() => onMarkRevised(topic.id)}
                    title={`Mark as Revised (Count: ${topic.revision_count || 0})`}
                >
                    ↻
                </button>
                <select
                    className={`status-select ${topic.status.toLowerCase().replace(' ', '-')}`}
                    value={topic.status}
                    onChange={(e) => onStatusChange(topic.id, e.target.value)}
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

TopicItem.displayName = 'TopicItem';

export default TopicItem;
