import React, { useState, useEffect } from 'react';
import './TriangulationHistory.css';
import MarkdownRenderer from '../Shared/MarkdownRenderer';

interface TriangulationReport {
    id: number;
    topic: string;
    synthesis: string;
    way_forward: any;
    created_at: string;
}

const TriangulationHistory: React.FC = () => {
    const [history, setHistory] = useState<TriangulationReport[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedReport, setSelectedReport] = useState<TriangulationReport | null>(null);

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/triangulation/history');
            const data = await response.json();
            if (data.success) {
                setHistory(data.data);
            }
        } catch (error) {
            console.error("Failed to fetch Triangulation history", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="triangulation-history-container">
            <h1 className="neon-text">⚔️ War Room Archives</h1>

            <div className="triangulation-layout">
                <div className="history-list glass-panel">
                    <h3>Strategic Reports</h3>
                    {loading ? (
                        <div>Loading intelligence...</div>
                    ) : (
                        <ul>
                            {history.map(item => (
                                <li
                                    key={item.id}
                                    className={`history-item ${selectedReport?.id === item.id ? 'active' : ''}`}
                                    onClick={() => setSelectedReport(item)}
                                >
                                    <div className="item-topic">{item.topic}</div>
                                    <div className="item-date">{new Date(item.created_at).toLocaleDateString()}</div>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>

                <div className="report-view glass-panel">
                    {selectedReport ? (
                        <>
                            <h2>{selectedReport.topic}</h2>
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
                        </>
                    ) : (
                        <div className="placeholder-text">
                            Select a strategic report to review.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default TriangulationHistory;
