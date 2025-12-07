import React, { useEffect, useState } from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';

interface DifficultyData {
    year: number;
    Easy: number;
    Medium: number;
    Hard: number;
}

interface DifficultyTrendChartProps {
    data: any[]; // Raw data from backend
}

const DifficultyTrendChart: React.FC<DifficultyTrendChartProps> = ({ data }) => {
    const [chartData, setChartData] = useState<DifficultyData[]>([]);

    useEffect(() => {
        if (!data) return;

        // Transform flat SQL data (year, difficulty, count) into Chart format (year, Easy, Medium, Hard)
        const transformed: Record<number, DifficultyData> = {};

        data.forEach(item => {
            const year = item.year;
            if (!transformed[year]) {
                transformed[year] = { year, Easy: 0, Medium: 0, Hard: 0 };
            }
            // Normalize difficulty string just in case
            const diff = item.difficulty ? item.difficulty.charAt(0).toUpperCase() + item.difficulty.slice(1).toLowerCase() : 'Medium';
            if (diff in transformed[year]) {
                // @ts-ignore
                transformed[year][diff] = item.count;
            }
        });

        // Convert to sorted array
        const result = Object.values(transformed).sort((a, b) => a.year - b.year);
        setChartData(result);

    }, [data]);

    return (
        <div className="trend-chart-container" style={{ width: '100%', height: '300px', background: '#2c3e50', borderRadius: '8px', padding: '10px', marginTop: '20px' }}>
            <h4 style={{ color: 'white', textAlign: 'center', margin: '0 0 10px 0' }}>Difficulty Escalation Matrix</h4>
            <ResponsiveContainer width="100%" height="90%">
                <BarChart data={chartData}>
                    <XAxis dataKey="year" stroke="#ecf0f1" />
                    <YAxis stroke="#ecf0f1" />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#34495e', border: 'none', color: '#ecf0f1' }}
                        itemStyle={{ color: '#ecf0f1' }}
                    />
                    <Legend />
                    <Bar dataKey="Easy" stackId="a" fill="#2ecc71" />
                    <Bar dataKey="Medium" stackId="a" fill="#f1c40f" />
                    <Bar dataKey="Hard" stackId="a" fill="#e74c3c" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

export default DifficultyTrendChart;
