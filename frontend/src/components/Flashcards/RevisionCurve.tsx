import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './RevisionCurve.css';

interface CurveData {
    interval: string;
    retention: number;
    reviews: number;
}

const RevisionCurve: React.FC = () => {
    const [curveData, setCurveData] = useState<CurveData[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchCurveData();
    }, []);

    const fetchCurveData = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/analytics/visualizations/revision-curve`);
            const data = await res.json();

            if (Array.isArray(data)) {
                setCurveData(data);
            } else {
                console.error('Revision curve data is not an array:', data);
                setCurveData([]);
            }
            setLoading(false);
        } catch (err) {
            console.error('Failed to fetch revision curve:', err);
            setCurveData([]);
            setLoading(false);
        }
    };

    if (loading) return <div className="curve-loading">Loading revision curve...</div>;

    if (curveData.length === 0) {
        return (
            <div className="revision-curve">
                <h3>📈 Revision Effectiveness Curve</h3>
                <div className="curve-container">
                    <p className="no-data">
                        Complete some flashcard reviews to see your retention curve!
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="revision-curve">
            <h3>📈 Revision Effectiveness Curve</h3>
            <p className="curve-description">
                This shows how well you retain information over time. Higher retention = better memory!
            </p>
            <div className="curve-container">
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={curveData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                        <XAxis
                            dataKey="interval"
                            stroke="#7d8590"
                            label={{ value: 'Days Since Last Review', position: 'insideBottom', offset: -5, fill: '#7d8590' }}
                        />
                        <YAxis
                            stroke="#7d8590"
                            domain={[0, 100]}
                            label={{ value: 'Retention Rate (%)', angle: -90, position: 'insideLeft', fill: '#7d8590' }}
                        />
                        <Tooltip
                            contentStyle={{
                                background: '#161b22',
                                border: '1px solid #30363d',
                                borderRadius: '6px',
                                color: '#d4a574'
                            }}
                            formatter={(value: any, name: any) => {
                                if (name === 'retention') return [`${value}%`, 'Retention Rate'];
                                if (name === 'reviews') return [value, 'Review Count'];
                                return [value, name ? String(name) : ''];
                            }}
                        />
                        <Legend
                            wrapperStyle={{ color: '#7d8590' }}
                        />
                        <Line
                            type="monotone"
                            dataKey="retention"
                            stroke="#d4a574"
                            strokeWidth={3}
                            dot={{ fill: '#d4a574', r: 5 }}
                            activeDot={{ r: 7 }}
                            name="Retention Rate"
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            <div className="curve-insights">
                <div className="insight-card">
                    <span className="insight-icon">💡</span>
                    <div className="insight-content">
                        <strong>Tip:</strong> Review cards before retention drops below 70% for optimal learning.
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RevisionCurve;
