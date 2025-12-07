import React, { useState, useMemo, useEffect } from 'react';
import './Renderers.css';
import { motion, AnimatePresence } from 'framer-motion';
import { FaSearch, FaSortAlphaDown, FaSortAlphaUp, FaList, FaStream, FaCalendarAlt, FaExpandAlt, FaCompressAlt } from 'react-icons/fa';

interface TimelineEvent {
    year: string;
    dateRaw?: string; // Original date string for display
    numericYear: number; // For sorting
    event: string;
    description?: string;
    category?: string; // Extracted or inferred
}

interface TimelineRendererProps {
    content: string;
    metadata?: any;
}

const TimelineRenderer: React.FC<TimelineRendererProps> = ({ content, metadata }) => {
    const [viewMode, setViewMode] = useState<'vertical' | 'horizontal' | 'compact'>('vertical');
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
    const [searchTerm, setSearchTerm] = useState('');
    const [activeTab, setActiveTab] = useState<string>('all');
    const [selectedEvent, setSelectedEvent] = useState<TimelineEvent | null>(null);

    // --- Parser Logic ---
    const parseTimeline = (text: string, meta: any): TimelineEvent[] => {
        // 1. Try to use Metadata if available (Best Source)
        if (meta && Array.isArray(meta.events)) {
            return meta.events.map((e: any) => ({
                year: e.year || e.date,
                dateRaw: e.date,
                numericYear: parseInt(String(e.year || e.date).replace(/\D/g, '')) || 0,
                event: e.title || e.event,
                description: e.description,
                category: e.category
            }));
        }

        // 2. Parse Text Content (Fallback)
        const lines = text.split('\n');
        const events: TimelineEvent[] = [];
        
        lines.forEach(line => {
            if (!line.trim()) return;

            // Regex strategies
            // Format A: "1947: Independence - India becomes free"
            // Format B: "**1947** - Independence" (Markdown bold)
            // Format C: "- 1947: Independence" (List item)

            // Clean up list markers and leading whitespace
            const cleanLine = line.replace(/^[\-\*]\s*/, '').trim();

            // Match Year at start (supports 1000 BC, c. 1500, etc.)
            // Capturing groups: 1=YearPart, 2=Rest
            // Added \s* to start and more robust separator handling
            const match = cleanLine.match(/^(\d{4}(?:\s?BC|AD|BCE|CE)?|c\.\s?\d{4}|[A-Za-z]{3}\s\d{4}|\d{1,2}(?:st|nd|rd|th)?\s[A-Za-z]+|[A-Za-z]+\s\d{1,2},?\s\d{4})[:\-\s]+(.+)/i);

            if (match) {
                const yearStr = match[1].trim();
                const rest = match[2].trim();

                // Separate Event and Description if possible (split by " - " or ": ")
                // But typically the first separator was already consumed by regex.
                // Look for a secondary separator like " - " inside 'rest'
                let title = rest;
                let desc = '';

                const splitIndex = rest.indexOf(' - ');
                if (splitIndex > 0) {
                    title = rest.substring(0, splitIndex).trim();
                    desc = rest.substring(splitIndex + 3).trim();
                } else if (rest.includes(': ')) {
                     const parts = rest.split(': ');
                     title = parts[0].trim();
                     desc = parts.slice(1).join(': ').trim();
                }

                // Try to extract numeric year for sorting
                const numMatch = yearStr.match(/(\d+)/);
                let numYear = numMatch ? parseInt(numMatch[1]) : 0;
                if (yearStr.toUpperCase().includes('BC') || yearStr.toUpperCase().includes('BCE')) {
                    numYear = -numYear;
                }

                events.push({
                    year: yearStr,
                    numericYear: numYear,
                    event: title.replace(/^\*\*|\*\*$/g, ''), // Remove markdown bold
                    description: desc,
                });
            }
        });

        return events;
    };

    const allEvents = useMemo(() => parseTimeline(content, metadata), [content, metadata]);

    // --- Eras / Tabs Logic ---
    const eras = useMemo(() => {
        const uniqueEras = new Set<string>();
        uniqueEras.add('all');

        allEvents.forEach(e => {
            // Group by Century logic
            if (e.numericYear !== 0) {
               const century = Math.floor((Math.abs(e.numericYear) - 1) / 100) + 1;
               const eraLabel = e.numericYear < 0 ? `${century}c BC` : `${century}c AD`;
               uniqueEras.add(eraLabel);
            }
        });

        // Sort eras naturally? 'all' first, then BC desc, then AD asc
        return Array.from(uniqueEras).sort((a, b) => {
            if (a === 'all') return -1;
            if (b === 'all') return 1;
            // Simple string sort for now, ideally sophisticated logic for BC/AD
            return a.localeCompare(b, undefined, { numeric: true });
        });
    }, [allEvents]);

    // --- Filtering & Sorting ---
    const filteredEvents = useMemo(() => {
        let processed = allEvents.filter(e => {
            const matchesSearch =
                e.event.toLowerCase().includes(searchTerm.toLowerCase()) ||
                e.year.toLowerCase().includes(searchTerm.toLowerCase()) ||
                (e.description && e.description.toLowerCase().includes(searchTerm.toLowerCase()));

            if (!matchesSearch) return false;

            if (activeTab !== 'all') {
                if (e.numericYear === 0) return true; // Keep undated events in all views usually, or maybe not
                const century = Math.floor((Math.abs(e.numericYear) - 1) / 100) + 1;
                const eraLabel = e.numericYear < 0 ? `${century}c BC` : `${century}c AD`;
                return eraLabel === activeTab;
            }
            return true;
        });

        processed.sort((a, b) => {
            const diff = a.numericYear - b.numericYear;
            return sortOrder === 'asc' ? diff : -diff;
        });

        return processed;
    }, [allEvents, searchTerm, activeTab, sortOrder]);


    // --- Renderers ---

    // Vertical "Snake" or Center Axis Layout
    const renderVertical = () => (
        <div className="timeline-vertical">
            <div className="timeline-center-line"></div>
            {filteredEvents.map((evt, idx) => (
                <motion.div
                    key={`${evt.year}-${idx}`}
                    className={`timeline-node ${idx % 2 === 0 ? 'left' : 'right'}`}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    onClick={() => setSelectedEvent(evt)}
                >
                    <div className="node-content glass-card hover-glow">
                        <div className="node-date">{evt.year}</div>
                        <h4 className="node-title">{evt.event}</h4>
                        {evt.description && <p className="node-desc-preview">{evt.description.substring(0, 100)}{evt.description.length > 100 ? '...' : ''}</p>}
                    </div>
                    <div className="node-dot"></div>
                </motion.div>
            ))}
        </div>
    );

    // Horizontal Scroll Layout
    const renderHorizontal = () => (
        <div className="timeline-horizontal-wrapper custom-scrollbar">
            <div className="timeline-horizontal-track">
                <div className="timeline-horiz-line"></div>
                {filteredEvents.map((evt, idx) => (
                    <motion.div
                        key={`${evt.year}-${idx}`}
                        className="timeline-card-horiz glass-card"
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: idx * 0.05 }}
                        onClick={() => setSelectedEvent(evt)}
                    >
                        <div className="horiz-dot"></div>
                        <div className="horiz-date">{evt.year}</div>
                        <h4 className="horiz-title">{evt.event}</h4>
                    </motion.div>
                ))}
            </div>
        </div>
    );

    // Compact List Layout
    const renderCompact = () => (
        <div className="timeline-compact">
            {filteredEvents.map((evt, idx) => (
                <div key={idx} className="compact-row" onClick={() => setSelectedEvent(evt)}>
                    <span className="compact-date">{evt.year}</span>
                    <span className="compact-title">{evt.event}</span>
                </div>
            ))}
        </div>
    );

    return (
        <div className="advanced-timeline-container">
            {/* Controls Header */}
            <div className="timeline-controls">
                <div className="control-group">
                    <div className="search-wrapper">
                        <FaSearch className="search-icon-sm" />
                        <input
                            type="text"
                            placeholder="Filter events..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <button className="icon-btn" onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')} title="Sort Date">
                        {sortOrder === 'asc' ? <FaSortAlphaDown /> : <FaSortAlphaUp />}
                    </button>
                </div>

                <div className="control-group view-toggles">
                    <button className={`view-btn ${viewMode === 'vertical' ? 'active' : ''}`} onClick={() => setViewMode('vertical')} title="Vertical View"><FaStream /></button>
                    <button className={`view-btn ${viewMode === 'horizontal' ? 'active' : ''}`} onClick={() => setViewMode('horizontal')} title="Horizontal View"><FaExpandAlt /></button>
                    <button className={`view-btn ${viewMode === 'compact' ? 'active' : ''}`} onClick={() => setViewMode('compact')} title="Compact List"><FaList /></button>
                </div>
            </div>

            {/* Era Tabs */}
            {eras.length > 2 && (
                <div className="era-tabs">
                    {eras.map(era => (
                        <button
                            key={era}
                            className={`era-tab ${activeTab === era ? 'active' : ''}`}
                            onClick={() => setActiveTab(era)}
                        >
                            {era === 'all' ? 'Full Timeline' : era}
                        </button>
                    ))}
                </div>
            )}

            {/* Main Content Area */}
            <div className={`timeline-viewport mode-${viewMode}`}>
                {filteredEvents.length === 0 ? (
                    <div className="no-events">No events found matching your criteria.</div>
                ) : (
                    <>
                        {viewMode === 'vertical' && renderVertical()}
                        {viewMode === 'horizontal' && renderHorizontal()}
                        {viewMode === 'compact' && renderCompact()}
                    </>
                )}
            </div>

            {/* Detail Modal / Overlay */}
            <AnimatePresence>
                {selectedEvent && (
                    <motion.div
                        className="event-modal-overlay"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setSelectedEvent(null)}
                    >
                        <motion.div
                            className="event-modal glass-panel"
                            initial={{ scale: 0.8, y: 50 }}
                            animate={{ scale: 1, y: 0 }}
                            exit={{ scale: 0.8, y: 50 }}
                            onClick={e => e.stopPropagation()}
                        >
                            <button className="close-modal-btn" onClick={() => setSelectedEvent(null)}>×</button>
                            <h2 className="modal-year neon-text">{selectedEvent.year}</h2>
                            <h3 className="modal-title">{selectedEvent.event}</h3>
                            <div className="modal-desc">
                                {selectedEvent.description ? (
                                    <p>{selectedEvent.description}</p>
                                ) : (
                                    <p className="no-desc">No detailed description available for this event.</p>
                                )}
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default TimelineRenderer;
