import React, { useState, useEffect } from 'react';
import './ExplainabilityDashboard.css';
import { FaLightbulb, FaFlask, FaCheck, FaTimes, FaInfoCircle } from 'react-icons/fa';

interface Opportunity {
    id: number;
    type: string;
    description: string;
    payload: any;
    status: string;
    created_at: string;
}



const ExplainabilityDashboard: React.FC = () => {
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchOpportunities();
    }, []);

    const fetchOpportunities = async () => {
        setLoading(true);
    try {
        const response = await fetch('/api/autonomy/optimizations');
        const data = await response.json();
        setOpportunities(data.opportunities || []);
    } catch (error) {
        console.error('Failed to fetch optimizations:', error);
    } finally {
        setLoading(false);
    }
};

const handleAccept = async (id: number) => {
    try {
        const response = await fetch(`/api/autonomy/optimizations/${id}/accept`, {
            method: 'POST'
        });
        const result = await response.json();
        if (result.success) {
            // Remove from list or mark accepted
            setOpportunities(prev => prev.filter(o => o.id !== id));
        }
    } catch (error) {
        console.error('Failed to accept optimization:', error);
    }
};

return (
    <div className="explainability-dashboard">
        <div className="dashboard-section">
            <h3><FaLightbulb /> Optimization Opportunities</h3>
            {loading ? (
                <div className="loading">Scanning system...</div>
            ) : opportunities.length === 0 ? (
                <div className="empty-state">No new optimizations found. System is running efficiently.</div>
            ) : (
                <div className="opportunities-list">
                    {opportunities.map(opp => (
                        <div key={opp.id} className="opportunity-card">
                            <div className="opp-header">
                                <span className={`opp-type ${opp.type}`}>{opp.type}</span>
                                <span className="opp-date">{new Date(opp.created_at).toLocaleDateString()}</span>
                            </div>
                            <p className="opp-desc">{opp.description}</p>
                            <div className="opp-actions">
                                <button className="accept-btn" onClick={() => handleAccept(opp.id)}>
                                    <FaCheck /> Accept
                                </button>
                                <button className="dismiss-btn">
                                    <FaTimes /> Dismiss
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>

        <div className="dashboard-section">
            <h3><FaFlask /> Active Experiments (A/B Tests)</h3>
            <div className="experiments-list">
                {/* Mock Data for Visualization */}
                <div className="experiment-card active">
                    <div className="exp-header">
                        <h4>Flashcard Timing</h4>
                        <span className="exp-status">Running</span>
                    </div>
                    <div className="exp-strategies">
                        <div className="strategy A">
                            <span>A: Morning</span>
                            <div className="progress-bar" style={{ width: '45%' }}>45% Retention</div>
                        </div>
                        <div className="strategy B active">
                            <span>B: Evening (You)</span>
                            <div className="progress-bar" style={{ width: '65%' }}>65% Retention</div>
                        </div>
                    </div>
                    <p className="exp-insight"><FaInfoCircle /> You are currently in the <strong>Evening</strong> group. Early results show this strategy is 20% more effective.</p>
                </div>
            </div>
        </div>
    </div>
);
};

export default ExplainabilityDashboard;
