import React, { useState, useMemo, useEffect, useRef } from 'react';
import './Renderers.css';
import { motion, AnimatePresence } from 'framer-motion';
import {
    FaSearch, FaSortAlphaDown, FaSortAlphaUp, FaList, FaStream,
    FaExpandAlt, FaPlay, FaPause
} from 'react-icons/fa';
// import MarkdownRenderer from '../../Shared/MarkdownRenderer';

interface TimelineEvent {
    id: string; // Unique ID for keys
    year: string;
    numericYear: number;
    endYear?: number; // For ranges
    event: string;
    description?: string;
    category?: string;
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

    // Advanced Features State
    const [isPlaying, setIsPlaying] = useState(false);
    const [zoomLevel, setZoomLevel] = useState(1); // 0.5 to 2.0
    const presentationTimerRef = useRef<number | null>(null);

    // --- Parser Logic (Enhanced) ---
    const parseTimeline = (text: string, meta: any): TimelineEvent[] => {
        if (meta && Array.isArray(meta.events)) {
            return meta.events.map((e: any, idx: number) => ({
                id: `meta-${idx}`,
                year: e.year || e.date,
                numericYear: parseInt(String(e.year || e.date).replace(/\D/g, '')) || 0,
                endYear: e.end_year ? parseInt(String(e.end_year).replace(/\D/g, '')) : undefined,
                event: e.title || e.event,
                description: e.description,
                category: e.category
            }));
        }

        const lines = text.split('\n');
        const events: TimelineEvent[] = [];

        lines.forEach((line, idx) => {
            if (!line.trim()) return;
            const cleanLine = line.replace(/^[\-\*]\s*/, '').trim();

            // Enhanced Regex: Captures "1939-1945" or "1947"
            const match = cleanLine.match(/^((?:\d{4}(?:\s?-\s?\d{4})?)|\d{4}(?:\s?BC|AD|BCE|CE)?|c\.\s?\d{4})[:\-\s]+(.+)/i);

            if (match) {
                const yearStr = match[1].trim();
                const rest = match[2].trim();

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

                // Range parsing
                const rangeMatch = yearStr.match(/(\d{4})\s?-\s?(\d{4})/);
                let numYear = 0;
                let endYear: number | undefined = undefined;

                if (rangeMatch) {
                    numYear = parseInt(rangeMatch[1]);
                    endYear = parseInt(rangeMatch[2]);
                } else {
                    const numMatch = yearStr.match(/(\d+)/);
                    numYear = numMatch ? parseInt(numMatch[1]) : 0;
                    if (yearStr.toUpperCase().includes('BC') || yearStr.toUpperCase().includes('BCE')) {
                        numYear = -numYear;
                    }
                }

                events.push({
                    id: `text-${idx}`,
                    year: yearStr,
                    numericYear: numYear,
                    endYear,
                    event: title.replace(/^\*\*|\*\*$/g, ''),
                    description: desc,
                });
            }
        });
        return events;
    };

    const allEvents = useMemo(() => parseTimeline(content, metadata), [content, metadata]);

    // --- Eras & Filtering ---
    const eras = useMemo(() => {
        const uniqueEras = new Set<string>();
        uniqueEras.add('all');
        allEvents.forEach(e => {
            if (e.numericYear !== 0) {
               const century = Math.floor((Math.abs(e.numericYear) - 1) / 100) + 1;
               const eraLabel = e.numericYear < 0 ? `${century}c BC` : `${century}c AD`;
               uniqueEras.add(eraLabel);
            }
        });
        return Array.from(uniqueEras).sort((a, b) => {
            if (a === 'all') return -1;
            if (b === 'all') return 1;
            return a.localeCompare(b, undefined, { numeric: true });
        });
    }, [allEvents]);

    const filteredEvents = useMemo(() => {
        const processed = allEvents.filter(e => {
            const matchesSearch =
                e.event.toLowerCase().includes(searchTerm.toLowerCase()) ||
                e.year.toLowerCase().includes(searchTerm.toLowerCase()) ||
                (e.description && e.description.toLowerCase().includes(searchTerm.toLowerCase()));

            if (!matchesSearch) return false;
            if (activeTab !== 'all') {
                if (e.numericYear === 0) return true;
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


    // --- Presentation Mode Logic ---
    useEffect(() => {
        if (isPlaying && filteredEvents.length > 0) {
            presentationTimerRef.current = window.setInterval(() => {
                setSelectedEvent(prev => {
                    const currentIndex = prev ? filteredEvents.findIndex(e => e.id === prev.id) : -1;
                    const nextIndex = currentIndex + 1;
                    if (nextIndex >= filteredEvents.length) {
                        setIsPlaying(false); // Stop at end
                        return prev;
                    }
                    return filteredEvents[nextIndex];
                });
            }, 4000); // 4 seconds per slide
        } else {
            if (presentationTimerRef.current) {
                clearInterval(presentationTimerRef.current);
            }
        }
        return () => {
            if (presentationTimerRef.current) clearInterval(presentationTimerRef.current);
        };
    }, [isPlaying, filteredEvents]);

    // Helper to highlight text
    const HighlightText = ({ text, highlight }: { text: string, highlight: string }) => {
        if (!highlight.trim()) return <>{text}</>;
        const parts = text.split(new RegExp(`(${highlight})`, 'gi'));
        return (
            <>
                {parts.map((part, i) =>
                    part.toLowerCase() === highlight.toLowerCase() ?
                    <span key={i} className="search-highlight">{part}</span> : part
                )}
            </>
        );
    };

    // --- Renderers ---

    const renderVertical = () => (
        <div className="timeline-vertical" style={{ '--zoom-scale': zoomLevel } as React.CSSProperties}>
            <div className="timeline-center-line"></div>
            {filteredEvents.map((evt, idx) => (
                <motion.div
                    key={evt.id}
                    className={`timeline-node ${idx % 2 === 0 ? 'left' : 'right'}`}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    onClick={() => setSelectedEvent(evt)}
                    style={{ marginBottom: `${2 * zoomLevel}rem` }}
                >
                    <div className="node-content glass-card hover-glow">
                        <div className="node-date">{evt.year}</div>
                        <h4 className="node-title"><HighlightText text={evt.event} highlight={searchTerm} /></h4>
                        {evt.description && (
                            <p className="node-desc-preview">
                                <HighlightText text={evt.description.substring(0, 100)} highlight={searchTerm} />
                                {evt.description.length > 100 ? '...' : ''}
                            </p>
                        )}
                    </div>
                    <div className="node-dot"></div>
                </motion.div>
            ))}
        </div>
    );

    const renderHorizontal = () => (
        <div className="timeline-horizontal-wrapper custom-scrollbar">
            <div className="timeline-horizontal-track" style={{ gap: `${40 * zoomLevel}px` }}>
                <div className="timeline-horiz-line"></div>
                {filteredEvents.map((evt, idx) => {
                    // Calculate duration width if endYear exists
                    let durationWidth = 0;
                    if (evt.endYear && evt.numericYear) {
                         // extremely simplified pixel mapping
                         durationWidth = (evt.endYear - evt.numericYear) * 10 * zoomLevel;
                         if (durationWidth < 0) durationWidth = 0;
                    }

                    return (
                        <motion.div
                            key={evt.id}
                            className="timeline-card-horiz glass-card"
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: idx * 0.05 }}
                            onClick={() => setSelectedEvent(evt)}
                            style={{ minWidth: durationWidth > 200 ? `${durationWidth}px` : '200px' }}
                        >
                            <div className="horiz-dot"></div>
                            {durationWidth > 0 && <div className="duration-bar" style={{ width: '100%' }}></div>}
                            <div className="horiz-date">{evt.year}</div>
                            <h4 className="horiz-title"><HighlightText text={evt.event} highlight={searchTerm} /></h4>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );

    const renderCompact = () => (
        <div className="timeline-compact">
            {filteredEvents.map((evt) => (
                <div key={evt.id} className="compact-row" onClick={() => setSelectedEvent(evt)}>
                    <span className="compact-date">{evt.year}</span>
                    <span className="compact-title"><HighlightText text={evt.event} highlight={searchTerm} /></span>
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
                            placeholder="Search & Highlight..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <button className="icon-btn" onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')} title="Sort Date">
                        {sortOrder === 'asc' ? <FaSortAlphaDown /> : <FaSortAlphaUp />}
                    </button>

                    {/* Zoom Control */}
                    <div className="zoom-control">
                        <span className="zoom-label">Zoom</span>
                        <input
                            type="range"
                            min="0.5"
                            max="2"
                            step="0.1"
                            value={zoomLevel}
                            onChange={(e) => setZoomLevel(parseFloat(e.target.value))}
                            title="Adjust Density"
                        />
                    </div>
                </div>

                <div className="control-group view-toggles">
                     {/* Presentation Toggle */}
                    <button
                        className={`view-btn play-btn ${isPlaying ? 'active-pulse' : ''}`}
                        onClick={() => {
                            if (!isPlaying && !selectedEvent && filteredEvents.length > 0) {
                                setSelectedEvent(filteredEvents[0]);
                            }
                            setIsPlaying(!isPlaying);
                        }}
                        title={isPlaying ? "Pause Presentation" : "Start Presentation"}
                    >
                        {isPlaying ? <FaPause /> : <FaPlay />}
                    </button>

                    <div className="divider-v"></div>

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

            {/* Detail Modal / Presentation Overlay */}
            <AnimatePresence>
                {selectedEvent && (
                    <motion.div
                        className="event-modal-overlay"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => !isPlaying && setSelectedEvent(null)}
                    >
                        <motion.div
                            className={`event-modal glass-panel ${isPlaying ? 'presentation-mode' : ''}`}
                            initial={{ scale: 0.8, y: 50 }}
                            animate={{ scale: 1, y: 0 }}
                            exit={{ scale: 0.8, y: 50 }}
                            onClick={e => e.stopPropagation()}
                        >
                            {!isPlaying && (
                                <button className="close-modal-btn" onClick={() => setSelectedEvent(null)}>×</button>
                            )}

                            {isPlaying && (
                                <div className="presentation-controls">
                                    <button onClick={() => setIsPlaying(false)} title="Exit Presentation">Exit</button>
                                    <span className="presentation-status">Auto-Playing...</span>
                                </div>
                            )}

                            <h2 className="modal-year neon-text">{selectedEvent.year}</h2>
                            <h3 className="modal-title">{selectedEvent.event}</h3>
                            <div className="modal-desc custom-scrollbar">
                                {selectedEvent.description ? (
                                    <p>{selectedEvent.description}</p>
                                ) : (
                                    <p className="no-desc">No detailed description available.</p>
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
