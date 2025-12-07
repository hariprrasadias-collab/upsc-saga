import React, { useState, useEffect, useRef } from 'react';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';
import mermaid from 'mermaid';
import './CheatSheetRenderer.css';

interface CheatSheetTab {
    id: string;
    label: string;
    content: string;
    type?: string; // 'markdown' (default) or 'mermaid'
}

interface CheatSheetData {
    title: string;
    tabs: CheatSheetTab[];
}

interface CheatSheetRendererProps {
    content: string;
}

// Mermaid Renderer Component
const MermaidDiagram: React.FC<{ code: string }> = ({ code }) => {
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (ref.current) {
            mermaid.initialize({ startOnLoad: true, theme: 'dark' });
            mermaid.run({ nodes: [ref.current] });
        }
    }, [code]);

    return (
        <div className="mermaid-container">
            <div ref={ref} className="mermaid">{code}</div>
        </div>
    );
};

const CheatSheetRenderer: React.FC<CheatSheetRendererProps> = ({ content }) => {
    const [data, setData] = useState<CheatSheetData | null>(null);
    const [activeTab, setActiveTab] = useState<string>('');
    const [searchTerm, setSearchTerm] = useState('');
    const [isLegacy, setIsLegacy] = useState<boolean>(false);
    const [isSpeaking, setIsSpeaking] = useState(false);

    useEffect(() => {
        try {
            const parsed = JSON.parse(content);
            if (parsed.tabs && Array.isArray(parsed.tabs)) {
                setData(parsed);
                if (parsed.tabs.length > 0) {
                    setActiveTab(parsed.tabs[0].id);
                }
                setIsLegacy(false);
            } else {
                setIsLegacy(true);
            }
        } catch (e) {
            setIsLegacy(true);
        }
    }, [content]);

    const handleSpeak = () => {
        if (isSpeaking) {
            window.speechSynthesis.cancel();
            setIsSpeaking(false);
            return;
        }

        if (!data) return;

        const currentTabObj = data.tabs.find(t => t.id === activeTab);
        if (currentTabObj) {
            const utterance = new SpeechSynthesisUtterance(currentTabObj.content);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.onend = () => setIsSpeaking(false);
            window.speechSynthesis.speak(utterance);
            setIsSpeaking(true);
        }
    };

    // Filter/Search Logic
    const getFilteredTabs = () => {
        if (!data) return [];
        if (!searchTerm) return data.tabs;

        // Return tabs where content or label matches search term
        return data.tabs.filter(tab =>
            tab.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
            tab.content.toLowerCase().includes(searchTerm.toLowerCase())
        );
    };

    // Highlight search term in text (simple version)
    // Note: ReactMarkdown doesn't easily support dynamic highlighting without plugins.
    // For now, search just filters tabs visibility in the nav, but we keep all tabs available content-wise?
    // Better: If search is active, show tabs that match.

    // Actually, let's keep all tabs in nav, but highlight the one containing the term?
    // Or just highlight matches?

    // Implementation: Search highlights matching tabs in Nav bar.
    const hasMatch = (tab: CheatSheetTab) => {
        if (!searchTerm) return false;
        return tab.content.toLowerCase().includes(searchTerm.toLowerCase());
    };

    if (isLegacy) {
        return (
            <div className="cheat-sheet-legacy">
                <div className="legacy-badge">Legacy Format</div>
                <MarkdownRenderer content={content} />
            </div>
        );
    }

    if (!data) return <div className="loading-pulse">Deciphering Codex...</div>;

    return (
        <div className="cheat-sheet-container">
            <header className="cs-header">
                <h3 className="cs-title">{data.title}</h3>
                <div className="cs-controls">
                    <input
                        type="text"
                        placeholder="Search cheat sheet..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="cs-search-input"
                    />
                    <button
                        className={`cs-action-btn ${isSpeaking ? 'active' : ''}`}
                        onClick={handleSpeak}
                        title={isSpeaking ? "Stop Speaking" : "Read Aloud"}
                    >
                        {isSpeaking ? '🔇' : '🔊'}
                    </button>
                    <button
                        className="cs-action-btn"
                        onClick={() => navigator.clipboard.writeText(JSON.stringify(data, null, 2))}
                        title="Copy Raw JSON"
                    >
                        📋
                    </button>
                </div>
            </header>

            <div className="cs-tabs-nav">
                {data.tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`cs-tab-btn ${activeTab === tab.id ? 'active' : ''} ${hasMatch(tab) ? 'match-highlight' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        {tab.label}
                        {hasMatch(tab) && <span className="match-dot" />}
                    </button>
                ))}
            </div>

            <div className="cs-tab-content glass-panel">
                {data.tabs.map(tab => (
                    <div
                        key={tab.id}
                        className={`cs-tab-pane ${activeTab === tab.id ? 'active' : ''}`}
                        style={{ display: activeTab === tab.id ? 'block' : 'none' }}
                    >
                        {tab.type === 'mermaid' ? (
                            <MermaidDiagram code={tab.content} />
                        ) : (
                            <MarkdownRenderer content={tab.content} />
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CheatSheetRenderer;
