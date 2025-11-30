import React from 'react';

import './FocusAreasPanel.css';

interface WeakArea {
    subject: string;
    topic: string;
    weakness_score: number;
    source: string;
    action: string;
    trend?: 'improving' | 'declining' | 'stable';
    trend_value?: number;
    impact?: 'High' | 'Medium' | 'Low';
    recent_scores?: number[];
    last_attempt?: string;
}

interface FocusAreasPanelProps {
    areas: WeakArea[];
    onNavigate?: (tab: string) => void;
}

const FocusAreasPanel: React.FC<FocusAreasPanelProps> = ({ areas, onNavigate }) => {
    if (!areas || areas.length === 0) {
        return (
            <div className="focus-areas-panel empty">
                <h3>🎯 Focus Areas</h3>
                <div className="no-weak-areas">
                    🎉 Great job! No major weak areas identified.
                </div>
            </div>
        );
    }

    // Group areas by subject
    const groupedAreas = areas.reduce((acc, area) => {
        const subject = area.subject || 'General';
        if (!acc[subject]) {
            acc[subject] = [];
        }
        acc[subject].push(area);
        return acc;
    }, {} as Record<string, WeakArea[]>);

    return (
        <div className="focus-areas-panel">
            <h3>🎯 Focus Areas (Subject-wise)</h3>

            <div className="subject-groups">
                {Object.entries(groupedAreas).map(([subject, subjectAreas]) => (
                    <div key={subject} className="subject-group">
                        <h4 className="subject-title">{subject}</h4>
                        <div className="focus-grid">
                            {subjectAreas.map((area, idx) => (
                                <div key={idx} className="focus-card">
                                    <div className="focus-header">
                                        <span className="focus-topic">{area.topic}</span>
                                        <button
                                            className="action-btn"
                                            onClick={() => onNavigate?.('weak-areas')}
                                        >
                                            Take Action
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default FocusAreasPanel;
