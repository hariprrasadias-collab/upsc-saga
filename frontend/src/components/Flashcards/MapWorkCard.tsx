// MapWorkCard.tsx - Interactive Map for Map Work Flashcards
import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for Leaflet marker icons in React
// @ts-ignore
import icon from 'leaflet/dist/images/marker-icon.png';
// @ts-ignore
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

interface Location {
    name: string;
    lat: number;
    lon: number;
    reason: string;
    question: string;
}

interface MapWorkCardProps {
    data: Location[];
    onComplete: () => void;
}

const MapEvents = ({ onMapClick }: { onMapClick: (e: L.LeafletMouseEvent) => void }) => {
    useMapEvents({
        click: onMapClick,
    });
    return null;
};

const MapWorkCard: React.FC<MapWorkCardProps> = ({ data, onComplete }) => {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [userClick, setUserClick] = useState<{ lat: number; lng: number } | null>(null);
    const [feedback, setFeedback] = useState<string | null>(null);
    const [revealed, setRevealed] = useState(false);
    const [score, setScore] = useState(0);

    const currentLocation = data[currentIndex];


    // Calculate distance between two coordinates in km (Haversine formula)
    const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number) => {
        const R = 6371; // Radius of the earth in km
        const dLat = deg2rad(lat2 - lat1);
        const dLon = deg2rad(lon2 - lon1);
        const a =
            Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        const d = R * c; // Distance in km
        return d;
    };

    const deg2rad = (deg: number) => {
        return deg * (Math.PI / 180);
    };

    const handleMapClick = (e: L.LeafletMouseEvent) => {
        if (revealed) return; // Ignore clicks if already revealed

        const clickedLat = e.latlng.lat;
        const clickedLng = e.latlng.lng;
        setUserClick({ lat: clickedLat, lng: clickedLng });

        const dist = calculateDistance(clickedLat, clickedLng, currentLocation.lat, currentLocation.lon);

        // Thresholds: < 50km = Excellent, < 200km = Good, else Miss
        if (dist < 50) {
            setFeedback(`🎯 Direct Hit! (${Math.round(dist)}km off)`);
            setScore(prev => prev + 2);
        } else if (dist < 200) {
            setFeedback(`✅ Close enough! (${Math.round(dist)}km off)`);
            setScore(prev => prev + 1);
        } else {
            setFeedback(`❌ Missed by ${Math.round(dist)}km. The location is shown.`);
        }

        setRevealed(true);
    };

    const handleNext = () => {
        setUserClick(null);
        setFeedback(null);
        setRevealed(false);
        if (currentIndex + 1 < data.length) {
            setCurrentIndex(prev => prev + 1);
        } else {
            onComplete();
        }
    };

    return (
        <div className="map-work-card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div className="map-header" style={{ padding: '10px', background: '#2c3e50', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <strong>Map Work Challenge ({currentIndex + 1}/{data.length})</strong>
                    <div style={{ fontSize: '1.2em', marginTop: '5px' }}>{currentLocation.question}</div>
                </div>
                <div>Score: {score}</div>
            </div>

            <div className="map-container" style={{ flex: 1, position: 'relative' }}>
                <MapContainer center={[20.5937, 78.9629]} zoom={4} style={{ height: '100%', width: '100%' }}>
                    {/* Auto-center map when location changes, but don't reveal exact spot immediately.
                        Maybe center on the general region? For now, we keep it static or center on India.
                        Actually, if we flyTo the location, it gives it away.
                        Let's just flyTo the first location's region or keep it broad.
                        To be safe, we won't auto-zoom to the target.
                        But we should ensure the map renders correctly. */}
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    <MapEvents onMapClick={handleMapClick} />

                    {/* Show actual location if revealed */}
                    {revealed && (
                        <Marker position={[currentLocation.lat, currentLocation.lon]} icon={DefaultIcon}>
                            <Popup>
                                <strong>{currentLocation.name}</strong><br/>
                                {currentLocation.reason}
                            </Popup>
                        </Marker>
                    )}

                    {/* Show user click */}
                    {userClick && (
                        <Marker position={[userClick.lat, userClick.lng]} icon={DefaultIcon} opacity={0.6}>
                             <Popup>Your Guess</Popup>
                        </Marker>
                    )}
                </MapContainer>

                {feedback && (
                    <div className="map-feedback-overlay" style={{
                        position: 'absolute',
                        bottom: '20px',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        background: 'rgba(0, 0, 0, 0.8)',
                        color: 'white',
                        padding: '15px',
                        borderRadius: '8px',
                        zIndex: 1000,
                        textAlign: 'center'
                    }}>
                        <div style={{ marginBottom: '10px' }}>{feedback}</div>
                        <button
                            onClick={handleNext}
                            style={{
                                padding: '8px 16px',
                                background: '#3498db',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer'
                            }}
                        >
                            {currentIndex + 1 < data.length ? "Next Location" : "Finish Map Work"}
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MapWorkCard;
