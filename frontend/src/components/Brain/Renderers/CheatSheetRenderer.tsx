import React, { useState, useEffect } from 'react';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';
import './CheatSheetRenderer.css';

interface CheatSheetTab {
    id: string;
    label: string;
    content: string;
}

interface CheatSheetData {
    title: string;
    tabs: CheatSheetTab[];
}

interface CheatSheetRendererProps {
    content: string; // Can be JSON string or raw markdown (legacy)
}

const CheatSheetRenderer: React.FC<CheatSheetRendererProps> = ({ content }) => {
    const [data, setData] = useState<CheatSheetData | null>(null);
    const [activeTab, setActiveTab] = useState<string>('');
    const [isLegacy, setIsLegacy] = useState<boolean>(false);

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
                // JSON but not our structure? Treat as legacy text.
                setIsLegacy(true);
            }
        } catch (e) {
            // Not JSON, so it's legacy markdown
            setIsLegacy(true);
        }
    }, [content]);

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
            <h3 className="cs-title">{data.title}</h3>

            <div className="cs-tabs-nav">
                {data.tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`cs-tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        {tab.label}
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
                        <MarkdownRenderer content={tab.content} />
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CheatSheetRenderer;
