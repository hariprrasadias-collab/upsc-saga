import React from 'react';
import {
    ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ZAxis
} from 'recharts';

interface PerformanceScatterProps {
    data: any[];
}

const PerformanceScatter: React.FC<PerformanceScatterProps> = ({ data }) => {
    if (!data || data.length === 0) return <div>No data available</div>;

    return (
        <div className="chart-container scatter-container">
            <h3>Speed vs. Accuracy</h3>
            <ResponsiveContainer width="100%" height={300}>
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#4a5568" />
                    <XAxis
                        type="number"
                        dataKey="time_per_question"
                        name="Time (sec)"
                        unit="s"
                        stroke="#ecf0f1"
                        label={{ value: 'Time per Question', position: 'insideBottom', offset: -10, fill: '#95a5a6' }}
                    />
                    <YAxis
                        type="number"
                        dataKey="accuracy"
                        name="Accuracy"
                        unit="%"
                        stroke="#ecf0f1"
                        label={{ value: 'Accuracy', angle: -90, position: 'insideLeft', fill: '#95a5a6' }}
                    />
                    <ZAxis type="number" dataKey="count" range={[50, 400]} name="Questions" />
                    <Tooltip
                        cursor={{ strokeDasharray: '3 3' }}
                        contentStyle={{ backgroundColor: '#2c3e50', border: 'none', color: '#ecf0f1' }}
                    />
                    <Scatter name="Performance" data={data} fill="#e74c3c" />
                </ScatterChart>
            </ResponsiveContainer>
        </div>
    );
};

export default PerformanceScatter;
