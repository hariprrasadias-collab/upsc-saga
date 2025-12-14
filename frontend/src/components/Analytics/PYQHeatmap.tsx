import React, { useEffect, useState } from 'react';
import { ResponsiveContainer, Treemap, Tooltip } from 'recharts';
import './Analytics.css'; // Assuming we can reuse existing analytics styles
import { API_BASE_URL } from '../../config';

interface HeatmapData {
    name: string;
    size: number;
    children?: HeatmapData[];
}

const PYQHeatmap: React.FC = () => {
    const [data, setData] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAnalytics = async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/pyq/analytics`);
                const rawData = await res.json();

                // Transform data for Treemap (Hierarchical: Subject > Topic)
                // Since the API returns flat subject/topic counts, we'll improvise a structure
                // Ideally, the backend should return a hierarchical structure.
                // For now, let's map the 'by_subject' data to the root level.

                const treeData: HeatmapData[] = rawData.by_subject.map((s: any) => ({
                    name: s.subject,
                    size: s.count,
                }));

                setData(treeData);
            } catch (err) {
                console.error("Failed to load heatmap data", err);
            } finally {
                setLoading(false);
            }
        };

        fetchAnalytics();
    }, []);

    const CustomContent = (props: any) => {
        const { depth, x, y, width, height, name } = props;

        return (
            <g>
                <rect
                    x={x}
                    y={y}
                    width={width}
                    height={height}
                    style={{
                        fill: depth < 2 ? '#3498db' : 'none',
                        stroke: '#fff',
                        strokeWidth: 2 / (depth + 1e-10),
                        strokeOpacity: 1 / (depth + 1e-10),
                        opacity: 0.8
                    }}
                />
                {depth === 1 ? (
                    <text
                        x={x + width / 2}
                        y={y + height / 2 + 7}
                        textAnchor="middle"
                        fill="#fff"
                        fontSize={14}
                    >
                        {name}
                    </text>
                ) : null}
            </g>
        );
    };

    if (loading) return <div>Loading Heatmap...</div>;

    return (
        <div className="heatmap-container" style={{ width: '100%', height: '500px', background: '#2c3e50', borderRadius: '8px', padding: '10px' }}>
            <h3 style={{ color: 'white', textAlign: 'center', marginBottom: '10px' }}>Tactical Topic Distribution</h3>
            <ResponsiveContainer width="100%" height="90%">
                <Treemap
                    width={400}
                    height={200}
                    data={data}
                    dataKey="size"
                    aspectRatio={4 / 3}
                    stroke="#fff"
                    fill="#8884d8"
                    content={<CustomContent />}
                >
                    <Tooltip contentStyle={{ backgroundColor: '#333', borderColor: '#555', color: '#fff' }} />
                </Treemap>
            </ResponsiveContainer>
        </div>
    );
};

export default PYQHeatmap;
