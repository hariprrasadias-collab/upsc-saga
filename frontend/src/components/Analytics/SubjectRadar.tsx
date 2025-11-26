import React from 'react';
import {
    RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    Tooltip, Legend, ResponsiveContainer
} from 'recharts';

interface SubjectRadarProps {
    data: any[];
}

const SubjectRadar: React.FC<SubjectRadarProps> = ({ data }) => {
    if (!data || data.length === 0) return <div>No data available</div>;

    return (
        <div className="chart-container radar-container">
            <h3>Subject Performance</h3>
            <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={data}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="subject" stroke="#ecf0f1" />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="#95a5a6" />
                    <Radar
                        name="Mock Avg"
                        dataKey="mock_avg"
                        stroke="#3498db"
                        fill="#3498db"
                        fillOpacity={0.6}
                    />
                    <Radar
                        name="Answer Avg"
                        dataKey="answer_avg"
                        stroke="#2ecc71"
                        fill="#2ecc71"
                        fillOpacity={0.6}
                    />
                    <Radar
                        name="Syllabus %"
                        dataKey="syllabus_pct"
                        stroke="#9b59b6"
                        fill="#9b59b6"
                        fillOpacity={0.6}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#2c3e50', border: 'none', color: '#ecf0f1' }}
                        itemStyle={{ color: '#ecf0f1' }}
                    />
                    <Legend />
                </RadarChart>
            </ResponsiveContainer>
        </div>
    );
};

export default SubjectRadar;
