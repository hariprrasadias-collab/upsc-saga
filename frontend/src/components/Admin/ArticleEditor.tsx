import { API_BASE_URL } from '../../config';

import React, { useState } from 'react';
import './ArticleEditor.css';
import { useToast } from '../Toast';

interface ArticleEditorProps {
    onClose: () => void;
    onSave: () => void;
}

const ArticleEditor: React.FC<ArticleEditorProps> = ({ onClose, onSave }) => {
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [tags, setTags] = useState('');
    const [category, setCategory] = useState('General');
    const [saving, setSaving] = useState(false);
    const { addToast } = useToast();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);

        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/articles`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title,
                    content,
                    tags,
                    category,
                    source: 'Admin Panel'
                })
            });

            if (res.ok) {
                addToast('Article created successfully', 'success');
                onSave();
                onClose();
            } else {
                addToast('Failed to create article', 'error');
            }
        } catch (error) {
            addToast('Error creating article', 'error');
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content animate-scale-in">
                <div className="modal-header">
                    <h2>New Article</h2>
                    <button className="close-btn" onClick={onClose} aria-label="Close"><span aria-hidden="true">×</span></button>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Title</label>
                        <input
                            type="text"
                            value={title}
                            onChange={e => setTitle(e.target.value)}
                            required
                            placeholder="Article Title"
                        />
                    </div>

                    <div className="form-group">
                        <label>Category</label>
                        <select value={category} onChange={e => setCategory(e.target.value)}>
                            <option value="General">General</option>
                            <option value="History">History</option>
                            <option value="Geography">Geography</option>
                            <option value="Polity">Polity</option>
                            <option value="Economics">Economics</option>
                            <option value="Science">Science</option>
                            <option value="Current Affairs">Current Affairs</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Tags (comma separated)</label>
                        <input
                            type="text"
                            value={tags}
                            onChange={e => setTags(e.target.value)}
                            placeholder="e.g. ancient, art, culture"
                        />
                    </div>

                    <div className="form-group">
                        <label>Content</label>
                        <textarea
                            value={content}
                            onChange={e => setContent(e.target.value)}
                            required
                            rows={15}
                            placeholder="Write your article content here (Markdown supported)..."
                        />
                    </div>

                    <div className="modal-actions">
                        <button type="button" className="cancel-btn" onClick={onClose}>Cancel</button>
                        <button type="submit" className="save-btn" disabled={saving}>
                            {saving ? 'Saving...' : 'Publish Article'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ArticleEditor;
