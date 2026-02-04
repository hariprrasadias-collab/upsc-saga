import React from 'react';
import {
    ResponsiveContainer, Treemap, Tooltip
} from 'recharts';
import './HeatmapRenderer.css';

interface HeatmapData {
    name: string;
    size: number;
    intensity: number; // 0-100, maps to color
    children?: HeatmapData[];
    [key: string]: any; // Index signature for Treemap compatibility
}

interface HeatmapRendererProps {
    content: string | HeatmapData[]; // JSON string or object
    title?: string;
}

const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
        const data = payload[0].payload;
        return (
            <div className="heatmap-tooltip">
                <p className="label">{data.name}</p>
                <p className="value">Volume: {data.size}</p>
                <p className="intensity">Intensity: {data.intensity}%</p>
            </div>
        );
    }
    return null;
};

const CustomizedContent = (props: any) => {
    const { depth, x, y, width, height, name, intensity } = props;

    // Determine color based on intensity (Green -> Red)
    // Low intensity (Safe) -> Green
    // High intensity (Critical/Weak) -> Red
    const getColor = (val: number) => {
        if (val < 30) return '#4caf50'; // Green
        if (val < 60) return '#ffeb3b'; // Yellow
        if (val < 80) return '#ff9800'; // Orange
        return '#f44336'; // Red
    };

    const color = getColor(intensity || 0);

    return (
        <g>
            <rect
                x={x}
                y={y}
                width={width}
                height={height}
                style={{
                    fill: color,
                    stroke: '#fff',
                    strokeWidth: 2 / (depth + 1e-10),
                    strokeOpacity: 1 / (depth + 1e-10),
                }}
            />
            {width > 50 && height > 30 ? (
                <text
                    x={x + width / 2}
                    y={y + height / 2 + 7}
                    textAnchor="middle"
                    fill="#fff"
                    fontSize={12}
                    style={{ textShadow: '0 1px 2px rgba(0,0,0,0.5)' }}
                >
                    {name}
                </text>
            ) : null}
        </g>
    );
};

const HeatmapRenderer: React.FC<HeatmapRendererProps> = ({ content, title }) => {
    let data: HeatmapData[] = [];

    try {
        data = typeof content === 'string' ? JSON.parse(content) : content;
        // Ensure it's an array for Recharts Treemap root
        if (!Array.isArray(data)) {
            data = [data]; // Wrap single root if needed
        }
    } catch (e) {
        console.error("Heatmap Data Error", e);
        return <div className="error-message">🔥 Heatmap Data Invalid</div>;
    }

    return (
        <div className="heatmap-container">
            {title && <h3 className="heatmap-title">{title}</h3>}
            <div className="heatmap-wrapper">
                <ResponsiveContainer width="100%" height={400}>
                    <Treemap
                        data={data}
                        dataKey="size"
                        stroke="#fff"
                        fill="#8884d8"
                        content={<CustomizedContent />}
                    >
                        <Tooltip content={<CustomTooltip />} />
                    </Treemap>
                </ResponsiveContainer>
            </div>
            <div className="heatmap-legend">
                <div className="legend-item"><span style={{background: '#4caf50'}}></span> Safe</div>
                <div className="legend-item"><span style={{background: '#ffeb3b'}}></span> Monitor</div>
                <div className="legend-item"><span style={{background: '#ff9800'}}></span> Risk</div>
                <div className="legend-item"><span style={{background: '#f44336'}}></span> Critical</div>
            </div>
        </div>
    );
};

export default HeatmapRenderer;
