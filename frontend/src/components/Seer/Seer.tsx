// /frontend/src/components/Seer/Seer.tsx
import React, { useEffect, useState } from 'react';
import './Seer.css';
import {
    Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip
} from 'recharts';

interface SeerData {
    radar_data: Array<{ subject: string; A: number }>;
    xp_history: Array<{ date: string; xp: number }>;
}

const Seer: React.FC = () => {
    const [data, setData] = useState<SeerData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('http://localhost:5000/api/seer')
            .then(res => res.json())
            .then(d => {
                setData(d);
                setLoading(false);
            })
            .catch(err => console.error("The pool is clouded...", err));
    }, []);

    if (loading) return <div style={{ color: '#7fdbff', textAlign: 'center', marginTop: '50px' }}>Gazing into the waters...</div>;

    return (
        <div className="seer-container">
            <div className="seer-header">
                <h1 className="seer-title">THE SEER'S POOL</h1>
                <p className="seer-subtitle">"Know thyself, and the war is half won."</p>
            </div>

            <div className="seer-grid">
                {/* CHART 1: SUBJECT BALANCE (RADAR) */}
                <div className="seer-card">
                    <h3>Warrior's Balance</h3>
                    <div style={{ width: '100%', height: 300 }}>
                        <ResponsiveContainer>
                            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data?.radar_data}>
                                <PolarGrid stroke="#3a6e85" />
                                <PolarAngleAxis dataKey="subject" tick={{ fill: '#7fdbff', fontSize: 12 }} />
                                <PolarRadiusAxis angle={30} domain={[0, 'auto']} tick={false} axisLine={false} />
                                <Radar
                                    name="Proficiency"
                                    dataKey="A"
                                    stroke="#7fdbff"
                                    fill="#7fdbff"
                                    fillOpacity={0.4}
                                />
                            </RadarChart>
                        </ResponsiveContainer>
                    </div>
                    <p style={{ textAlign: 'center', fontSize: '0.9rem', color: '#aaa', marginTop: '10px' }}>
                        Shows your focus distribution across GS Papers.
                    </p>
                </div>

                {/* CHART 2: CONSISTENCY (AREA) */}
                <div className="seer-card">
                    <h3>Tides of Effort (XP)</h3>
                    <div style={{ width: '100%', height: 300 }}>
                        <ResponsiveContainer>
                            <AreaChart data={data?.xp_history}>
                                <defs>
                                    <linearGradient id="colorXp" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#7fdbff" stopOpacity={0.8} />
                                        <stop offset="95%" stopColor="#7fdbff" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <XAxis dataKey="date" stroke="#3a6e85" tick={{ fill: '#aaa' }} />
                                <YAxis stroke="#3a6e85" tick={{ fill: '#aaa' }} />
                                <CartesianGrid strokeDasharray="3 3" stroke="#1a3a4a" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#001f3f', borderColor: '#7fdbff', color: '#fff' }}
                                    itemStyle={{ color: '#7fdbff' }}
                                />
                                <Area type="monotone" dataKey="xp" stroke="#7fdbff" fillOpacity={1} fill="url(#colorXp)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                    <p style={{ textAlign: 'center', fontSize: '0.9rem', color: '#aaa', marginTop: '10px' }}>
                        Your daily XP gains over the last 7 days.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Seer;