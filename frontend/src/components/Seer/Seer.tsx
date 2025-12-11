import React, { useEffect, useState } from 'react';
import './Seer.css';
import {
    Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
    PieChart, Pie, Cell, BarChart, Bar, Legend
} from 'recharts';

interface SeerData {
    radar_data: Array<{ subject: string; A: number }>;
    xp_history: Array<{ date: string; xp: number }>;
}

interface WeightageData {
    subject: string;
    count: number;
}

interface TrendData {
    year: number;
    [key: string]: number;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

const Seer: React.FC = () => {
    const [data, setData] = useState<SeerData | null>(null);
    const [weightage, setWeightage] = useState<WeightageData[]>([]);
    const [trends, setTrends] = useState<TrendData[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [seerRes, weightRes, trendRes] = await Promise.all([
                    fetch('/api/seer'),
                    fetch('/api/seer/weightage'),
                    fetch('/api/seer/trends')
                ]);

                const seerData = await seerRes.json();
                const weightData = await weightRes.json();
                const trendData = await trendRes.json();

                setData(seerData);
                setWeightage(weightData);
                setTrends(trendData);
                setLoading(false);
            } catch (err) {
                console.error("The pool is clouded...", err);
            }
        };

        fetchData();
    }, []);

    // Helper: Get top N subjects, group rest as "Others"
    const getTopSubjects = (data: WeightageData[], topN: number = 6) => {
        if (data.length <= topN) return data;

        const sorted = [...data].sort((a, b) => b.count - a.count);
        const top = sorted.slice(0, topN);
        const others = sorted.slice(topN);

        if (others.length > 0) {
            const othersSum = others.reduce((sum, item) => sum + item.count, 0);
            top.push({ subject: 'Others', count: othersSum });
        }

        return top;
    };

    // Helper: Get top subjects for trends
    const getTopTrendSubjects = (trendsData: TrendData[], topN: number = 6): string[] => {
        if (trendsData.length === 0) return [];

        const subjectTotals: { [key: string]: number } = {};
        trendsData.forEach(yearData => {
            Object.keys(yearData).forEach(key => {
                if (key !== 'year') {
                    subjectTotals[key] = (subjectTotals[key] || 0) + yearData[key];
                }
            });
        });

        return Object.entries(subjectTotals)
            .sort((a, b) => b[1] - a[1])
            .slice(0, topN)
            .map(([subject]) => subject);
    };

    if (loading) return <div style={{ color: '#7fdbff', textAlign: 'center', marginTop: '50px' }}>Gazing into the waters...</div>;

    const topWeightage = getTopSubjects(weightage, 6);
    const topTrendSubjects = getTopTrendSubjects(trends, 6);

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
                    <div style={{ width: '100%', height: 300, minWidth: 0 }}>
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
                    <p className="chart-desc">Shows your focus distribution across GS Papers.</p>
                </div>

                {/* CHART 2: CONSISTENCY (AREA) */}
                <div className="seer-card">
                    <h3>Tides of Effort (XP)</h3>
                    <div style={{ width: '100%', height: 300, minWidth: 0 }}>
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
                    <p className="chart-desc">Your daily XP gains over the last 7 days.</p>
                </div>

                {/* CHART 3: SUBJECT WEIGHTAGE (PIE) - Simplified */}
                <div className="seer-card">
                    <h3>The Weight of Knowledge</h3>
                    <div style={{ width: '100%', height: 380, minWidth: 0 }}>
                        <ResponsiveContainer>
                            <PieChart>
                                <Pie
                                    data={topWeightage as any}
                                    cx="50%"
                                    cy="42%"
                                    labelLine={true}
                                    label={({ subject, percent }: any) => `${subject}: ${((percent || 0) * 100).toFixed(0)}%`}
                                    outerRadius={95}
                                    fill="#8884d8"
                                    dataKey="count"
                                    nameKey="subject"
                                >
                                    {topWeightage.map((_, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#001f3f', borderColor: '#7fdbff', color: '#fff' }}
                                    formatter={(value: number, name: string) => [value, name]}
                                />
                                <Legend
                                    verticalAlign="bottom"
                                    height={60}
                                    wrapperStyle={{ paddingTop: '10px' }}
                                    iconType="circle"
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                    <p className="chart-desc">Top 6 subjects in Archives{topWeightage.length > 6 && ' (+ Others group)'}.</p>
                </div>

                {/* CHART 4: YEARLY TRENDS (BAR) - Simplified */}
                <div className="seer-card wide">
                    <h3>Chronicles of the Past</h3>
                    <div style={{ width: '100%', height: 380, minWidth: 0 }}>
                        <ResponsiveContainer>
                            <BarChart data={trends}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1a3a4a" />
                                <XAxis dataKey="year" stroke="#3a6e85" tick={{ fill: '#aaa' }} />
                                <YAxis stroke="#3a6e85" tick={{ fill: '#aaa' }} />
                                <Tooltip contentStyle={{ backgroundColor: '#001f3f', borderColor: '#7fdbff', color: '#fff' }} />
                                <Legend
                                    wrapperStyle={{ paddingTop: '10px' }}
                                    iconType="rect"
                                />
                                {topTrendSubjects.map((subject, index) => (
                                    <Bar
                                        key={subject}
                                        dataKey={subject}
                                        stackId="a"
                                        fill={COLORS[index % COLORS.length]}
                                    />
                                ))}
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <p className="chart-desc">Year-wise breakdown of top 6 subjects.</p>
                </div>
            </div>
        </div>
    );
};

export default Seer;