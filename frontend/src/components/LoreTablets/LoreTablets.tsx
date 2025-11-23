// /frontend/src/components/LoreTablets/LoreTablets.tsx
import React, { useState, useEffect, useCallback } from 'react';
import './LoreTablets.css';

interface Note {
    id: number;
    title: string;
    content: string;
    created_at: string;
}

const LoreTablets: React.FC = () => {
    const [notes, setNotes] = useState<Note[]>([]);
    const [selectedNote, setSelectedNote] = useState<Note | null>(null);
    const [isEditing, setIsEditing] = useState(false);
    const [loading, setLoading] = useState(true);

    // Editor State
    const [editTitle, setEditTitle] = useState('');
    const [editContent, setEditContent] = useState('');

    const fetchNotes = useCallback(async () => {
        try {
            const res = await fetch('http://localhost:5000/api/lore');
            if (res.ok) {
                const data = await res.json();
                setNotes(data);
            }
        } catch (err) {
            console.error("Failed to fetch lore", err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchNotes();
    }, [fetchNotes]);

    // Open Editor (New or Existing)
    const handleOpenEditor = (note?: Note) => {
        if (note) {
            setSelectedNote(note);
            setEditTitle(note.title);
            setEditContent(note.content);
        } else {
            setSelectedNote(null); // New Note
            setEditTitle('');
            setEditContent('');
        }
        setIsEditing(true);
    };

    // Save Note (Create or Update)
    const handleSave = async () => {
        const endpoint = selectedNote 
            ? `http://localhost:5000/api/lore/${selectedNote.id}`
            : `http://localhost:5000/api/lore`;
        
        const method = selectedNote ? 'PUT' : 'POST';

        try {
            const res = await fetch(endpoint, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: editTitle || 'Untitled Tablet',
                    content: editContent
                })
            });

            if (res.ok) {
                await fetchNotes();
                setIsEditing(false);
            }
        } catch (err) {
            console.error("Error saving tablet", err);
        }
    };

    // Delete Note
    const handleDelete = async () => {
        if (!selectedNote) return;
        if (!confirm("Are you sure you want to destroy this tablet?")) return;

        try {
            const res = await fetch(`http://localhost:5000/api/lore/${selectedNote.id}`, {
                method: 'DELETE'
            });
            if (res.ok) {
                await fetchNotes();
                setIsEditing(false);
            }
        } catch (err) {
            console.error("Error destroying tablet", err);
        }
    };

    return (
        <div className="lore-container">
            <h1 className="lore-header">LORE TABLETS</h1>

            {loading ? (
                <div style={{color:'white', textAlign:'center'}}>Deciphering runes...</div>
            ) : (
                <div className="tablets-grid">
                    {/* Add New Button */}
                    <div className="add-tablet-btn" onClick={() => handleOpenEditor()}>
                        <span className="plus-icon">+</span>
                        <span style={{color: '#888'}}>Carve New Tablet</span>
                    </div>

                    {/* Existing Notes */}
                    {notes.map(note => (
                        <div key={note.id} className="tablet-card" onClick={() => handleOpenEditor(note)}>
                            <h3 className="tablet-title">{note.title}</h3>
                            <p className="tablet-preview">{note.content || "(Empty Inscription)"}</p>
                        </div>
                    ))}
                </div>
            )}

            {/* EDITOR OVERLAY */}
            {isEditing && (
                <div className="editor-overlay" onClick={() => setIsEditing(false)}>
                    <div className="editor-stone" onClick={e => e.stopPropagation()}>
                        <div className="editor-header">
                            <input 
                                type="text" 
                                className="title-input" 
                                placeholder="Tablet Title..." 
                                value={editTitle}
                                onChange={e => setEditTitle(e.target.value)}
                            />
                            <button className="close-btn" onClick={() => setIsEditing(false)}>✕</button>
                        </div>
                        
                        <textarea 
                            className="content-textarea" 
                            placeholder="Inscribe your knowledge here..."
                            value={editContent}
                            onChange={e => setEditContent(e.target.value)}
                        />

                        <div className="editor-footer">
                            {selectedNote ? (
                                <button className="delete-btn" onClick={handleDelete}>Destroy Tablet</button>
                            ) : (
                                <div></div> // Spacer
                            )}
                            <button className="save-btn" onClick={handleSave}>Carve (Save)</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default LoreTablets;