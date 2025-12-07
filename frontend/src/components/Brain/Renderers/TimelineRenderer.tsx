import React from 'react';
import { motion } from 'framer-motion';
import './Renderers.css';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';

interface TimelineEvent {
    year: string;
    event: string;
    description?: string;
}

interface TimelineRendererProps {
    content: string;
}

const TimelineRenderer: React.FC<TimelineRendererProps> = ({ content }) => {
    // Robust parser for AI generated timelines
    // Supports:
    // 1. "Year: Event - Description"
    // 2. "**Year**: Event - Description"
    // 3. "- Year: Event"
    const parseTimeline = (text: string): TimelineEvent[] => {
        const lines = text.split('\n');
        const events: TimelineEvent[] = [];
        
        lines.forEach(line => {
            const cleanLine = line.trim().replace(/^[-*]\s+/, ''); // Remove bullet points

            // Regex strategies
            // 1. Standard: 1947: Independence
            // 2. Bold Year: **1947**: Independence
            // 3. Loose: 1947 - Independence

            let year = '';
            let rest = '';

            // Strategy A: Colon separated
            const colonMatch = cleanLine.match(/^(\*\*.*?\*\*|\d{4}(?:-\d{4})?|[^:]+):(.+)/);
            if (colonMatch) {
                year = colonMatch[1].replace(/\*\*/g, '').trim();
                rest = colonMatch[2].trim();
            } else {
                // Strategy B: Dash separated (if starts with year-like)
                const dashMatch = cleanLine.match(/^(\d{4})\s?-\s?(.+)/);
                if (dashMatch) {
                    year = dashMatch[1].trim();
                    rest = dashMatch[2].trim();
                }
            }

            if (year && rest) {
                // Split rest into event and description if possible
                // Look for second dash or just take the whole thing as event if short
                const parts = rest.split(' - ');
                let evtTitle = parts[0].trim();
                let evtDesc = parts.slice(1).join(' - ').trim();

                // If description is empty, check if event title is very long, maybe it contains description
                if (!evtDesc && evtTitle.length > 50 && evtTitle.includes('.')) {
                     const splitIdx = evtTitle.indexOf('.');
                     evtDesc = evtTitle.substring(splitIdx + 1).trim();
                     evtTitle = evtTitle.substring(0, splitIdx + 1).trim();
                }

                events.push({
                    year: year,
                    event: evtTitle,
                    description: evtDesc
                });
            }
        });
        return events;
    };

    const events = parseTimeline(content);

    if (events.length === 0) {
        return (
            <div className="timeline-container-fallback">
                 <div className="glass-card">
                    <MarkdownRenderer content={content} />
                 </div>
            </div>
        );
    }

    return (
        <div className="timeline-container-vertical">
            <div className="timeline-line"></div>
            {events.map((evt, idx) => (
                <motion.div
                    key={idx}
                    className="timeline-item-vertical"
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: idx * 0.1 }}
                >
                    <div className="timeline-marker-dot"></div>
                    <div className="timeline-date-label">{evt.year}</div>
                    <div className="timeline-content-card glass-card">
                        <h4>{evt.event}</h4>
                        {evt.description && <p>{evt.description}</p>}
                    </div>
                </motion.div>
            ))}
            <style>{`
                .timeline-container-vertical {
                    position: relative;
                    padding: 20px 0 20px 30px;
                    border-left: 2px solid rgba(168, 85, 247, 0.3);
                    margin-left: 10px;
                }
                .timeline-item-vertical {
                    position: relative;
                    margin-bottom: 30px;
                    padding-left: 20px;
                }
                .timeline-marker-dot {
                    position: absolute;
                    left: -37px;
                    top: 15px;
                    width: 12px;
                    height: 12px;
                    background: #a855f7;
                    border-radius: 50%;
                    box-shadow: 0 0 10px #a855f7;
                    z-index: 2;
                }
                .timeline-date-label {
                    font-size: 0.85rem;
                    color: #a855f7;
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                .timeline-content-card h4 {
                    margin: 0 0 5px 0;
                    color: #e2e8f0;
                }
                .timeline-content-card p {
                    margin: 0;
                    font-size: 0.9rem;
                    color: #94a3b8;
                    line-height: 1.5;
                }
            `}</style>
        </div>
    );
};

export default TimelineRenderer;
