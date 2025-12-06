import React from 'react';
import './Renderers.css';

interface TimelineEvent {
    year: string;
    event: string;
    description?: string;
}

interface TimelineRendererProps {
    content: string;
}

const TimelineRenderer: React.FC<TimelineRendererProps> = ({ content }) => {
    // Basic parser for AI generated timelines (Expected format: "Year: Event - Description")
    const parseTimeline = (text: string): TimelineEvent[] => {
        const lines = text.split('\n');
        const events: TimelineEvent[] = [];
        
        lines.forEach(line => {
            // Regex to find Year (matches 4 digits or date-like strings at start)
            const match = line.match(/^(\d{4}|[A-Za-z]+\s\d{4}|[^:]+):(.+)/);
            if (match) {
                const parts = match[2].split('-');
                events.push({
                    year: match[1].trim(),
                    event: parts[0].trim(),
                    description: parts.slice(1).join('-').trim()
                });
            }
        });
        return events;
    };

    const events = parseTimeline(content);

    if (events.length === 0) {
        return <div className="raw-content">{content}</div>;
    }

    return (
        <div className="timeline-container">
            {events.map((evt, idx) => (
                <div key={idx} className="timeline-item">
                    <div className="timeline-marker"></div>
                    <div className="timeline-date">{evt.year}</div>
                    <div className="timeline-content glass-card">
                        <h4>{evt.event}</h4>
                        {evt.description && <p>{evt.description}</p>}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default TimelineRenderer;
