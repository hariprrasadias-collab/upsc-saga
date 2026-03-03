import React, { useState } from 'react';
import './TerritoryNodeMap.css';

interface TerritoryNode {
    id: string;
    label: string;
    status: 'secured' | 'contested' | 'unexplored';
    x: number;
    y: number;
}

// Simulated data for the map view
const SAMPLE_NODES: TerritoryNode[] = [
    { id: 'polity-1', label: 'Constitution', status: 'secured', x: 20, y: 30 },
    { id: 'polity-2', label: 'Parliament', status: 'contested', x: 40, y: 25 },
    { id: 'geo-1', label: 'Physical Geo', status: 'unexplored', x: 60, y: 40 },
    { id: 'hist-1', label: 'Modern India', status: 'secured', x: 30, y: 60 },
    { id: 'eco-1', label: 'Macro Econ', status: 'contested', x: 70, y: 70 },
    { id: 'env-1', label: 'Ecology', status: 'unexplored', x: 80, y: 20 },
];

const TerritoryNodeMap: React.FC = () => {
    const [activeNode, setActiveNode] = useState<string | null>(null);

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'secured': return '#34c759'; // Green
            case 'contested': return '#ffcc00'; // Yellow/Orange
            case 'unexplored': return '#ff3b30'; // Red
            default: return '#555';
        }
    };

    return (
        <div className="territory-map-container">
            <header className="map-header">
                <h3>GLOBAL SYLLABUS THEATER</h3>
                <div className="map-legend">
                    <span className="legend-item"><span className="dot secured"></span>Secured</span>
                    <span className="legend-item"><span className="dot contested"></span>Contested</span>
                    <span className="legend-item"><span className="dot unexplored"></span>Unexplored</span>
                </div>
            </header>

            <div className="battle-map">
                {/* Background Grid Texture */}
                <div className="radar-sweep"></div>

                {SAMPLE_NODES.map(node => (
                    <div
                        key={node.id}
                        className={`map-node ${node.status} ${activeNode === node.id ? 'active' : ''}`}
                        style={{ left: `${node.x}%`, top: `${node.y}%` }}
                        onMouseEnter={() => setActiveNode(node.id)}
                        onMouseLeave={() => setActiveNode(null)}
                    >
                        <div className="node-core" style={{ backgroundColor: getStatusColor(node.status) }}></div>
                        <div className="node-pulse" style={{ borderColor: getStatusColor(node.status) }}></div>

                        {activeNode === node.id && (
                            <div className="node-tooltip">
                                <strong>{node.label}</strong>
                                <span>Status: {node.status.toUpperCase()}</span>
                            </div>
                        )}
                    </div>
                ))}

                {/* Draw some fake SVG lines between nodes to look like a network */}
                <svg className="map-connections" width="100%" height="100%">
                    <line x1="20%" y1="30%" x2="40%" y2="25%" stroke="#00ffff" strokeWidth="1" strokeOpacity="0.3" strokeDasharray="5,5" />
                    <line x1="40%" y1="25%" x2="60%" y2="40%" stroke="#00ffff" strokeWidth="1" strokeOpacity="0.3" />
                    <line x1="30%" y1="60%" x2="70%" y2="70%" stroke="#00ffff" strokeWidth="1" strokeOpacity="0.3" strokeDasharray="5,5" />
                    <line x1="20%" y1="30%" x2="30%" y2="60%" stroke="#00ffff" strokeWidth="1" strokeOpacity="0.3" />
                </svg>
            </div>
        </div>
    );
};

export default TerritoryNodeMap;
