import React from 'react';
import './Renderers.css';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';

interface CheatSheetProps {
    content: string;
}

const CheatSheetRenderer: React.FC<CheatSheetProps> = ({ content }) => {
    // Heuristic: Split by "##" or lines that look like headers
    const sections = content.split(/^##\s+/m).filter(s => s.trim().length > 0);

    return (
        <div className="cheat-sheet-grid">
            {sections.map((sec, idx) => {
                const lines = sec.split('\n');
                const title = lines[0].trim();
                const body = lines.slice(1).join('\n').trim();

                return (
                    <div key={idx} className="cheat-sheet-card glass-card">
                        <h3 className="cheat-title">{title || "Notes"}</h3>
                        <div className="cheat-body">
                            <MarkdownRenderer content={body} />
                        </div>
                    </div>
                );
            })}
            {/* Fallback if no sections detected */}
            {sections.length === 0 && (
                <div className="cheat-sheet-card glass-card full-width">
                    <MarkdownRenderer content={content} />
                </div>
            )}
        </div>
    );
};

export default CheatSheetRenderer;
