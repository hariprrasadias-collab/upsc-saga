import React, { useState, useEffect, useRef } from 'react';
import './MindPalace.css';
import { FaPlus, FaMapMarkerAlt, FaBoxOpen, FaArrowLeft } from 'react-icons/fa';

interface Location {
    id: number;
    name: string;
    description: string;
    image_url?: string;
    layout_type: string;
}

interface Artifact {
    id: number;
    location_id: number;
    title: string;
    content: string;
    type: string;
    x_position: number;
    y_position: number;
    icon: string;
    color: string;
}

const MindPalace: React.FC = () => {
    const [view, setView] = useState<'map' | 'room'>('map');
    const [locations, setLocations] = useState<Location[]>([]);
    const [currentLocation, setCurrentLocation] = useState<Location | null>(null);
    const [artifacts, setArtifacts] = useState<Artifact[]>([]);

    // Modal State
    const [showLocationModal, setShowLocationModal] = useState(false);
    const [showArtifactModal, setShowArtifactModal] = useState(false);
    const [editingArtifact, setEditingArtifact] = useState<Artifact | null>(null);

    // Form State
    const [newName, setNewName] = useState('');
    const [newDesc, setNewDesc] = useState('');
    const [newContent, setNewContent] = useState('');

    useEffect(() => {
        fetchLocations();
    }, []);

    useEffect(() => {
        if (currentLocation) {
            fetchArtifacts(currentLocation.id);
        }
    }, [currentLocation]);

    const fetchLocations = async () => {
        try {
            const res = await fetch('http://localhost:5000/api/mind_palace/locations');
            const data = await res.json();
            setLocations(data);
        } catch (err) {
            console.error(err);
        }
    };

    const fetchArtifacts = async (locationId: number) => {
        try {
            const res = await fetch(`http://localhost:5000/api/mind_palace/locations/${locationId}/artifacts`);
            const data = await res.json();
            setArtifacts(data);
        } catch (err) {
            console.error(err);
        }
    };

    const handleCreateLocation = async () => {
        try {
            const res = await fetch('http://localhost:5000/api/mind_palace/locations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: newName, description: newDesc })
            });
            if (res.ok) {
                fetchLocations();
                setShowLocationModal(false);
                setNewName('');
                setNewDesc('');
            }
        } catch (err) {
            console.error(err);
        }
    };

    const handleCreateArtifact = async (e: React.MouseEvent) => {
        // Create artifact at click position if in room view
        if (!currentLocation) return;

        // Default position center if not clicked on canvas
        const x = 50;
        const y = 50;

        try {
            const res = await fetch('http://localhost:5000/api/mind_palace/artifacts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    location_id: currentLocation.id,
                    title: newName,
                    content: newContent,
                    x_position: x,
                    y_position: y,
                    icon: '📝',
                    color: '#3498db'
                })
            });
            if (res.ok) {
                fetchArtifacts(currentLocation.id);
                setShowArtifactModal(false);
                setNewName('');
                setNewContent('');
            }
        } catch (err) {
            console.error(err);
        }
    };

    const handleUpdateArtifactPosition = async (id: number, x: number, y: number) => {
        try {
            await fetch(`http://localhost:5000/api/mind_palace/artifacts/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ x_position: x, y_position: y })
            });
            // Optimistic update
            setArtifacts(prev => prev.map(a => a.id === id ? { ...a, x_position: x, y_position: y } : a));
        } catch (err) {
            console.error(err);
        }
    };

    // Drag and Drop Logic
    const handleDragEnd = (e: React.DragEvent, artifactId: number) => {
        const canvas = document.querySelector('.palace-canvas');
        if (!canvas) return;

        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Convert to percentage
        const xPercent = (x / rect.width) * 100;
        const yPercent = (y / rect.height) * 100;

        handleUpdateArtifactPosition(artifactId, xPercent, yPercent);
    };

    return (
        <div className="mind-palace-container">
            <div className="palace-header">
                <h1>
                    {view === 'room' && (
                        <button className="palace-btn" onClick={() => setView('map')} style={{ marginRight: '1rem' }}>
                            <FaArrowLeft />
                        </button>
                    )}
                    🏰 The Mind Palace {view === 'room' && `> ${currentLocation?.name}`}
                </h1>
                <div className="palace-controls">
                    {view === 'map' ? (
                        <button className="palace-btn" onClick={() => setShowLocationModal(true)}>
                            <FaPlus /> New Location
                        </button>
                    ) : (
                        <button className="palace-btn" onClick={() => setShowArtifactModal(true)}>
                            <FaPlus /> New Memory
                        </button>
                    )}
                </div>
            </div>

            <div className="palace-canvas">
                {view === 'map' ? (
                    <div className="locations-grid" style={{ display: 'flex', flexWrap: 'wrap', gap: '2rem' }}>
                        {locations.map(loc => (
                            <div key={loc.id} className="location-card" onClick={() => { setCurrentLocation(loc); setView('room'); }}>
                                <div className="location-icon" style={{ fontSize: '3rem', marginBottom: '1rem' }}>🏛️</div>
                                <div className="location-info">
                                    <div className="location-title">{loc.name}</div>
                                    <div className="location-desc">{loc.description}</div>
                                </div>
                            </div>
                        ))}
                        {locations.length === 0 && (
                            <div className="empty-state">
                                <h2>Your Mind Palace is Empty</h2>
                                <p>Create a location (e.g., "Library", "Parliament") to start placing memories.</p>
                            </div>
                        )}
                    </div>
                ) : (
                    <div
                        className="room-view"
                        style={{ width: '100%', height: '100%', position: 'relative' }}
                        onDragOver={(e) => e.preventDefault()}
                    >
                        {artifacts.map(art => (
                            <div
                                key={art.id}
                                className="artifact-node"
                                style={{
                                    left: `${art.x_position}%`,
                                    top: `${art.y_position}%`,
                                    backgroundColor: art.color
                                }}
                                draggable
                                onDragEnd={(e) => handleDragEnd(e, art.id)}
                                onClick={() => { setEditingArtifact(art); setShowArtifactModal(true); }}
                            >
                                {art.icon}
                                <div className="artifact-tooltip">{art.title}</div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Location Modal */}
            {showLocationModal && (
                <div className="palace-modal-overlay" onClick={() => setShowLocationModal(false)}>
                    <div className="palace-modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Construct New Location</h2>
                            <button className="close-btn" onClick={() => setShowLocationModal(false)}>×</button>
                        </div>
                        <div className="form-group">
                            <label>Name</label>
                            <input value={newName} onChange={e => setNewName(e.target.value)} placeholder="e.g., The Senate Hall" />
                        </div>
                        <div className="form-group">
                            <label>Description</label>
                            <textarea value={newDesc} onChange={e => setNewDesc(e.target.value)} placeholder="What do you store here?" />
                        </div>
                        <div className="modal-actions">
                            <button className="save-btn" onClick={handleCreateLocation}>Construct</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Artifact Modal */}
            {showArtifactModal && (
                <div className="palace-modal-overlay" onClick={() => { setShowArtifactModal(false); setEditingArtifact(null); }}>
                    <div className="palace-modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>{editingArtifact ? 'Recall Memory' : 'Place New Memory'}</h2>
                            <button className="close-btn" onClick={() => { setShowArtifactModal(false); setEditingArtifact(null); }}>×</button>
                        </div>
                        <div className="form-group">
                            <label>Title</label>
                            <input
                                value={editingArtifact ? editingArtifact.title : newName}
                                onChange={e => editingArtifact ? setEditingArtifact({ ...editingArtifact, title: e.target.value }) : setNewName(e.target.value)}
                                placeholder="e.g., Article 21"
                            />
                        </div>
                        <div className="form-group">
                            <label>Content</label>
                            <textarea
                                value={editingArtifact ? editingArtifact.content : newContent}
                                onChange={e => editingArtifact ? setEditingArtifact({ ...editingArtifact, content: e.target.value }) : setNewContent(e.target.value)}
                                placeholder="Details of the memory..."
                                rows={5}
                            />
                        </div>
                        <div className="modal-actions">
                            {editingArtifact ? (
                                <>
                                    <button className="delete-btn" onClick={async () => {
                                        await fetch(`http://localhost:5000/api/mind_palace/artifacts/${editingArtifact.id}`, { method: 'DELETE' });
                                        fetchArtifacts(currentLocation!.id);
                                        setShowArtifactModal(false);
                                        setEditingArtifact(null);
                                    }}>Forget</button>
                                    <button className="save-btn" onClick={async () => {
                                        await fetch(`http://localhost:5000/api/mind_palace/artifacts/${editingArtifact.id}`, {
                                            method: 'PUT',
                                            headers: { 'Content-Type': 'application/json' },
                                            body: JSON.stringify({ title: editingArtifact.title, content: editingArtifact.content })
                                        });
                                        fetchArtifacts(currentLocation!.id);
                                        setShowArtifactModal(false);
                                        setEditingArtifact(null);
                                    }}>Update</button>
                                </>
                            ) : (
                                <button className="save-btn" onClick={handleCreateArtifact}>Place Memory</button>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MindPalace;
