import React, { useState, useEffect, useRef } from 'react';
import './TriangulationHistory.css';
import MarkdownRenderer from '../Shared/MarkdownRenderer';
import mermaid from 'mermaid';
import { motion, AnimatePresence } from 'framer-motion';
import DOMPurify from 'dompurify';

// Mermaid Renderer Component (reused)
const MermaidDiagram: React.FC<{ code: string }> = ({ code }) => {
    const ref = useRef<HTMLDivElement>(null);
    const [renderError, setRenderError] = useState(false);

    useEffect(() => {
        if (ref.current && code) {
            try {
                mermaid.initialize({ startOnLoad: true, theme: 'dark', securityLevel: 'loose' });
                // Unique ID for each render to prevent conflicts
                const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
                ref.current.innerHTML = ''; // Clear previous
                mermaid.render(id, code).then(result => {
                    if (ref.current) {
                        ref.current.innerHTML = DOMPurify.sanitize(result.svg, {
                            USE_PROFILES: { svg: true }
                        });
                    }
                }).catch(e => {
                    console.error("Mermaid Render Error:", e);
                    setRenderError(true);
                });
            } catch (e) {
                console.error("Mermaid Init Error:", e);
                setRenderError(true);
            }
        }
    }, [code]);

    if (renderError) return <div className="error-text">Could not render diagram.</div>;

    return (
        <div className="mermaid-container" style={{ background: 'rgba(0,0,0,0.3)', padding: '20px', borderRadius: '8px' }}>
            <div ref={ref} className="mermaid" />
        </div>
    );
};

interface TriangulationReport {
    id: number;
    topic: string;
    synthesis: string;
    way_forward: any; // Legacy format
    full_report?: any; // New rich format
    created_at: string;
}

const TriangulationHistory: React.FC = () => {
    const [history, setHistory] = useState<TriangulationReport[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedReport, setSelectedReport] = useState<TriangulationReport | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [activeTab, setActiveTab] = useState<'overview' | 'analysis' | 'evidence' | 'strategy'>('overview');
    const [isDecrypting, setIsDecrypting] = useState(false);
    const [extracting, setExtracting] = useState(false);

    useEffect(() => {
        if (selectedReport) {
            setIsDecrypting(true);
            const timer = setTimeout(() => setIsDecrypting(false), 1200);
            return () => clearTimeout(timer);
        }
    }, [selectedReport]);

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/triangulation/history?limit=50');
            const data = await response.json();
            if (data.success) {
                setHistory(data.data);
                // Auto-select first if available
                if (data.data.length > 0 && !selectedReport) {
                    setSelectedReport(data.data[0]);
                }
            }
        } catch (error) {
            console.error("Failed to fetch Triangulation history", error);
        } finally {
            setLoading(false);
        }
    };

    const handleExtractActionables = async () => {
        if (!selectedReport?.full_report?.way_forward) return;
        setExtracting(true);
        try {
            const response = await fetch('http://127.0.0.1:5000/api/triangulation/extract-actionables', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic: selectedReport.topic,
                    way_forward: selectedReport.full_report.way_forward
                })
            });
            const data = await response.json();
            if (data.success) {
                alert('Actionables successfully injected into the Task Queue!');
            } else {
                alert('Extraction failed: ' + data.error);
            }
        } catch (error) {
            console.error(error);
            alert('Oracle Connection Error.');
        } finally {
            setExtracting(false);
        }
    };

    const filteredHistory = history.filter(item =>
        item.topic.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const renderContent = () => {
        if (!selectedReport) return <div className="placeholder-text">Select a report to inspect.</div>;

        const isRich = !!selectedReport.full_report && Object.keys(selectedReport.full_report).length > 0;
        const data = selectedReport.full_report || {};

        if (!isRich) {
            // Legacy View
            return (
                <div className="legacy-view">
                    <div className="alert-banner">⚠️ Legacy Report Format</div>
                    <div className="report-section">
                        <h3>Synthesis</h3>
                        <MarkdownRenderer content={selectedReport.synthesis} />
                    </div>
                    {selectedReport.way_forward && Object.keys(selectedReport.way_forward).length > 0 && (
                        <div className="report-section">
                            <h3>Way Forward</h3>
                            <pre>{JSON.stringify(selectedReport.way_forward, null, 2)}</pre>
                        </div>
                    )}
                </div>
            );
        }

        // Rich View
        return (
            <div className="rich-view">
                <div className="tabs-nav">
                    <button
                        className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
                        onClick={() => setActiveTab('overview')}
                    >
                        👁️ Overview
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'analysis' ? 'active' : ''}`}
                        onClick={() => setActiveTab('analysis')}
                    >
                        🧠 Analysis
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'evidence' ? 'active' : ''}`}
                        onClick={() => setActiveTab('evidence')}
                    >
                        📜 Evidence
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'strategy' ? 'active' : ''}`}
                        onClick={() => setActiveTab('strategy')}
                    >
                        ⚔️ Strategy
                    </button>
                </div>

                <div className="tab-content custom-scrollbar">
                    <AnimatePresence mode="wait">
                        {activeTab === 'overview' && (
                            <motion.div
                                key="overview"
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 10 }}
                                transition={{ duration: 0.2 }}
                            >
                                <div className="report-section">
                                    <h3>Synthesis</h3>
                                    <MarkdownRenderer content={selectedReport.synthesis} />
                                </div>
                                {data.predicted_question && (
                                    <div className="report-section highlight-box">
                                        <h3>🔮 Predicted Question</h3>
                                        <p>{data.predicted_question}</p>
                                    </div>
                                )}
                                {data.gs_linkages && (
                                    <div className="report-section">
                                        <h3>🔗 GS Linkages</h3>
                                        <div className="grid-2">
                                            {Object.entries(data.gs_linkages).map(([k, v]: any) => (
                                                <div key={k} className="stat-card">
                                                    <strong>{k.toUpperCase()}</strong>
                                                    <p>{v}</p>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </motion.div>
                        )}

                        {activeTab === 'analysis' && (
                            <motion.div
                                key="analysis"
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 10 }}
                                transition={{ duration: 0.2 }}
                            >
                                {data.critical_axis && (
                                    <div className="report-section">
                                        <h3>⚖️ Critical Axis</h3>
                                        <div className="comparison-grid">
                                            <div className="pros-col">
                                                <h4>Arguments For</h4>
                                                <ul>
                                                    {data.critical_axis.arguments_for?.map((arg: string, i: number) => (
                                                        <li key={i}>{arg}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                            <div className="cons-col">
                                                <h4>Arguments Against</h4>
                                                <ul>
                                                    {data.critical_axis.arguments_against?.map((arg: string, i: number) => (
                                                        <li key={i}>{arg}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                )}
                                {data.pestle && (
                                    <div className="report-section">
                                        <h3>🌍 PESTLE Analysis</h3>
                                        <div className="pestle-grid">
                                            {Object.entries(data.pestle).map(([k, v]: any) => (
                                                <div key={k} className="pestle-card">
                                                    <div className="pestle-icon">{k[0].toUpperCase()}</div>
                                                    <div className="pestle-content">
                                                        <strong>{k.charAt(0).toUpperCase() + k.slice(1)}</strong>
                                                        <p>{v}</p>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </motion.div>
                        )}

                        {activeTab === 'evidence' && (
                            <motion.div
                                key="evidence"
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 10 }}
                                transition={{ duration: 0.2 }}
                            >
                                {data.scholars && data.scholars.length > 0 && (
                                    <div className="report-section">
                                        <h3>🎓 Scholars & Quotes</h3>
                                        {data.scholars.map((s: any, i: number) => (
                                            <div key={i} className="quote-card">
                                                <blockquote>"{s.quote}"</blockquote>
                                                <cite>- {s.name} ({s.context})</cite>
                                            </div>
                                        ))}
                                    </div>
                                )}
                                {data.data_bank && data.data_bank.length > 0 && (
                                    <div className="report-section">
                                        <h3>📊 Data Bank</h3>
                                        <table className="data-table">
                                            <thead>
                                                <tr>
                                                    <th>Statistic</th>
                                                    <th>Source</th>
                                                    <th>Relevance</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {data.data_bank.map((d: any, i: number) => (
                                                    <tr key={i}>
                                                        <td>{d.statistic}</td>
                                                        <td>{d.source}</td>
                                                        <td>{d.relevance}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                                {data.precedents && data.precedents.length > 0 && (
                                    <div className="report-section">
                                        <h3>🏛️ Precedents</h3>
                                        <ul>
                                            {data.precedents.map((p: any, i: number) => (
                                                <li key={i}><strong>{p.name}</strong> ({p.type}): {p.summary}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </motion.div>
                        )}

                        {activeTab === 'strategy' && (
                            <motion.div
                                key="strategy"
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 10 }}
                                transition={{ duration: 0.2 }}
                            >
                                {data.way_forward && (
                                    <div className="report-section">
                                        <h3>🚀 Way Forward</h3>
                                        <div className="strategy-timeline">
                                            <div className="strategy-step">
                                                <span className="step-label">Immediate</span>
                                                <p>{data.way_forward.immediate}</p>
                                            </div>
                                            <div className="strategy-step">
                                                <span className="step-label">Medium Term</span>
                                                <p>{data.way_forward.medium_term}</p>
                                            </div>
                                            <div className="strategy-step">
                                                <span className="step-label">Long Term</span>
                                                <p>{data.way_forward.long_term}</p>
                                            </div>
                                        </div>
                                    </div>
                                )}
                                {data.mind_map_code && (
                                    <div className="report-section">
                                        <h3>🗺️ Mind Map</h3>
                                        <MermaidDiagram code={data.mind_map_code} />
                                    </div>
                                )}
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        );
    };

    return (
        <div className="triangulation-history-container">
            <h1 className="neon-text">⚔️ War Room Archives</h1>

            <div className="triangulation-layout">
                <div className="history-list glass-panel">
                    <div className="list-header">
                        <h3>Strategic Reports</h3>
                        <input
                            type="text"
                            placeholder="Search reports..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="search-input"
                        />
                    </div>

                    {loading ? (
                        <div className="loading-text">Loading intelligence...</div>
                    ) : (
                        <ul className="custom-scrollbar">
                            {filteredHistory.map(item => (
                                <li
                                    key={item.id}
                                    className={`history-item ${selectedReport?.id === item.id ? 'active' : ''}`}
                                    onClick={() => setSelectedReport(item)}
                                >
                                    <div className="item-topic">{item.topic}</div>
                                    <div className="item-date">{new Date(item.created_at).toLocaleDateString()}</div>
                                </li>
                            ))}
                            {filteredHistory.length === 0 && <div className="no-results">No reports found.</div>}
                        </ul>
                    )}
                </div>

                <div className="report-view glass-panel">
                    {selectedReport ? (
                        isDecrypting ? (
                            <div className="decrypting-overlay">
                                <div className="spinner-core"></div>
                                <h2 className="glitch" data-text="DECRYPTING DOSSIER...">DECRYPTING DOSSIER...</h2>
                                <div className="scan-line"></div>
                            </div>
                        ) : (
                            <>
                                <div className="report-header">
                                    <div className="header-title-block">
                                        <h2>{selectedReport.topic}</h2>
                                        <span className="report-date">CLASSIFIED: {new Date(selectedReport.created_at).toLocaleString()}</span>
                                    </div>
                                    {selectedReport.full_report?.way_forward && (
                                        <button
                                            className="actionable-btn"
                                            onClick={handleExtractActionables}
                                            disabled={extracting}
                                        >
                                            {extracting ? 'INJECTING...' : '⚡ EXTRACT ACTIONABLES'}
                                        </button>
                                    )}
                                </div>
                                {renderContent()}
                            </>
                        )
                    ) : (
                        <div className="empty-state">
                            <div className="icon">📂</div>
                            <p>Awaiting dossier selection.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default TriangulationHistory;
