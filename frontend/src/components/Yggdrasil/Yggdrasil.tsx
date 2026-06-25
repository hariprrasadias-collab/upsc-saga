import { API_BASE_URL } from '../../config';

// /frontend/src/components/Yggdrasil/YggdrasilTree.tsx
import React, { useState, useEffect, useCallback } from 'react';
import type { SyllabusNode } from '../../data/syllabus';
import { upscSyllabus } from '../../data/syllabus';
import './Yggdrasil.css';
import { brainService } from '../../services/BrainService';
import MarkdownRenderer from '../Shared/MarkdownRenderer';

// --- HELPER: Map Status String <-> Integer Level ---
// 0 = Locked
// 1 = Unlocked (Started)
// 2 = Read (1st Reading)
// 3 = Rev 1 (Revision 1)
// 4 = Rev 2 (Revision 2)
// 5 = Mastered (Ready)

const getLevel = (status: string): number => {
    switch (status) {
        case 'locked': return 0;
        case 'unlocked': return 1;
        case 'read': return 2;
        case 'rev1': return 3;
        case 'rev2': return 4;
        case 'mastered': return 5;
        default: return 1;
    }
};

const getStatusFromLevel = (level: number): string => {
    const levels = ['locked', 'unlocked', 'read', 'rev1', 'rev2', 'mastered'];
    return levels[level] || 'unlocked';
};

const getStatusLabel = (level: number): string => {
    const labels = [
        "LOCKED (Requires Prerequisite)",
        "STARTED (NCERTs/Intro)",
        "1ST READING COMPLETE",
        "REVISION 1 COMPLETE (Notes Made)",
        "REVISION 2 COMPLETE (PYQs Solved)",
        "MASTERED (Exam Ready)"
    ];
    return labels[level] || "UNKNOWN";
};

// --- COMPONENT 1: Tablet Modal ---
interface TabletModalProps {
    node: SyllabusNode;
    onClose: () => void;
    onUpdateStatus: (newLevel: number) => void;
}

const TabletModal: React.FC<TabletModalProps> = ({ node, onClose, onUpdateStatus }) => {
    const [explanation, setExplanation] = useState<string | null>(null);
    const [isExplaining, setIsExplaining] = useState(false);

    const handleExplain = async () => {
        setIsExplaining(true);
        try {
            const result = await brainService.executeAction('EXPLAIN_SYLLABUS_NODE', { node: node.title });
            if (result.success) {
                setExplanation(result.explanation);
            } else {
                alert("Explanation failed: " + result.message);
            }
        } catch (err) {
            console.error("Explanation error:", err);
            alert("The Brain is silent.");
        } finally {
            setIsExplaining(false);
        }
    };
    const currentLevel = getLevel(node.status);

    return (
        <div className="tablet-overlay" onClick={onClose}>
            <div className="tablet-stone" onClick={(e) => e.stopPropagation()}>
                <div className="tablet-header">
                    <h2>{node.title}</h2>
                    <button className="close-btn" onClick={onClose} aria-label="Close"><span aria-hidden="true">✕</span></button>
                </div>

                <div className="tablet-body">
                    <p className="tablet-desc">{node.description}</p>

                    {explanation && (
                        <div className="explanation-box" style={{
                            background: 'rgba(255, 255, 255, 0.1)',
                            padding: '10px',
                            borderRadius: '5px',
                            marginBottom: '15px',
                            fontSize: '14px',
                            lineHeight: '1.4'
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                                <strong style={{ color: '#f1c40f' }}>🧠 Strategos Insight:</strong>
                                <button onClick={() => setExplanation(null)} style={{ background: 'none', border: 'none', color: '#ccc', cursor: 'pointer' }} aria-label="Close"><span aria-hidden="true">✕</span></button>
                            </div>
                            <MarkdownRenderer content={explanation} />
                        </div>
                    )}

                    {/* REVISION TRACKER UI */}
                    <div className="revision-tracker">
                        <span className="tracker-label">
                            Status: <span style={{ color: 'white', fontWeight: 'bold' }}>{getStatusLabel(currentLevel)}</span>
                        </span>
                        <div className="tracker-dots">
                            {[1, 2, 3, 4, 5].map(lvl => (
                                <div
                                    key={lvl}
                                    className={`dot l${lvl} ${currentLevel >= lvl ? 'active' : ''}`}
                                    title={getStatusLabel(lvl)}
                                ></div>
                            ))}
                        </div>
                    </div>

                    {node.resources && (
                        <div className="resources-section">
                            <h3>Recommended Sources</h3>
                            <ul className="resources-list">
                                {node.resources.map((res, idx) => <li key={idx}>{res}</li>)}
                            </ul>
                        </div>
                    )}

                    <div className="tablet-actions" style={{ display: 'flex', gap: '10px' }}>
                        <button
                            className="mastery-btn"
                            style={{ borderColor: '#9b59b6', color: '#9b59b6' }}
                            onClick={handleExplain}
                            disabled={isExplaining}
                        >
                            {isExplaining ? 'Thinking...' : '🧠 Explain'}
                        </button>
                        {/* REGRESS BUTTON (Forgetting Curve) */}
                        {currentLevel > 1 && (
                            <button
                                className="mastery-btn"
                                style={{ borderColor: '#e74c3c', color: '#e74c3c' }}
                                onClick={() => onUpdateStatus(currentLevel - 1)}
                            >
                                ▼ Regress
                            </button>
                        )}

                        {/* PROGRESS BUTTON */}
                        {currentLevel < 5 ? (
                            <button
                                className="mastery-btn"
                                onClick={() => onUpdateStatus(currentLevel + 1)}
                            >
                                ▲ Mark {getStatusLabel(currentLevel + 1)}
                            </button>
                        ) : (
                            <button className="mastery-btn mastered" disabled>
                                👑 TOPIC MASTERED
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

// --- COMPONENT 2: Tree Node ---
interface TreeNodeProps {
    node: SyllabusNode;
    onNodeClick: (node: SyllabusNode) => void;
    depth?: number;
}

const TreeNode: React.FC<TreeNodeProps> = ({ node, onNodeClick, depth = 0 }) => {
    // Auto-expand first 2 levels for better UX
    const [isExpanded, setIsExpanded] = useState(depth < 2);

    // Convert status string to integer for dynamic CSS class
    const level = getLevel(node.status);

    const handleStoneClick = (e: React.MouseEvent) => {
        e.stopPropagation();
        onNodeClick(node);
    };

    const handleToggleExpand = (e: React.MouseEvent) => {
        e.stopPropagation();
        setIsExpanded(!isExpanded);
    };

    // Logic to determine layout (Grid vs List)
    const hasChildren = node.children && node.children.length > 0;
    const isGridLayer = hasChildren && !node.children![0].children;

    return (
        <div className={`tree-node status-${level}`}>
            <div className="node-wrapper">
                <div className="node-content" onClick={handleStoneClick}>
                    <span className="node-title">{node.title}</span>
                </div>

                {hasChildren && (
                    <button className={`expand-btn ${isExpanded ? 'expanded' : ''}`} onClick={handleToggleExpand}>
                        {isExpanded ? '−' : '+'}
                    </button>
                )}
            </div>

            {hasChildren && isExpanded && (
                <div className={`children-container ${isGridLayer ? 'leaf-grid' : ''}`}>
                    {node.children!.map(child => (
                        <TreeNode
                            key={child.id}
                            node={child}
                            onNodeClick={onNodeClick}
                            depth={depth + 1}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

// --- COMPONENT 3: Main Container ---
const YggdrasilTree: React.FC = () => {
    const [selectedNode, setSelectedNode] = useState<SyllabusNode | null>(null);
    const [, setForceUpdate] = useState(0);
    const [treeData, setTreeData] = useState<SyllabusNode>(upscSyllabus);
    const [loading, setLoading] = useState(true);

    // 1. Load Progress from Backend
    const fetchProgress = useCallback(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/codex/progress`);
            if (!response.ok) return;

            const progressMap: Record<string, string> = await response.json();

            // Recursively apply status from DB to local Syllabus object
            const applyStatus = (node: SyllabusNode) => {
                if (progressMap[node.id]) {
                    node.status = progressMap[node.id] as SyllabusNode['status'];
                }
                if (node.children) {
                    node.children.forEach(applyStatus);
                }
            };

            applyStatus(upscSyllabus);
            setTreeData({ ...upscSyllabus });
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { fetchProgress(); }, [fetchProgress]);

    // 2. Handle Status Change (Increment/Decrement)
    const handleStatusUpdate = async (newLevel: number) => {
        if (selectedNode) {
            const newStatusStr = getStatusFromLevel(newLevel) as SyllabusNode['status'];

            // Optimistic UI Update
            selectedNode.status = newStatusStr;
            setForceUpdate(p => p + 1);
            setSelectedNode(null); // Close modal

            // API Call to Save
            try {
                await fetch(`${API_BASE_URL}/api/codex/update`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ node_id: selectedNode.id, status: newStatusStr })
                });
            } catch (err) {
                console.error("Failed to save progress", err);
            }
        }
    };

    if (loading) return <div style={{ color: 'white', textAlign: 'center', marginTop: '50px' }}>Consulting the Archives...</div>;

    return (
        <div className="yggdrasil-container">
            <h1 className="tree-header">YGGDRASIL</h1>

            <div className="tree-wrapper">
                <TreeNode node={treeData} onNodeClick={setSelectedNode} />
            </div>

            {selectedNode && (
                <TabletModal
                    node={selectedNode}
                    onClose={() => setSelectedNode(null)}
                    onUpdateStatus={handleStatusUpdate}
                />
            )}
        </div>
    );
};

export default YggdrasilTree;