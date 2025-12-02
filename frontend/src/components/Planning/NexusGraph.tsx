import React, { useEffect, useRef, useState } from 'react';
import { KnowledgeGraphEngine, type GraphNode, type GraphLink } from '../../util/KnowledgeGraphEngine';

interface NexusGraphProps {
    engine: KnowledgeGraphEngine;
    completedItems: { subject: string, topic: string }[];
    onNodeClick?: (node: GraphNode) => void;
    onDebateClick?: (topic: string) => void;
}

const NexusGraph: React.FC<NexusGraphProps> = React.memo(({ engine, completedItems, onNodeClick, onDebateClick }) => {
    const svgRef = useRef<SVGSVGElement>(null);
    const [nodes, setNodes] = useState<GraphNode[]>([]);
    const [links, setLinks] = useState<GraphLink[]>([]);
    const [dimensions] = useState({ width: 800, height: 600 });
    const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

    // Simulation State
    const requestRef = useRef<number | null>(null);

    useEffect(() => {
        const initGraph = async () => {
            // Load data from backend (Golden Path Service)
            await engine.loadData();

            // Update mastery based on completed tasks
            engine.updateMastery(completedItems);
            const data = engine.getGraphData();

            // Initialize random positions (preserve existing positions if possible could be better, but for now re-init is safer for data sync)
            const initializedNodes = data.nodes.map(n => ({
                ...n,
                x: Math.random() * 800,
                y: Math.random() * 600,
                vx: 0,
                vy: 0
            }));
            setNodes(initializedNodes);
            setLinks(data.links);
        };

        initGraph();
    }, [engine, completedItems]);

    // Simple Force-Directed Simulation Loop
    const simulate = () => {
        setNodes(prevNodes => {
            const newNodes = prevNodes.map(n => ({ ...n })); // Shallow copy
            const center = { x: dimensions.width / 2, y: dimensions.height / 2 };

            // 1. Repulsion (Coulomb's Law)
            for (let i = 0; i < newNodes.length; i++) {
                for (let j = i + 1; j < newNodes.length; j++) {
                    const n1 = newNodes[i];
                    const n2 = newNodes[j];
                    const dx = n1.x! - n2.x!;
                    const dy = n1.y! - n2.y!;
                    const distSq = dx * dx + dy * dy || 1;
                    const force = 5000 / distSq; // Repulsion strength
                    const fx = (dx / Math.sqrt(distSq)) * force;
                    const fy = (dy / Math.sqrt(distSq)) * force;

                    n1.vx! += fx;
                    n1.vy! += fy;
                    n2.vx! -= fx;
                    n2.vy! -= fy;
                }
            }

            // 2. Attraction (Springs)
            links.forEach(link => {
                const source = newNodes.find(n => n.id === link.source);
                const target = newNodes.find(n => n.id === link.target);
                if (source && target) {
                    const dx = target.x! - source.x!;
                    const dy = target.y! - source.y!;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    const force = (dist - 150) * 0.05; // Spring constant & rest length
                    const fx = (dx / dist) * force;
                    const fy = (dy / dist) * force;

                    source.vx! += fx;
                    source.vy! += fy;
                    target.vx! -= fx;
                    target.vy! -= fy;
                }
            });

            // 3. Center Gravity
            newNodes.forEach(n => {
                n.vx! += (center.x - n.x!) * 0.01;
                n.vy! += (center.y - n.y!) * 0.01;
            });

            // 4. Update Positions & Damping
            return newNodes.map(n => ({
                ...n,
                x: n.x! + n.vx!,
                y: n.y! + n.vy!,
                vx: n.vx! * 0.9, // Damping
                vy: n.vy! * 0.9
            }));
        });

        requestRef.current = requestAnimationFrame(simulate);
    };

    useEffect(() => {
        if (nodes.length > 0) {
            requestRef.current = requestAnimationFrame(simulate);
        }
        return () => cancelAnimationFrame(requestRef.current!);
    }, [nodes.length]); // Restart if nodes change (initial load)

    // Stop simulation on unmount
    useEffect(() => {
        return () => cancelAnimationFrame(requestRef.current!);
    }, []);

    const getNodeColor = (group: string) => {
        switch (group) {
            case 'History': return '#e74c3c';
            case 'Geography': return '#2ecc71';
            case 'Polity': return '#3498db';
            case 'Economy': return '#f1c40f';
            case 'Science': return '#9b59b6';
            case 'Environment': return '#1abc9c';
            default: return '#ecf0f1';
        }
    };

    return (
        <div className="nexus-container">
            <svg ref={svgRef} width="100%" height="600" viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}>
                <defs>
                    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                        <feGaussianBlur stdDeviation="2.5" result="coloredBlur" />
                        <feMerge>
                            <feMergeNode in="coloredBlur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                    <filter id="gold-glow" x="-50%" y="-50%" width="200%" height="200%">
                        <feGaussianBlur stdDeviation="4" result="coloredBlur" />
                        <feMerge>
                            <feMergeNode in="coloredBlur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>

                {/* Links */}
                {links.map((link, i) => {
                    const source = nodes.find(n => n.id === link.source);
                    const target = nodes.find(n => n.id === link.target);
                    if (!source || !target) return null;
                    return (
                        <line
                            key={i}
                            x1={source.x}
                            y1={source.y}
                            x2={target.x}
                            y2={target.y}
                            stroke="#555"
                            strokeWidth={link.type === 'dependency' ? 2 : 1}
                            strokeOpacity={0.6}
                            strokeDasharray={link.type === 'related' ? "5,5" : "none"}
                        />
                    );
                })}

                {/* Nodes */}
                {nodes.map((node) => (
                    <g
                        key={node.id}
                        transform={`translate(${node.x}, ${node.y})`}
                        onClick={(e) => {
                            e.stopPropagation();
                            setSelectedNode(node);
                            if (onNodeClick) onNodeClick(node);
                        }}
                        style={{ cursor: 'pointer' }}
                    >
                        <circle
                            r={node.radius}
                            fill={node.isBridge ? '#f1c40f' : getNodeColor(node.group)}
                            fillOpacity={0.2 + (node.mastery / 200)} // Opacity based on mastery
                            stroke={node.isBridge ? '#f1c40f' : getNodeColor(node.group)}
                            strokeWidth={node.isBridge ? 3 : 2}
                            filter={node.isBridge ? "url(#gold-glow)" : "url(#glow)"}
                        />
                        <text
                            dy={5}
                            textAnchor="middle"
                            fill="#fff"
                            fontSize="10px"
                            fontFamily="Orbitron"
                            pointerEvents="none"
                        >
                            {node.label}
                        </text>
                    </g>
                ))}
            </svg>

            {selectedNode && (
                <div className="nexus-side-panel" style={{
                    position: 'absolute',
                    top: 0,
                    right: 0,
                    width: '300px',
                    height: '100%',
                    background: 'rgba(10, 15, 30, 0.95)',
                    borderLeft: '1px solid rgba(52, 152, 219, 0.3)',
                    padding: '20px',
                    boxShadow: '-5px 0 15px rgba(0,0,0,0.5)',
                    backdropFilter: 'blur(10px)',
                    overflowY: 'auto',
                    color: '#ecf0f1',
                    zIndex: 10
                }}>
                    <button
                        onClick={() => setSelectedNode(null)}
                        style={{
                            position: 'absolute',
                            top: '10px',
                            right: '10px',
                            background: 'none',
                            border: 'none',
                            color: '#7f8c8d',
                            cursor: 'pointer',
                            fontSize: '1.2rem'
                        }}
                    >×</button>

                    <h2 style={{
                        marginTop: '20px',
                        marginBottom: '5px',
                        color: getNodeColor(selectedNode.group),
                        fontFamily: 'Orbitron'
                    }}>
                        {selectedNode.label}
                    </h2>
                    <span style={{
                        fontSize: '0.8rem',
                        textTransform: 'uppercase',
                        letterSpacing: '1px',
                        color: '#bdc3c7'
                    }}>{selectedNode.group}</span>

                    <div className="panel-section" style={{ marginTop: '30px' }}>
                        <h3>MASTERY LEVEL</h3>
                        <div className="mastery-display" style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                            <span style={{ fontSize: '2rem', fontWeight: 'bold', color: '#fff' }}>
                                {Math.round(selectedNode.mastery)}%
                            </span>
                            <div className="mastery-bar-container" style={{ flex: 1, height: '8px', background: 'rgba(255,255,255,0.1)', borderRadius: '4px' }}>
                                <div className="mastery-fill" style={{
                                    width: `${selectedNode.mastery}%`,
                                    height: '100%',
                                    background: getNodeColor(selectedNode.group),
                                    borderRadius: '4px',
                                    boxShadow: `0 0 10px ${getNodeColor(selectedNode.group)}`
                                }}></div>
                            </div>
                        </div>
                    </div>

                    {selectedNode.isBridge && (
                        <div className="bridge-alert" style={{
                            marginTop: '20px',
                            padding: '10px',
                            background: 'rgba(241, 196, 15, 0.1)',
                            border: '1px solid #f1c40f',
                            borderRadius: '4px',
                            fontSize: '0.9rem',
                            color: '#f1c40f'
                        }}>
                            ⚠️ <strong>BRIDGE NODE</strong><br />
                            Critical concept linking multiple domains. High priority for revision.
                        </div>
                    )}

                    <div className="panel-actions" style={{ marginTop: '30px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        <button
                            style={{
                                background: 'rgba(52, 152, 219, 0.2)',
                                border: '1px solid #3498db',
                                color: '#fff',
                                padding: '10px',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontFamily: 'Orbitron',
                                transition: 'all 0.3s ease'
                            }}
                            onClick={(e) => {
                                e.stopPropagation();
                                if (onDebateClick) onDebateClick(selectedNode.label);
                            }}
                        >
                            🏛️ DEBATE THIS TOPIC
                        </button>
                        <button
                            style={{
                                background: 'rgba(46, 204, 113, 0.2)',
                                border: '1px solid #2ecc71',
                                color: '#fff',
                                padding: '10px',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontFamily: 'Orbitron'
                            }}
                            onClick={() => alert(`Opening resources for ${selectedNode.label}...`)}
                        >
                            📚 STUDY NOW
                        </button>
                    </div>

                    <div className="connected-nodes" style={{ marginTop: '30px' }}>
                        <h4 style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '5px' }}>CONNECTED CONCEPTS</h4>
                        <ul style={{ listStyle: 'none', padding: 0, marginTop: '10px' }}>
                            {links
                                .filter(l => l.source === selectedNode.id || l.target === selectedNode.id)
                                .map((link, i) => {
                                    const otherId = link.source === selectedNode.id ? link.target : link.source;
                                    const otherNode = nodes.find(n => n.id === otherId);
                                    if (!otherNode) return null;
                                    return (
                                        <li key={i} style={{
                                            padding: '5px 0',
                                            fontSize: '0.9rem',
                                            color: '#bdc3c7',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '10px'
                                        }}>
                                            <span style={{
                                                width: '8px',
                                                height: '8px',
                                                borderRadius: '50%',
                                                background: getNodeColor(otherNode.group)
                                            }}></span>
                                            {otherNode.label}
                                        </li>
                                    );
                                })}
                        </ul>
                    </div>
                </div>
            )}
        </div>
    );
});

export default NexusGraph;
