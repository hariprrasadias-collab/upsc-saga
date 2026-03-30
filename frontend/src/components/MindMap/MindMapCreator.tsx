import { API_BASE_URL } from '../../config';

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
    const [contextMenu, setContextMenu] = useState<{ x: number, y: number, node: any } | null>(null);
    const [divingId, setDivingId] = useState<string | null>(null);

    // Close context menu on external clicks
    React.useEffect(() => {
        const handleClick = () => setContextMenu(null);
        window.addEventListener('click', handleClick);
        return () => window.removeEventListener('click', handleClick);
    }, []);

    React.useEffect(() => {
        fetchSavedMaps();
    }, []);

    const fetchSavedMaps = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/mindmap/list`);
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
            const res = await fetch(`${API_BASE_URL}/api/mindmap/generate`, {
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
            const res = await fetch(`${API_BASE_URL}/api/mindmap/save`, {
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
            const res = await fetch(`${API_BASE_URL}/api/mindmap/${id}`);
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

    const deleteMap = async (id: number, event: React.MouseEvent) => {
        event.stopPropagation(); // Prevent loadMap from firing
        if (!confirm('Are you sure you want to delete this mind map?')) return;

        try {
            const res = await fetch(`${API_BASE_URL}/api/mindmap/${id}`, {
                method: 'DELETE'
            });

            if (res.ok) {
                alert('Mind map deleted successfully!');
                fetchSavedMaps(); // Refresh list
            } else {
                throw new Error('Failed to delete mind map');
            }
        } catch (err: any) {
            alert(err.message);
        }
    };

    const handleNodeRightClick = (nodeData: any, x: number, y: number) => {
        setContextMenu({ x, y, node: nodeData });
    };

    const handleDeepDive = async () => {
        if (!contextMenu || !mindMapData) return;

        const targetNode = contextMenu.node;
        setContextMenu(null);
        setDivingId(targetNode.name);

        try {
            const res = await fetch(`${API_BASE_URL}/api/mindmap/deepdive`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic, node_name: targetNode.name })
            });

            if (!res.ok) throw new Error("Failed to deep dive");

            const data = await res.json();
            if (data.success && data.children) {
                // We need to find the node within our mindMapData tree and attach children
                const newData = JSON.parse(JSON.stringify(mindMapData)); // Deep clone

                const appendChildren = (currentNode: any, targetName: string, newChildren: any[]) => {
                    if (currentNode.name === targetName) {
                        currentNode.children = currentNode.children || [];
                        currentNode.children = [...currentNode.children, ...newChildren];
                        return true;
                    }
                    if (currentNode.children) {
                        for (const child of currentNode.children) {
                            if (appendChildren(child, targetName, newChildren)) return true;
                        }
                    }
                    return false;
                };

                appendChildren(newData, targetNode.name, data.children);
                setMindMapData(newData);
            }
        } catch (err: any) {
            alert(err.message);
        } finally {
            setDivingId(null);
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
                                        <div className="map-info">
                                            <span className="map-title">{map.title}</span>
                                            <span className="map-date">{new Date(map.created_at).toLocaleDateString()}</span>
                                        </div>
                                        <button
                                            className="delete-map-btn"
                                            onClick={(e) => deleteMap(map.id, e)}
                                            title="Delete this map"
                                        >
                                            🗑️
                                        </button>
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
                                <D3Tree data={mindMapData} onNodeRightClick={handleNodeRightClick} />
                                {divingId && (
                                    <div className="diving-indicator">
                                        ⚡ Neural Link Extrapolating "{divingId}"...
                                    </div>
                                )}
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

            {contextMenu && (
                <div
                    className="cyber-context-menu"
                    style={{ left: contextMenu.x, top: contextMenu.y }}
                    onClick={(e) => e.stopPropagation()}
                >
                    <div className="menu-header">Node: {contextMenu.node.name.length > 20 ? contextMenu.node.name.substring(0, 20) + '...' : contextMenu.node.name}</div>
                    <button className="menu-btn" onClick={handleDeepDive}>
                        ⚡ AI Deep Dive Expansion
                    </button>
                </div>
            )}
        </div>
    );
};

export default MindMapCreator;
