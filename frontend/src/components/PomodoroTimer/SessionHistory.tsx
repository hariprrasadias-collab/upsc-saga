import React, { useState, useMemo } from 'react';
import type { PomodoroSession } from '../../contexts/PomodoroContext';
import './SessionHistory.css';

export const SessionHistory: React.FC = () => {
    const [sessions, setSessions] = useState<PomodoroSession[]>(() => {
        return JSON.parse(localStorage.getItem('pomodoro_sessions') || '[]');
    });
    const [filterMode, setFilterMode] = useState<'all' | 'work' | 'break'>('all');
    const [dateRange, setDateRange] = useState<number>(7); // days

    // Calculate stats
    const stats = useMemo(() => {
        const now = new Date();
        const cutoffDate = new Date(now.getTime() - dateRange * 24 * 60 * 60 * 1000);

        const filteredSessions = sessions.filter(s => {
            const sessionDate = new Date(s.timestamp);
            const modeMatch = filterMode === 'all' ||
                (filterMode === 'work' && s.mode === 'work') ||
                (filterMode === 'break' && s.mode !== 'work');
            return sessionDate >= cutoffDate && modeMatch;
        });

        const workSessions = filteredSessions.filter(s => s.mode === 'work');
        const totalTime = filteredSessions.reduce((acc, s) => acc + s.duration, 0);
        const totalWorkTime = workSessions.reduce((acc, s) => acc + s.duration, 0);

        // Calculate streaks
        const workSessionsByDate = new Map<string, number>();
        sessions.filter(s => s.mode === 'work').forEach(s => {
            const date = new Date(s.timestamp).toDateString();
            workSessionsByDate.set(date, (workSessionsByDate.get(date) || 0) + 1);
        });

        let currentStreak = 0;
        let bestStreak = 0;
        let tempStreak = 0;
        const today = new Date().toDateString();
        let checkDate = new Date();

        // Current streak
        while (true) {
            const dateStr = checkDate.toDateString();
            if (workSessionsByDate.has(dateStr)) {
                currentStreak++;
                checkDate.setDate(checkDate.getDate() - 1);
            } else if (dateStr === today) {
                checkDate.setDate(checkDate.getDate() - 1);
            } else {
                break;
            }
        }

        // Best streak
        const sortedDates = Array.from(workSessionsByDate.keys()).sort();
        for (let i = 0; i < sortedDates.length; i++) {
            if (i === 0 || new Date(sortedDates[i]).getTime() - new Date(sortedDates[i - 1]).getTime() === 86400000) {
                tempStreak++;
                bestStreak = Math.max(bestStreak, tempStreak);
            } else {
                tempStreak = 1;
            }
        }

        return {
            totalSessions: filteredSessions.length,
            workSessions: workSessions.length,
            totalTime: Math.round(totalTime / 60), // minutes
            totalWorkTime: Math.round(totalWorkTime / 60),
            currentStreak,
            bestStreak,
            sessions: filteredSessions
        };
    }, [sessions, filterMode, dateRange]);

    const exportToCSV = () => {
        const headers = ['Date', 'Time', 'Mode', 'Duration (min)', 'Task'];
        const rows = stats.sessions.map(s => {
            const date = new Date(s.timestamp);
            return [
                date.toLocaleDateString(),
                date.toLocaleTimeString(),
                s.mode,
                Math.round(s.duration / 60),
                s.taskTitle || 'No task'
            ];
        });

        const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pomodoro-history-${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const exportToJSON = () => {
        const data = {
            exportDate: new Date().toISOString(),
            dateRange: `Last ${dateRange} days`,
            stats: {
                totalSessions: stats.totalSessions,
                workSessions: stats.workSessions,
                totalTime: stats.totalTime,
                currentStreak: stats.currentStreak,
                bestStreak: stats.bestStreak
            },
            sessions: stats.sessions
        };

        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pomodoro-history-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const clearHistory = () => {
        if (window.confirm('Delete all session history? This cannot be undone.')) {
            localStorage.setItem('pomodoro_sessions', '[]');
            setSessions([]);
        }
    };

    return (
        <div className="session-history">
            <div className="history-header">
                <h3>📊 SESSION HISTORY</h3>
                <div className="history-actions">
                    <button onClick={exportToCSV} className="export-btn csv">CSV</button>
                    <button onClick={exportToJSON} className="export-btn json">JSON</button>
                    <button onClick={clearHistory} className="clear-btn">Clear</button>
                </div>
            </div>

            <div className="history-filters">
                <select value={dateRange} onChange={(e) => setDateRange(Number(e.target.value))}>
                    <option value={7}>Last 7 days</option>
                    <option value={30}>Last 30 days</option>
                    <option value={90}>Last 90 days</option>
                    <option value={365}>Last year</option>
                    <option value={999999}>All time</option>
                </select>
                <select value={filterMode} onChange={(e) => setFilterMode(e.target.value as any)}>
                    <option value="all">All sessions</option>
                    <option value="work">Work only</option>
                    <option value="break">Breaks only</option>
                </select>
            </div>

            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-value">{stats.totalSessions}</div>
                    <div className="stat-label">Total Sessions</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{stats.workSessions}</div>
                    <div className="stat-label">Work Sessions</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{stats.totalWorkTime}m</div>
                    <div className="stat-label">Focus Time</div>
                </div>
                <div className="stat-card streak">
                    <div className="stat-value">🔥 {stats.currentStreak}</div>
                    <div className="stat-label">Current Streak</div>
                    <div className="stat-note">Best: {stats.bestStreak} days</div>
                </div>
            </div>

            <div className="session-list">
                {stats.sessions.length === 0 ? (
                    <div className="empty-state">No sessions found</div>
                ) : (
                    stats.sessions.slice(0, 50).map(session => {
                        const date = new Date(session.timestamp);
                        return (
                            <div key={session.id} className={`session-item ${session.mode}`}>
                                <div className="session-icon">
                                    {session.mode === 'work' ? '⚔️' : '🛡️'}
                                </div>
                                <div className="session-details">
                                    <div className="session-task">{session.taskTitle || 'Untitled'}</div>
                                    <div className="session-meta">
                                        {date.toLocaleDateString()} • {date.toLocaleTimeString()} • {Math.round(session.duration / 60)}min
                                    </div>
                                </div>
                            </div>
                        );
                    })
                )}
            </div>

            {stats.sessions.length > 50 && (
                <div className="session-note">Showing 50 most recent sessions</div>
            )}
        </div>
    );
};
