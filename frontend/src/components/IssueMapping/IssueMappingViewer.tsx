import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';
import './IssueMappingViewer.css';
import VisualLinker from './VisualLinker';

interface Mapping {
    id: number;
    subject: string;
    syllabus_topic: string;
    paper: string;
    relevance_score: number;
    key_linkages: string;
    exam_utility: string;
}

interface Props {
    articleId: number;
    articleTitle?: string;
}

const IssueMappingViewer: React.FC<Props> = ({ articleId, articleTitle }) => {
    const [mappings, setMappings] = useState<Mapping[]>([]);
    const [tags, setTags] = useState<string[]>([]);
    const [newTag, setNewTag] = useState('');
    const [loading, setLoading] = useState(false);
    const [analyzing, setAnalyzing] = useState(false);

    useEffect(() => {
        fetchMappings();
    }, [articleId]);

    const fetchMappings = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/issue-mapping/article/${articleId}`);
            const data = await response.json();

            if (data.success) {
                setMappings(data.mappings);
                setTags(data.tags || []);
            }
        } catch (error) {
            console.error('Error fetching mappings:', error);
        } finally {
            setLoading(false);
        }
    };

    const analyzeArticle = async () => {
        setAnalyzing(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/issue-mapping/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ article_id: articleId })
            });

            const data = await response.json();

            if (data.success) {
                setMappings(data.mappings);
            }
        } catch (error) {
            console.error('Error analyzing article:', error);
        } finally {
            setAnalyzing(false);
        }
    };

    const handleAddTag = async () => {
        if (!newTag.trim()) return;
        const updatedTags = [...tags, newTag.trim()];

        try {
            const res = await fetch(`${API_BASE_URL}/api/issue-mapping/tags`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ article_id: articleId, tags: updatedTags })
            });
            if (res.ok) {
                setTags(updatedTags);
                setNewTag('');
            }
        } catch (err) {
            console.error("Failed to add tag", err);
        }
    };

    const handleRemoveTag = async (tagToRemove: string) => {
        const updatedTags = tags.filter(t => t !== tagToRemove);
        try {
            const res = await fetch(`${API_BASE_URL}/api/issue-mapping/tags`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ article_id: articleId, tags: updatedTags })
            });
            if (res.ok) {
                setTags(updatedTags);
            }
        } catch (err) {
            console.error("Failed to remove tag", err);
        }
    };

    const getScoreColor = (score: number): string => {
        if (score >= 0.8) return '#10b981';
        if (score >= 0.6) return '#f59e0b';
        return '#6366f1';
    };

    const getPaperColor = (paper: string): string => {
        const colors: Record<string, string> = {
            'GS1': '#ec4899',
            'GS2': '#8b5cf6',
            'GS3': '#3b82f6',
            'GS4': '#10b981'
        };
        return colors[paper] || '#6b7280';
    };

    return (
        <div className="issue-mapping-viewer">
            <div className="mapping-header">
                <h3>📍 Syllabus Mapping</h3>
                {mappings.length === 0 && !loading && (
                    <button onClick={analyzeArticle} disabled={analyzing} className="analyze-btn">
                        {analyzing ? '🔄 Analyzing...' : '🤖 Map to Syllabus (AI)'}
                    </button>
                )}
                {mappings.length > 0 && (
                    <button onClick={analyzeArticle} disabled={analyzing} className="re-analyze-btn">
                        {analyzing ? '🔄 Re-analyzing...' : '🔄 Re-analyze'}
                    </button>
                )}
            </div>

            {/* TAGS SECTION */}
            <div className="tags-section">
                <div className="tags-list">
                    {tags.map(tag => (
                        <span key={tag} className="tag-chip">
                            #{tag}
                            <button onClick={() => handleRemoveTag(tag)} className="remove-tag-btn" aria-label={`Remove tag ${tag}`}>
                                <span aria-hidden="true">×</span>
                            </button>
                        </span>
                    ))}
                </div>
                <div className="add-tag-form">
                    <input
                        type="text"
                        value={newTag}
                        onChange={(e) => setNewTag(e.target.value)}
                        placeholder="Add tag..."
                        aria-label="New tag name"
                        onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                    />
                    <button onClick={handleAddTag} aria-label="Add tag">
                        <span aria-hidden="true">+</span>
                    </button>
                </div>
            </div>

            {loading ? (
                <div className="loading-state">Loading mappings...</div>
            ) : mappings.length > 0 ? (
                <>
                    <VisualLinker articleTitle={articleTitle || 'Article'} mappings={mappings} />

                    <div className="mappings-grid">
                        {mappings.map((mapping) => (
                            <div key={mapping.id} className="mapping-card">
                                <div className="mapping-card-header">
                                    <div className="subject-badge" style={{ backgroundColor: getPaperColor(mapping.paper) }}>
                                        {mapping.subject}
                                    </div>
                                    <div className="relevance-score" style={{ color: getScoreColor(mapping.relevance_score) }}>
                                        {Math.round(mapping.relevance_score * 100)}%
                                    </div>
                                </div>

                                <div className="topic-section">
                                    <div className="paper-tag">{mapping.paper}</div>
                                    <h4>{mapping.syllabus_topic}</h4>
                                </div>

                                <div className="linkages-section">
                                    <label>🔗 Key Linkages:</label>
                                    <p>{mapping.key_linkages}</p>
                                </div>

                                <div className="utility-section">
                                    <label>📝 Exam Utility:</label>
                                    <p>{mapping.exam_utility}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </>
            ) : (
                <div className="empty-state">
                    <p>No syllabus mappings yet. Click "Map to Syllabus" to analyze this article with AI.</p>
                </div>
            )}
        </div>
    );
};

export default IssueMappingViewer;
