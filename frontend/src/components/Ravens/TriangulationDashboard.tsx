import { API_BASE_URL } from '../../config';

import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import './TriangulationDashboard.css';

interface TriangulationResult {
    topic: string;
    synthesis: string;
    scholars: { name: string; quote: string; context: string }[];
    data_bank: { statistic: string; source: string; relevance: string }[];
    critical_axis: { arguments_for: string[]; arguments_against: string[] };
    pestle: { political: string; economic: string; sociological: string; technological: string; legal: string; environmental: string };
    gs_linkages: { gs1: string; gs2: string; gs3: string; gs4: string };
    way_forward: { immediate: string; medium_term: string; long_term: string };
    predicted_question: string;
    mind_map_code: string;
    theory: { source: string; chapter: string; relevance: string }[];
    precedents: { name: string; type: string; summary: string }[];
    pyqs: { year: number; question_text: string; subject: string }[];
}

interface Props {
    text: string;
    onClose: () => void;
}

const TriangulationDashboard: React.FC<Props> = ({ text, onClose }) => {
    const [result, setResult] = useState<TriangulationResult | null>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'core' | 'prism' | 'omni' | 'solution'>('core');

    React.useEffect(() => {
        const analyze = async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/triangulation/analyze`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                });
                const data = await res.json();
                setResult(data);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        analyze();
    }, [text]);

    const [saving, setSaving] = useState(false);

    const handleSaveToLore = async () => {
        if (!result) return;
        setSaving(true);
        try {
            const content = `
# Source Triangulation: ${result.topic}

## 🧬 Deep Synthesis
${result.synthesis}

## 🎓 Scholar's Corner
${result.scholars.map(s => `- "${s.quote}" — ${s.name} (${s.context})`).join('\n')}

## 📊 Data Bank
${result.data_bank.map(d => `- ${d.statistic} (Source: ${d.source})`).join('\n')}

## ⚖️ Critical Axis
**FOR:**
${result.critical_axis.arguments_for?.map(a => `- ${a}`).join('\n')}

**AGAINST:**
${result.critical_axis.arguments_against?.map(a => `- ${a}`).join('\n')}

## 🌐 PESTLE Scan
${Object.entries(result.pestle).map(([k, v]) => `- **${k.toUpperCase()}**: ${v}`).join('\n')}

## 🔗 GS Linkages
${Object.entries(result.gs_linkages).map(([k, v]) => `- **${k.toUpperCase()}**: ${v}`).join('\n')}

## 🚀 Way Forward
- **Immediate**: ${result.way_forward.immediate}
- **Medium**: ${result.way_forward.medium_term}
- **Long**: ${result.way_forward.long_term}

## 🔮 Predicted Question
${result.predicted_question}
            `;

            const res = await fetch(`${API_BASE_URL}/api/lore`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: `📐 Triangulation: ${result.topic}`,
                    content: content.trim()
                })
            });

            if (res.ok) {
                alert('Saved to Lore Tablets!');
            } else {
                alert('Failed to save.');
            }
        } catch (e) {
            console.error(e);
            alert('Error saving to Lore.');
        } finally {
            setSaving(false);
        }
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        // Could add a toast here
    };

    // Safe Base64 encoding for Unicode characters (emojis, etc.)
    const toBase64 = (str: string) => {
        try {
            return btoa(unescape(encodeURIComponent(str)));
        } catch (e) {
            console.error("Base64 encoding failed", e);
            return "";
        }
    };

    const renderTabContent = () => {
        if (!result) return null;

        switch (activeTab) {
            case 'core':
                const mermaidUrl = result.mind_map_code ? `https://mermaid.ink/img/${toBase64(result.mind_map_code)}` : '';
                return (
                    <div className="t-tab-content fade-in">
                        <div className="t-section synthesis-section">
                            <h3>🧬 Deep Synthesis</h3>
                            <p>{result.synthesis}</p>
                        </div>
                        <div className="t-grid-2">
                            <div className="t-col">
                                <h3>🧠 Mind Map Blueprint</h3>
                                <div className="mind-map-container">
                                    {mermaidUrl ? (
                                        <img src={mermaidUrl} alt="Mind Map" className="mind-map-img" />
                                    ) : (
                                        <div className="t-empty">Mind Map Unavailable</div>
                                    )}
                                </div>
                            </div>
                            <div className="t-col">
                                <h3>❓ Relevant PYQs</h3>
                                <div className="t-list">
                                    {result.pyqs.length > 0 ? result.pyqs.map((q, i) => (
                                        <div key={i} className="t-card pyq-card">
                                            <div className="t-meta">{q.year} | {q.subject}</div>
                                            <div className="t-question">{q.question_text}</div>
                                        </div>
                                    )) : <div className="t-empty">No direct PYQs found.</div>}
                                </div>
                            </div>
                        </div>
                    </div>
                );
            case 'prism':
                return (
                    <div className="t-tab-content fade-in">
                        <div className="t-grid-2">
                            <div className="t-col">
                                <h3>🎓 Scholar's Corner</h3>
                                {result.scholars.map((s, i) => (
                                    <div key={i} className="t-card scholar-card group">
                                        <div className="quote">"{s.quote}"</div>
                                        <div className="author">— {s.name}</div>
                                        <div className="context">({s.context})</div>
                                        <button aria-label="Copy to clipboard" className="copy-btn" onClick={() => copyToClipboard(`"${s.quote}" - ${s.name}`)}>📋</button>
                                    </div>
                                ))}
                            </div>
                            <div className="t-col">
                                <h3>📊 Data Bank</h3>
                                {result.data_bank.map((d, i) => (
                                    <div key={i} className="t-card data-card group">
                                        <div>
                                            <div className="stat">{d.statistic}</div>
                                            <div className="source">Source: {d.source}</div>
                                        </div>
                                        <button aria-label="Copy to clipboard" className="copy-btn" onClick={() => copyToClipboard(`${d.statistic} (${d.source})`)}>📋</button>
                                    </div>
                                ))}
                            </div>
                        </div>
                        <div className="t-section critical-axis">
                            <h3>⚖️ Critical Axis</h3>
                            <div className="axis-container">
                                <div className="axis-col for">
                                    <h4>Arguments FOR</h4>
                                    <ul>{result.critical_axis.arguments_for?.map((a, i) => <li key={i}>{a}</li>)}</ul>
                                </div>
                                <div className="axis-col against">
                                    <h4>Arguments AGAINST</h4>
                                    <ul>{result.critical_axis.arguments_against?.map((a, i) => <li key={i}>{a}</li>)}</ul>
                                </div>
                            </div>
                        </div>
                    </div>
                );
            case 'omni':
                return (
                    <div className="t-tab-content fade-in">
                        <div className="t-section pestle-grid">
                            <h3>🌐 PESTLE Scan</h3>
                            <div className="pestle-cards">
                                {Object.entries(result.pestle).map(([key, val]) => (
                                    <div key={key} className={`pestle-card ${key}`}>
                                        <div className="p-label">{key.charAt(0).toUpperCase() + key.slice(1)}</div>
                                        <div className="p-val">{val}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                        <div className="t-section gs-linkages">
                            <h3>🔗 Inter-Paper Linkages</h3>
                            <div className="gs-grid">
                                <div className="gs-card gs1"><strong>GS-1:</strong> {result.gs_linkages.gs1}</div>
                                <div className="gs-card gs2"><strong>GS-2:</strong> {result.gs_linkages.gs2}</div>
                                <div className="gs-card gs3"><strong>GS-3:</strong> {result.gs_linkages.gs3}</div>
                                <div className="gs-card gs4"><strong>GS-4:</strong> {result.gs_linkages.gs4}</div>
                            </div>
                        </div>
                    </div>
                );
            case 'solution':
                return (
                    <div className="t-tab-content fade-in">
                        <div className="t-section way-forward">
                            <h3>🚀 The Way Forward</h3>
                            <div className="wf-timeline">
                                <div className="wf-item immediate">
                                    <span className="wf-tag">Immediate</span>
                                    <p>{result.way_forward.immediate}</p>
                                </div>
                                <div className="wf-item medium">
                                    <span className="wf-tag">Medium-Term</span>
                                    <p>{result.way_forward.medium_term}</p>
                                </div>
                                <div className="wf-item long">
                                    <span className="wf-tag">Long-Term</span>
                                    <p>{result.way_forward.long_term}</p>
                                </div>
                            </div>
                        </div>
                        <div className="t-section prediction-box">
                            <h3>🔮 Oracle Prediction</h3>
                            <div className="prediction-card">
                                <div className="prediction-label">Expected Mains Question:</div>
                                <div className="prediction-text">{result.predicted_question}</div>
                            </div>
                        </div>
                    </div>
                );
        }
    };

    React.useEffect(() => {
        const handleEsc = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };
        window.addEventListener('keydown', handleEsc);
        return () => window.removeEventListener('keydown', handleEsc);
    }, [onClose]);

    const handleBackdropClick = (e: React.MouseEvent) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    return createPortal(
        <div className="triangulation-overlay" onClick={handleBackdropClick}>
            <div className="triangulation-modal omni-modal">
                <div className="t-header">
                    <div className="header-title">
                        <h2>📐 Source Triangulation 5.0</h2>
                        <span className="subtitle">The Omni-Link System</span>
                    </div>
                    <div className="header-actions">
                        {result && (
                            <button className="save-btn" onClick={handleSaveToLore} disabled={saving}>
                                {saving ? '💾 Saving...' : '💾 Save to Lore'}
                            </button>
                        )}
                        <button aria-label="Close" onClick={onClose} className="close-btn">×</button>
                    </div>
                </div>

                {loading ? (
                    <div className="t-loading">
                        <div className="scanner"></div>
                        <div className="loading-text">
                            <span className="typing">Triangulating Sources...</span>
                            <span className="sub-text">Scanning PESTLE • Linking GS Papers • Predicting Questions</span>
                        </div>
                    </div>
                ) : result ? (
                    <>
                        <div className="t-tabs">
                            <button className={`tab-btn ${activeTab === 'core' ? 'active' : ''}`} onClick={() => setActiveTab('core')}>🧬 The Core</button>
                            <button className={`tab-btn ${activeTab === 'prism' ? 'active' : ''}`} onClick={() => setActiveTab('prism')}>💎 The Prism</button>
                            <button className={`tab-btn ${activeTab === 'omni' ? 'active' : ''}`} onClick={() => setActiveTab('omni')}>🌐 Omni-Link</button>
                            <button className={`tab-btn ${activeTab === 'solution' ? 'active' : ''}`} onClick={() => setActiveTab('solution')}>🚀 Solution</button>
                        </div>
                        <div className="t-content-area">
                            {renderTabContent()}
                        </div>
                    </>
                ) : (
                    <div className="t-error">Analysis Failed</div>
                )}
            </div>
        </div>,
        document.body
    );
};

export default TriangulationDashboard;
