import React from 'react';
import './SelfReviewRenderer.css';

interface SelfReviewData {
    week: string;
    stats: {
        total: number;
        success_rate: number;
        avg_impact: number;
    };
    improvement_plan: {
        plan: string[];
    };
    review_id?: number;
}

interface SelfReviewRendererProps {
    content: string | SelfReviewData;
}

const SelfReviewRenderer: React.FC<SelfReviewRendererProps> = ({ content }) => {
    let data: SelfReviewData;

    try {
        let parsed = typeof content === 'string' ? JSON.parse(content) : content;

        // Handle error objects
        if (parsed && parsed.error) {
            return <div className="error-message" style={{ textAlign: 'center', padding: '30px' }}>⚠️ {parsed.error}: Review data not available. Try regenerating.</div>;
        }

        // Unwrap debug envelope
        if (parsed && parsed.response_text && !parsed.week) {
            let inner = parsed.response_text;
            const jsonMatch = inner.match(/```json\s*\n?([\s\S]*?)\n?```/);
            if (jsonMatch) inner = jsonMatch[1].trim();
            try { parsed = JSON.parse(inner); } catch { }
        }

        data = parsed;
    } catch (e) {
        console.error("SelfReview Data Error", e);
        return <div className="error-message">📋 Review Data Corrupted</div>;
    }

    const { week, stats, improvement_plan } = data;

    return (
        <div className="self-review-container">
            <header className="review-header">
                <h2>📈 Weekly System Review</h2>
                <span className="review-week">{week}</span>
            </header>

            <div className="metrics-grid">
                <div className="metric-card">
                    <span className="metric-val">{stats.total}</span>
                    <span className="metric-label">Actions</span>
                </div>
                <div className="metric-card">
                    <span className={`metric-val ${stats.success_rate >= 80 ? 'good' : 'bad'}`}>
                        {stats.success_rate.toFixed(1)}%
                    </span>
                    <span className="metric-label">Success Rate</span>
                </div>
                <div className="metric-card">
                    <span className="metric-val">{stats.avg_impact.toFixed(2)}</span>
                    <span className="metric-label">Avg. Impact</span>
                </div>
            </div>

            <div className="improvement-section">
                <h3>🚀 Strategic Improvement Plan</h3>
                <ul className="plan-list">
                    {improvement_plan.plan?.map((item, idx) => (
                        <li key={idx} className="plan-item">
                            <span className="item-idx">{idx + 1}</span>
                            <span className="item-text">{item}</span>
                        </li>
                    )) || <li>No improvements suggested. System nominal.</li>}
                </ul>
            </div>

            <div className="review-footer">
                <p>Generated autonomously by the Brain's Self-Reflection Module.</p>
            </div>
        </div>
    );
};

export default SelfReviewRenderer;
