import React, { useState } from 'react';
import D3Tree from './D3Tree';
import './MindMapCreator.css';

const MindMapCreator: React.FC = () => {
    const [topic, setTopic] = useState('');
    const [mindMapData, setMindMapData] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [savedMaps, setSavedMaps] = useState<any[]>([]);
    const [showSaved, setShowSaved] = useState(false);

    React.useEffect(() => {
        fetchSavedMaps();
    }, []);

    const fetchSavedMaps = async () => {
        try {
            const res = await fetch('http://localhost:5000/api/mindmap/list');
            if (res.ok) {
                const data = await res.json();
                setSavedMaps(data);
            }
        } catch (err) {
            console.error("Failed to fetch saved maps", err);
        }
    };

    const handleGenerate = async () => {
        if (!topic.trim()) return;

        setLoading(true);
        setError(null);
        setMindMapData(null);

        try {
            const res = await fetch('http://localhost:5000/api/mindmap/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic })
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.error || 'Failed to generate mind map');
            }

            const data = await res.json();
            setMindMapData(data);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        if (!mindMapData) return;

        try {
            const res = await fetch('http://localhost:5000/api/mindmap/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: topic,
                    root_node: mindMapData
                })
            });

            if (res.ok) {
                alert('Mind map saved successfully!');
                fetchSavedMaps(); // Refresh list
            } else {
                throw new Error('Failed to save mind map');
            }
        } catch (err: any) {
            alert(err.message);
        }
    };

    const loadMap = async (id: number) => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`http://localhost:5000/api/mindmap/${id}`);
            if (res.ok) {
                const data = await res.json();
                setTopic(data.title);
                setMindMapData(data.root_node);
                setShowSaved(false);
            } else {
                throw new Error('Failed to load map');
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="mindmap-container">
            <div className="mindmap-header">
                <h1>🧠 Mind Map Creator</h1>
                <p>Visualize complex topics with AI-generated mind maps.</p>
                <button
                    className="toggle-saved-btn"
                    onClick={() => setShowSaved(!showSaved)}
                >
                    {showSaved ? 'Hide Saved Maps' : '📂 Open Saved Maps'}
                </button>
            </div>

            <div className="mindmap-content-wrapper">
                {showSaved && (
                    <div className="saved-maps-sidebar">
                        <h3>Saved Maps</h3>
                        {savedMaps.length === 0 ? (
                            <p className="no-maps">No saved maps yet.</p>
                        ) : (
                            <ul className="saved-maps-list">
                                {savedMaps.map(map => (
                                    <li key={map.id} onClick={() => loadMap(map.id)}>
                                        <span className="map-title">{map.title}</span>
                                        <span className="map-date">{new Date(map.created_at).toLocaleDateString()}</span>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                )}

                <div className="mindmap-main">
                    <div className="mindmap-controls">
                        <input
                            type="text"
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            placeholder="Enter a topic (e.g., Indus Valley Civilization)"
                            className="topic-input"
                            onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
                        />
                        <button
                            className="generate-btn"
                            onClick={handleGenerate}
                            disabled={loading || !topic.trim()}
                        >
                            {loading ? 'Generating...' : 'Generate Mind Map'}
                        </button>
                    </div>

                    {error && <div className="error-message">{error}</div>}

                    <div className="mindmap-canvas">
                        {mindMapData ? (
                            <>
                                <div className="canvas-actions">
                                    <button className="save-btn" onClick={handleSave}>💾 Save Map</button>
                                </div>
                                <D3Tree data={mindMapData} />
                            </>
                        ) : (
                            !loading && (
                                <div className="empty-state">
                                    <p>Enter a topic above to generate a mind map.</p>
                                </div>
                            )
                        )}
                        {loading && (
                            <div className="loading-state">
                                <div className="spinner"></div>
                                <p>Consulting the archives...</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MindMapCreator;
