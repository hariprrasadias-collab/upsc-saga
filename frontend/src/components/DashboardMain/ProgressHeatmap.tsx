import React, { useState, useEffect } from 'react';
import './ProgressHeatmap.css';

interface HeatmapData {
    date: string;
    intensity: number;
    study_hours: number;
    activities: number;
}

const ProgressHeatmap: React.FC = () => {
    const [heatmapData, setHeatmapData] = useState<HeatmapData[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchHeatmapData();
    }, []);

    const fetchHeatmapData = async () => {
        try {
            const res = await fetch('/api/analytics/visualizations/heatmap?days=90');
            const data = await res.json();

            // Ensure data is an array
            if (Array.isArray(data)) {
                setHeatmapData(data);
            } else {
                console.error('Heatmap data is not an array:', data);
                setHeatmapData([]);
            }
            setLoading(false);
        } catch (err) {
            console.error('Failed to fetch heatmap data:', err);
            setHeatmapData([]);
            setLoading(false);
        }
    };

    const getIntensityColor = (intensity: number) => {
        // GitHub-style green gradient
        if (intensity === 0) return '#161b22';
        if (intensity <= 2) return '#0e4429';
        if (intensity <= 4) return '#006d32';
        if (intensity <= 6) return '#26a641';
        if (intensity <= 8) return '#39d353';
        return '#d4a574'; // Gold for very high activity
    };

    const groupByWeek = (data: HeatmapData[]) => {
        const weeks: HeatmapData[][] = [];
        let currentWeek: HeatmapData[] = [];

        // Fill in missing days with 0 intensity
        const today = new Date();
        const startDate = new Date(today.getTime() - (90 * 24 * 60 * 60 * 1000));

        for (let d = new Date(startDate); d <= today; d.setDate(d.getDate() + 1)) {
            const dateStr = d.toISOString().split('T')[0];
            const existing = data.find(item => item.date === dateStr);

            if (existing) {
                currentWeek.push(existing);
            } else {
                currentWeek.push({
                    date: dateStr,
                    intensity: 0,
                    study_hours: 0,
                    activities: 0
                });
            }

            if (currentWeek.length === 7) {
                weeks.push([...currentWeek]);
                currentWeek = [];
            }
        }

        if (currentWeek.length > 0) {
            weeks.push(currentWeek);
        }

        return weeks;
    };

    if (loading) return <div className="heatmap-loading">Loading heatmap...</div>;

    const weeks = groupByWeek(heatmapData);

    // Handle empty data
    if (weeks.length === 0 || heatmapData.length === 0) {
        return (
            <div className="progress-heatmap">
                <h3>📅 Activity Heatmap (Last 90 Days)</h3>
                <div className="heatmap-container">
                    <p style={{ textAlign: 'center', color: '#7d8590', padding: '2rem' }}>
                        No activity data yet. Start studying to see your progress!
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="progress-heatmap">
            <h3>📅 Activity Heatmap (Last 90 Days)</h3>
            <div className="heatmap-container">
                <div className="heatmap-grid">
                    {weeks.map((week, weekIdx) => (
                        <div key={weekIdx} className="heatmap-week">
                            {week.map((day, dayIdx) => (
                                <div
                                    key={dayIdx}
                                    className="heatmap-day"
                                    style={{ backgroundColor: getIntensityColor(day.intensity) }}
                                    title={`${day.date}\n${day.study_hours}h studied\n${day.activities} activities\nIntensity: ${day.intensity}/10`}
                                >
                                </div>
                            ))}
                        </div>
                    ))}
                </div>
                <div className="heatmap-legend">
                    <span className="legend-label">Less</span>
                    {[0, 2, 4, 6, 8, 10].map(intensity => (
                        <div
                            key={intensity}
                            className="legend-box"
                            style={{ backgroundColor: getIntensityColor(intensity) }}
                        ></div>
                    ))}
                    <span className="legend-label">More</span>
                </div>
            </div>
        </div>
    );
};

export default ProgressHeatmap;
