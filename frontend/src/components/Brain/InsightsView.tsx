import React from 'react';
import { FaBolt } from 'react-icons/fa';
import type { Insight, Action } from './types';

interface InsightsViewProps {
    insights: Insight[];
    isLoading: boolean;
    onExecuteAction: (action: Action) => void;
}

const InsightsView: React.FC<InsightsViewProps> = ({ insights, isLoading, onExecuteAction }) => {
    return (
        <div className="insights-view">
            <h3>Proactive Insights</h3>
            {isLoading ? (
                <div className="loading-spinner">Analyzing...</div>
            ) : (
                <div className="insights-list">
                    {insights.length === 0 ? (
                        <div className="no-insights">No critical insights at the moment.</div>
                    ) : (
                        insights.map((insight, idx) => (
                            <div key={idx} className={`insight-card ${insight.priority.toLowerCase()}`}>
                                <div className="insight-header">
                                    <span className="insight-type">{insight.type}</span>
                                    <span className="insight-priority">{insight.priority}</span>
                                </div>
                                <p>{insight.message}</p>
                                {insight.actions && (
                                    <div className="insight-actions">
                                        {insight.actions.map((action, aIdx) => (
                                            <button key={aIdx} className="action-btn" onClick={() => onExecuteAction(action)}>
                                                <FaBolt /> {action.label}
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    );
};

export default InsightsView;
