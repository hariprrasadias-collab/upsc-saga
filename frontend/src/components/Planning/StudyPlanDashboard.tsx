import React, { useState, useEffect } from 'react';
import './StudyPlanDashboard.css';
import FlashcardsManager from '../Flashcards/FlashcardsManager';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer,
    PieChart, Pie, Cell,
    Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts';

interface Slot {
    id: number;
    time: string;
    subject: string;
    activity: string;
    status: 'pending' | 'completed' | 'skipped' | 'rescheduled';
    resource_link?: string;
}

interface DayPlan {
    date: string;
    day: string;
    slots: Slot[];
}

type ViewMode = 'daily' | 'weekly' | 'monthly' | 'yearly' | 'overall' | 'flashcards';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

const StudyPlanDashboard: React.FC = () => {
    const [plan, setPlan] = useState<DayPlan[]>([]);
    const [loading, setLoading] = useState(false);
    const [viewMode, setViewMode] = useState<ViewMode>('daily');
    const [selectedTask, setSelectedTask] = useState<Slot | null>(null);

    useEffect(() => {
        fetchCSVPlan();
    }, []);

    const fetchCSVPlan = async () => {
        setLoading(true);
        try {
            const response = await fetch('/UPSC_Scheduler.csv');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const csvText = await response.text();
            const parsedPlan = parseCSV(csvText);
            setPlan(parsedPlan);
        } catch (err) {
            console.error("Failed to fetch CSV plan:", err);
        } finally {
            setLoading(false);
        }
    };

    const parseCSV = (csvText: string): DayPlan[] => {
        const lines = csvText.split('\n').filter(line => line.trim() !== '');
        // Skip headers
        const dataRows = lines.slice(1);

        const dayMap: { [key: string]: DayPlan } = {};
        const completedTasks = new Set(JSON.parse(localStorage.getItem('completedTasks') || '[]'));

        dataRows.forEach((row, index) => {
            // Simple split for now as data seems simple and doesn't contain quoted commas in our generation script
            const columns = row.split(',').map(c => c.trim());

            // Date,Day,Slot_Type,Time,Subject,Topic,Activity_Type,Resources
            const date = columns[0];
            const dayName = columns[1];
            const time = columns[3];
            const subject = columns[4];
            const topic = columns[5];
            const activityType = columns[6];
            const resources = columns[7];

            if (!date || columns.length < 5) return;

            if (!dayMap[date]) {
                dayMap[date] = {
                    date: date,
                    day: dayName,
                    slots: []
                };
            }

            const taskId = index + 1;
            const isCompleted = completedTasks.has(taskId);

            dayMap[date].slots.push({
                id: taskId,
                time: time,
                subject: subject,
                activity: `${topic} (${activityType})`,
                status: isCompleted ? 'completed' : 'pending',
                resource_link: resources !== 'N/A' ? resources : undefined
            });
        });

        return Object.values(dayMap).sort((a, b) => a.date.localeCompare(b.date));
    };

    const handleTaskClick = (slot: Slot) => {
        setSelectedTask(slot);
    };

    const closeModal = () => {
        setSelectedTask(null);
    };

    const toggleTaskStatus = async (task: Slot) => {
        const newStatus: 'pending' | 'completed' | 'skipped' | 'rescheduled' = task.status === 'completed' ? 'pending' : 'completed';

        // Optimistic Update
        const updatedPlan = plan.map(day => ({
            ...day,
            slots: day.slots.map(s => s.id === task.id ? { ...s, status: newStatus } : s)
        }));
        setPlan(updatedPlan);

        if (selectedTask && selectedTask.id === task.id) {
            setSelectedTask({ ...selectedTask, status: newStatus });
        }

        // Persist to LocalStorage
        const completedTasks = new Set(JSON.parse(localStorage.getItem('completedTasks') || '[]'));
        if (newStatus === 'completed') {
            completedTasks.add(task.id);
        } else {
            completedTasks.delete(task.id);
        }
        localStorage.setItem('completedTasks', JSON.stringify(Array.from(completedTasks)));
    };

    // Analytics Helpers
    const getWeeklyAnalytics = (weekSlots: Slot[]) => {
        const subjectCounts: { [key: string]: number } = {};
        weekSlots.forEach(slot => {
            if (slot.subject === 'Break' || slot.subject === 'Buffer') return;
            subjectCounts[slot.subject] = (subjectCounts[slot.subject] || 0) + 1;
        });

        const data = Object.entries(subjectCounts).map(([name, value]) => ({ name, value }));
        data.sort((a, b) => b.value - a.value);

        const totalStudySlots = weekSlots.filter(s => s.subject !== 'Break').length;
        const focusSubject = data.length > 0 ? data[0].name : 'General';

        return { data, totalStudySlots, focusSubject };
    };

    const getMonthlyAnalytics = (monthSlots: Slot[]) => {
        const total = monthSlots.length;
        const completed = monthSlots.filter(s => s.status === 'completed').length;
        const consistency = total > 0 ? Math.round((completed / total) * 100) : 0;

        // Determine Phase (Mock logic based on dates or content)
        // For now, simple date check or just "Phase 1"
        const phase = "Phase 1: Foundation";

        return { consistency, phase };
    };

    const renderContent = () => {
        if (viewMode === 'flashcards') {
            return <FlashcardsManager />;
        } else if (viewMode === 'daily') {
            return plan.map((day, idx) => (
                <div key={idx} className="day-card">
                    <div className="day-header">
                        <span className="day-date">{day.date}</span>
                        <span className="day-name">{day.day}</span>
                    </div>
                    <div className="day-slots">
                        {day.slots.length > 0 ? (
                            day.slots.map((slot, sIdx) => (
                                <div
                                    key={sIdx}
                                    className={`slot-card ${slot.subject.toLowerCase().replace(/\s+/g, '-')}`}
                                    onClick={() => handleTaskClick(slot)}
                                >
                                    <div className={`slot-status ${slot.status}`} title={slot.status}></div>
                                    <div className="slot-time">{slot.time}</div>
                                    <div className="slot-subject">{slot.subject}</div>
                                    <div className="slot-activity">{slot.activity}</div>
                                    {slot.resource_link && (
                                        <div className="resource-link">🔗 {slot.resource_link}</div>
                                    )}
                                </div>
                            ))
                        ) : (
                            <div className="no-slots">Rest Day / Buffer</div>
                        )}
                    </div>
                </div>
            ));
        } else if (viewMode === 'weekly') {
            // Group by Week (assuming plan starts on start_date)
            const weeks: DayPlan[][] = [];
            let currentWeek: DayPlan[] = [];

            plan.forEach((day, i) => {
                currentWeek.push(day);
                if ((i + 1) % 7 === 0 || i === plan.length - 1) {
                    weeks.push(currentWeek);
                    currentWeek = [];
                }
            });

            return weeks.map((week, idx) => {
                const weekSlots = week.flatMap(d => d.slots);
                const { data, totalStudySlots, focusSubject } = getWeeklyAnalytics(weekSlots);
                const completed = week.reduce((acc, day) => acc + day.slots.filter(s => s.status === 'completed').length, 0);
                const totalTasks = week.reduce((acc, day) => acc + day.slots.length, 0);
                const progress = totalTasks > 0 ? (completed / totalTasks) * 100 : 0;
                const startDate = week[0].date;
                const endDate = week[week.length - 1].date;

                // Insight Logic
                let insight = "Maintain steady pace.";
                if (totalStudySlots > 40) insight = "⚠️ Heavy Load: Prioritize sleep & recovery.";
                else if (focusSubject === 'History') insight = "📜 History Week: Use timelines for better retention.";
                else if (focusSubject === 'Polity') insight = "⚖️ Polity Focus: Review relevant articles daily.";
                else if (progress > 90) insight = "🔥 Crushing it! Consider an extra mock test.";

                return (
                    <div key={idx} className="mission-card">
                        <div className="mission-header">
                            <div className="mission-title">
                                <h3>MISSION {idx + 1}</h3>
                                <span>{startDate} - {endDate}</span>
                            </div>
                            <div className="mission-status">
                                <span className="status-label">{progress === 100 ? 'COMPLETE' : 'IN PROGRESS'}</span>
                                <div className="circular-progress" style={{ background: `conic-gradient(#2ecc71 ${progress}%, #333 ${progress}%)` }}>
                                    <span>{Math.round(progress)}%</span>
                                </div>
                            </div>
                        </div>

                        <div className="mission-body">
                            <div className="mission-intel">
                                <h4>INTEL BRIEF</h4>
                                <p>{insight}</p>
                                <div className="key-stats">
                                    <div className="stat-box">
                                        <label>FOCUS</label>
                                        <span>{focusSubject}</span>
                                    </div>
                                    <div className="stat-box">
                                        <label>LOAD</label>
                                        <span>{totalStudySlots} Slots</span>
                                    </div>
                                </div>
                            </div>

                            <div className="mission-radar">
                                <h4>SUBJECT DISTRIBUTION</h4>
                                <ResponsiveContainer width="100%" height={150}>
                                    <BarChart data={data} layout="vertical" margin={{ left: 40, right: 20 }}>
                                        <XAxis type="number" hide />
                                        <YAxis dataKey="name" type="category" width={80} tick={{ fill: '#bdc3c7', fontSize: 10 }} />
                                        <RechartsTooltip contentStyle={{ background: '#1e1e1e', border: 'none' }} />
                                        <Bar dataKey="value" fill="#3498db" radius={[0, 4, 4, 0]}>
                                            {data.map((_, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                );
            });
        } else if (viewMode === 'monthly') {
            // Group by Month
            const months: { [key: string]: DayPlan[] } = {};
            plan.forEach(day => {
                const monthKey = day.date.substring(0, 7); // YYYY-MM
                if (!months[monthKey]) months[monthKey] = [];
                months[monthKey].push(day);
            });

            return Object.entries(months).map(([month, days]) => {
                const { consistency, phase } = getMonthlyAnalytics(days.flatMap(d => d.slots));

                // Calculate Subject Distribution for Pie Chart
                const subjectCounts: { [key: string]: number } = {};
                days.flatMap(d => d.slots).forEach(s => {
                    if (s.subject !== 'Break') subjectCounts[s.subject] = (subjectCounts[s.subject] || 0) + 1;
                });
                const pieData = Object.entries(subjectCounts).map(([name, value]) => ({ name, value }));

                return (
                    <div key={month} className="strategy-card">
                        <div className="strategy-header">
                            <div className="strategy-title">
                                <h3>{new Date(month + '-01').toLocaleString('default', { month: 'long', year: 'numeric' })}</h3>
                                <span className="phase-badge">{phase}</span>
                            </div>
                            <div className="consistency-score">
                                <label>CONSISTENCY</label>
                                <span className={consistency > 80 ? 'high' : consistency > 50 ? 'med' : 'low'}>{consistency}%</span>
                            </div>
                        </div>

                        <div className="strategy-body">
                            <div className="calendar-grid">
                                {days.map((day, dIdx) => {
                                    const dayTasks = day.slots.length;
                                    const dayCompleted = day.slots.filter(s => s.status === 'completed').length;
                                    const statusClass = dayTasks === 0 ? 'empty' : dayCompleted === dayTasks ? 'full' : dayCompleted > 0 ? 'partial' : 'none';

                                    return (
                                        <div key={dIdx} className={`calendar-day ${statusClass}`} title={`${day.date}: ${dayCompleted}/${dayTasks}`}>
                                            {day.date.split('-')[2]}
                                        </div>
                                    );
                                })}
                            </div>

                            <div className="month-analytics">
                                <h4>DISTRIBUTION</h4>
                                <ResponsiveContainer width="100%" height={180}>
                                    <PieChart>
                                        <Pie
                                            data={pieData}
                                            cx="50%"
                                            cy="50%"
                                            innerRadius={40}
                                            outerRadius={60}
                                            paddingAngle={5}
                                            dataKey="value"
                                        >
                                            {pieData.map((_, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <RechartsTooltip contentStyle={{ background: '#1e1e1e', border: 'none', fontSize: '12px' }} />
                                    </PieChart>
                                </ResponsiveContainer>
                                <div className="legend">
                                    {pieData.slice(0, 3).map((entry, index) => (
                                        <div key={index} className="legend-item">
                                            <span style={{ background: COLORS[index % COLORS.length] }}></span>
                                            {entry.name}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                );
            });
        } else if (viewMode === 'yearly') {
            // Calculate Subject Mastery for Radar Chart
            const subjectCounts: { [key: string]: { total: number, completed: number } } = {};
            plan.flatMap(d => d.slots).forEach(s => {
                if (s.subject === 'Break' || s.subject === 'Buffer') return;
                if (!subjectCounts[s.subject]) subjectCounts[s.subject] = { total: 0, completed: 0 };
                subjectCounts[s.subject].total++;
                if (s.status === 'completed') subjectCounts[s.subject].completed++;
            });

            const radarData = Object.entries(subjectCounts)
                .map(([subject, stats]) => ({
                    subject,
                    A: Math.round((stats.completed / stats.total) * 100) || 0, // Mastery %
                    fullMark: 100
                }))
                .sort((a, b) => b.A - a.A)
                .slice(0, 6); // Top 6 subjects for cleaner radar

            // Strategic Insights Logic
            const daysElapsed = Math.floor((Date.now() - new Date(plan[0]?.date).getTime()) / (1000 * 60 * 60 * 24));
            const safeDaysElapsed = daysElapsed < 0 ? 0 : daysElapsed; // Fix negative days
            const totalCompleted = plan.reduce((acc, day) => acc + day.slots.filter(s => s.status === 'completed').length, 0);
            const totalTasks = plan.reduce((acc, day) => acc + day.slots.length, 0);
            const completionRate = totalTasks > 0 ? (totalCompleted / totalTasks) * 100 : 0;

            let strategicNote = "Maintain current velocity.";
            if (completionRate < 30 && safeDaysElapsed > 30) strategicNote = "CRITICAL: Velocity below threshold. Increase daily output.";
            else if (completionRate > 80) strategicNote = "EXCELLENT: Exceeding operational targets. Consider advanced modules.";
            else if (safeDaysElapsed < 7) strategicNote = "INITIATION: Establish baseline rhythm.";

            return (
                <div className="grand-strategy-view">
                    <div className="strategy-header-main">
                        <div className="header-content">
                            <h2>THE GRAND STRATEGY</h2>
                            <span className="subtitle">OPERATIONAL COMMAND CENTER</span>
                        </div>
                        <div className="war-room-stats">
                            <div className="stat-pod">
                                <label>CAMPAIGN STATUS</label>
                                <span className="active">ACTIVE</span>
                            </div>
                            <div className="stat-pod">
                                <label>DAYS DEPLOYED</label>
                                <span>{safeDaysElapsed}</span>
                            </div>
                            <div className="stat-pod">
                                <label>GLOBAL MASTERY</label>
                                <span>{Math.round(completionRate)}%</span>
                            </div>
                        </div>
                    </div>

                    <div className="strategy-grid">
                        <div className="hud-panel radar-sector">
                            <div className="panel-header">
                                <h3>SUBJECT MASTERY</h3>
                                <div className="panel-decor"></div>
                            </div>
                            <div className="radar-container">
                                <ResponsiveContainer width="100%" height={280}>
                                    <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                                        <PolarGrid stroke="#34495e" strokeDasharray="3 3" />
                                        <PolarAngleAxis dataKey="subject" tick={{ fill: '#bdc3c7', fontSize: 11, fontFamily: 'Orbitron' }} />
                                        <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                                        <Radar
                                            name="Mastery"
                                            dataKey="A"
                                            stroke="#00d2d3"
                                            strokeWidth={2}
                                            fill="#00d2d3"
                                            fillOpacity={0.2}
                                        />
                                        <RechartsTooltip
                                            contentStyle={{ background: 'rgba(20, 20, 20, 0.9)', border: '1px solid #00d2d3', color: '#fff' }}
                                            itemStyle={{ color: '#00d2d3' }}
                                        />
                                    </RadarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        <div className="right-sector">
                            <div className="hud-panel timeline-sector">
                                <div className="panel-header">
                                    <h3>CAMPAIGN TIMELINE</h3>
                                    <div className="panel-decor"></div>
                                </div>
                                <div className="phase-timeline-graphical">
                                    <div className="timeline-track"></div>
                                    <div className="phase-node completed">
                                        <div className="node-dot"></div>
                                        <div className="node-content">
                                            <span className="phase-name">FOUNDATION</span>
                                            <span className="phase-meta">Nov - Dec</span>
                                        </div>
                                    </div>
                                    <div className="phase-node active">
                                        <div className="node-dot"></div>
                                        <div className="node-content">
                                            <span className="phase-name">CORE COMPETENCY</span>
                                            <span className="phase-meta">Jan - May</span>
                                            <div className="pulse-ring"></div>
                                        </div>
                                    </div>
                                    <div className="phase-node">
                                        <div className="node-dot"></div>
                                        <div className="node-content">
                                            <span className="phase-name">PRELIMS SPRINT</span>
                                            <span className="phase-meta">Jun - Aug</span>
                                        </div>
                                    </div>
                                    <div className="phase-node">
                                        <div className="node-dot"></div>
                                        <div className="node-content">
                                            <span className="phase-name">MAINS MASTERY</span>
                                            <span className="phase-meta">Sep - Dec</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="hud-panel insights-sector">
                                <div className="panel-header">
                                    <h3>STRATEGIC INTEL</h3>
                                    <div className="panel-decor"></div>
                                </div>
                                <div className="intel-content">
                                    <div className="intel-row">
                                        <span className="intel-label">COMMANDER'S NOTE:</span>
                                        <span className="intel-value typing-effect">{strategicNote}</span>
                                    </div>
                                    <div className="heatmap-mini">
                                        <h4>ACTIVITY SIGNATURE</h4>
                                        <div className="heatmap-grid">
                                            {plan.slice(0, 180).map((day, idx) => {
                                                const dayTasks = day.slots.length;
                                                const dayCompleted = day.slots.filter(s => s.status === 'completed').length;
                                                const intensity = dayTasks === 0 ? 0 : Math.ceil((dayCompleted / dayTasks) * 4);
                                                return (
                                                    <div
                                                        key={idx}
                                                        className={`heatmap-cell intensity-${intensity}`}
                                                        title={`${day.date}: ${dayCompleted}/${dayTasks}`}
                                                    ></div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            );
        } else if (viewMode === 'overall') {
            const totalTasks = plan.reduce((acc, day) => acc + day.slots.length, 0);
            const completedTasks = plan.reduce((acc, day) => acc + day.slots.filter(s => s.status === 'completed').length, 0);
            const overallProgress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

            return (
                <div className="overall-view">
                    <h2>📊 2-Year Strategy Overview</h2>
                    <div className="stats-grid">
                        <div className="stat-card">
                            <h3>Total Tasks</h3>
                            <p>{totalTasks}</p>
                        </div>
                        <div className="stat-card">
                            <h3>Completion</h3>
                            <p>{Math.round(overallProgress)}%</p>
                        </div>
                        <div className="stat-card">
                            <h3>Projected End</h3>
                            <p>{plan.length > 0 ? plan[plan.length - 1].date : 'N/A'}</p>
                        </div>
                    </div>
                    <div className="subject-progress">
                        <h3>Subject Breakdown</h3>
                        {['History', 'Geography', 'Polity', 'Economy', 'Science', 'Environment'].map(subject => {
                            const subjectTasks = plan.flatMap(d => d.slots).filter(s => s.subject === subject).length;
                            const subjectCompleted = plan.flatMap(d => d.slots).filter(s => s.subject === subject && s.status === 'completed').length;
                            const subProgress = subjectTasks > 0 ? (subjectCompleted / subjectTasks) * 100 : 0;

                            return (
                                <div key={subject} className="progress-item">
                                    <span>{subject} ({subjectCompleted}/{subjectTasks})</span>
                                    <div className="progress-bar"><div style={{ width: `${subProgress}%` }}></div></div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            );
        }
    };

    return (
        <div className="study-plan-dashboard">
            <div className="planner-header">
                <h1>📅 Mimir's Advanced Scheduler</h1>
                <div className="view-tabs">
                    <button className={viewMode === 'daily' ? 'active' : ''} onClick={() => setViewMode('daily')}>Daily</button>
                    <button className={viewMode === 'weekly' ? 'active' : ''} onClick={() => setViewMode('weekly')}>Weekly</button>
                    <button className={viewMode === 'monthly' ? 'active' : ''} onClick={() => setViewMode('monthly')}>Monthly</button>
                    <button className={viewMode === 'yearly' ? 'active' : ''} onClick={() => setViewMode('yearly')}>Yearly</button>
                    <button className={viewMode === 'overall' ? 'active' : ''} onClick={() => setViewMode('overall')}>Overall</button>
                    <button className={viewMode === 'flashcards' ? 'active' : ''} onClick={() => setViewMode('flashcards')}>🎴 Flashcards</button>
                </div>
                <div className="controls">
                    <button onClick={fetchCSVPlan} disabled={loading}>
                        🔄 Refresh Plan
                    </button>
                </div>
            </div>

            {plan.length > 0 ? (
                <div className="plan-timeline">
                    {renderContent()}
                </div>
            ) : (
                <div className="empty-state">
                    <h2>Loading Plan...</h2>
                </div>
            )}

            {selectedTask && (
                <div className="modal-overlay" onClick={closeModal}>
                    <div className="task-modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>{selectedTask.subject}</h2>
                            <button onClick={closeModal}>×</button>
                        </div>
                        <div className="modal-body">
                            <div className="modal-row">
                                <label>Topic:</label>
                                <p>{selectedTask.activity}</p>
                            </div>
                            <div className="modal-row">
                                <label>Time:</label>
                                <p>{selectedTask.time}</p>
                            </div>
                            <div className="modal-row">
                                <label>Status:</label>
                                <span className={`status-badge ${selectedTask.status}`}>{selectedTask.status}</span>
                            </div>
                            {selectedTask.resource_link && (
                                <div className="modal-row">
                                    <label>Resources:</label>
                                    <a href="#" onClick={(e) => e.preventDefault()}>{selectedTask.resource_link}</a>
                                </div>
                            )}
                            <div className="modal-notes">
                                <label>Notes:</label>
                                <textarea placeholder="Add your notes here..."></textarea>
                            </div>
                        </div>
                        <div className="modal-footer">
                            <button
                                className={`complete-btn ${selectedTask.status === 'completed' ? 'completed' : ''}`}
                                onClick={() => toggleTaskStatus(selectedTask)}
                            >
                                {selectedTask.status === 'completed' ? 'Mark Pending' : 'Mark Complete'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default StudyPlanDashboard;
