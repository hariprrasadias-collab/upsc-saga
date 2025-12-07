import React, { useState, useEffect } from 'react';
import './BrainVault.css';
import MarkdownRenderer from '../Shared/MarkdownRenderer';
import TimelineRenderer from './Renderers/TimelineRenderer';
import PodcastPlayer from './Renderers/PodcastPlayer';
import ChatInterface from './Renderers/ChatInterface';
import VisualPromptRenderer from './Renderers/VisualPromptRenderer';
import EssayRenderer from './Renderers/EssayRenderer';
import MapRenderer from './Renderers/MapRenderer';

interface AIContent {
    id: number;
    content_type: string;
    topic: string;
    content: string;
    metadata: any;
    created_at: string;
}

const BrainVault: React.FC = () => {
    // ... (state lines 15-26 remain same)
    const [contentList, setContentList] = useState<AIContent[]>([]);
    const [loading, setLoading] = useState(true);
    const [filterType, setFilterType] = useState<string>('all');
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedContent, setSelectedContent] = useState<AIContent | null>(null);

    const contentTypes = [
        'all', 'podcast', 'essay', 'visual_prompt', 'roleplay',
        'cheat_sheet', 'timeline', 'eli5', 'pitfalls', 'quote_bank', 'map_work'
    ];

    useEffect(() => {
        fetchContent();
    }, [filterType]);
    // ... (fetchContent and handleDelete remain same)
    const fetchContent = async () => {
        setLoading(true);
        try {
            let url = 'http://localhost:5000/api/automation/content';
            if (filterType !== 'all') {
                url += `?type=${filterType}`;
            }
            const response = await fetch(url);
            const data = await response.json();
            if (data.success) {
                setContentList(data.data);
            }
        } catch (error) {
            console.error("Failed to fetch Brain Vault content", error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id: number, e: React.MouseEvent) => {
        e.stopPropagation();
        if (!window.confirm("Delete this artifact from the Neural Storage?")) return;

        try {
            await fetch(`http://localhost:5000/api/automation/content/${id}`, { method: 'DELETE' });
            setContentList(prev => prev.filter(item => item.id !== id));
            if (selectedContent?.id === id) setSelectedContent(null);
        } catch (error) {
            console.error("Deletion failed", error);
        }
    };

    const filteredList = contentList.filter(item =>
        item.topic.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const renderContentBody = (item: AIContent) => {
        const normalizedType = String(item.content_type || '').trim().toLowerCase();

        let metadataObj = item.metadata;
        // Ensure metadata is an object
        if (typeof metadataObj === 'string') {
            try {
                metadataObj = JSON.parse(metadataObj);
            } catch (e) {
                console.error("Failed to parse metadata in BrainVault", e);
                metadataObj = {};
            }
        }

        // Priority Override: If it looks like a map, treat it as a map!
        if (metadataObj?.locations && Array.isArray(metadataObj.locations)) {
            return <MapRenderer content={item.content} metadata={metadataObj} />;
        }

        switch (normalizedType) {
            case 'timeline':
                return <TimelineRenderer content={item.content} metadata={metadataObj} />;
            case 'podcast':
                return <PodcastPlayer content={item.content} title={item.topic} />;
            case 'roleplay':
            case 'socratic':
                return <ChatInterface content={item.content} />;
            case 'visual_prompt':
                return <VisualPromptRenderer content={item.content} />;
            case 'essay':
                return <EssayRenderer content={item.content} />;
            case 'map_work':
            case 'mapwork': // just in case
                return <MapRenderer content={item.content} metadata={item.metadata} />;
            default:
                return (
                    <div>
                        <div style={{ color: 'orange', fontSize: '0.8rem', padding: '5px', border: '1px dashed orange', marginBottom: '10px' }}>
                            Debug: Type="{item.content_type}" (Normalized="{normalizedType}") - Falling back to Markdown
                        </div>
                        <MarkdownRenderer content={item.content} />
                    </div>
                );
        }
    };

    return (
        <div className="brain-vault-container">
            <header className="vault-header">
                <h1 className="neon-text">🧠 The Brain Vault</h1>
                <div className="search-bar">
                    <span className="search-icon">🔍</span>
                    <input
                        type="text"
                        placeholder="Search Neural Storage..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </header>

            <nav className="vault-filters">
                {contentTypes.map(type => (
                    <button
                        key={type}
                        className={`filter-btn ${filterType === type ? 'active' : ''}`}
                        onClick={() => setFilterType(type)}
                    >
                        {type.toUpperCase().replace('_', ' ')}
                    </button>
                ))}
            </nav>

            <div className="vault-layout">
                <aside className="content-list-panel glass-panel">
                    {loading ? (
                        <div className="loading-state">Accessing Neural Storage...</div>
                    ) : (
                        <ul className="content-list-ul">
                            {filteredList.map(item => (
                                <li
                                    key={item.id}
                                    className={`vault-item ${selectedContent?.id === item.id ? 'active' : ''}`}
                                    onClick={() => setSelectedContent(item)}
                                >
                                    <div className="item-header">
                                        <span className="item-type-tag">{item.content_type}</span>
                                        <button
                                            className="delete-btn"
                                            onClick={(e) => handleDelete(item.id, e)}
                                            title="Delete Artifact"
                                        >
                                            ×
                                        </button>
                                    </div>
                                    <h4 className="item-topic">{item.topic}</h4>
                                    <span className="item-date">{new Date(item.created_at).toLocaleDateString()}</span>
                                </li>
                            ))}
                            {filteredList.length === 0 && !loading && (
                                <div className="empty-state">No artifacts found.</div>
                            )}
                        </ul>
                    )}
                </aside>

                <main className="content-view-panel glass-panel">
                    {selectedContent ? (
                        <div className="content-view-inner">
                            <div className="view-header">
                                <div>
                                    <h2 className="glow-text">{selectedContent.topic}</h2>
                                    <span className="type-badge large">{selectedContent.content_type}</span>
                                </div>
                                <div className="action-buttons">
                                    <button
                                        className="action-btn"
                                        onClick={() => navigator.clipboard.writeText(selectedContent.content)}
                                    >
                                        📋 Copy
                                    </button>
                                </div>
                            </div>

                            <div className="view-body custom-scrollbar">
                                {renderContentBody(selectedContent)}
                            </div>

                            {selectedContent.metadata && Object.keys(selectedContent.metadata).length > 0 && (
                                <div className="metadata-box">
                                    <h4>Artifact Metadata</h4>
                                    <pre>{JSON.stringify(selectedContent.metadata, null, 2)}</pre>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="placeholder-state">
                            <div className="placeholder-icon">📂</div>
                            <h3>Select an Artifact</h3>
                            <p>Choose an item from the left to view its neural contents.</p>
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
};

export default BrainVault;
