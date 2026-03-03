import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip } from 'recharts';
import { useNavigate } from 'react-router-dom';
import './TimeBoxing.css';
import { brainService } from '../../services/BrainService';

interface TimeBox {
    subject: string;
    allocated_hours: number;
    spent_hours: number;
}

interface Suggestion {
    subject: string;
    reason: string;
    recommended_hours: number;
}

const TimeBoxing: React.FC = () => {
    const [timeBoxes, setTimeBoxes] = useState<TimeBox[]>([]);
    const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
    const [showModal, setShowModal] = useState(false);
    const [newSubject, setNewSubject] = useState('General Studies I');
    const [newHours, setNewHours] = useState(2);
    const [isOptimizing, setIsOptimizing] = useState(false);
    const navigate = useNavigate();

    // Persist daily goal in localStorage
    const [dailyGoal, setDailyGoal] = useState(() => {
        const saved = localStorage.getItem('timebox_daily_goal');
        return saved ? Number(saved) : 8;
    });

    useEffect(() => {
        fetchTimeBoxes();
        fetchSuggestions();
    }, []);

    useEffect(() => {
        localStorage.setItem('timebox_daily_goal', dailyGoal.toString());
    }, [dailyGoal]);

    const fetchTimeBoxes = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/timebox/get`);
            const data = await res.json();
            setTimeBoxes(data);
        } catch (err) {
            console.error('Failed to fetch time boxes:', err);
        }
    };

    const fetchSuggestions = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/timebox/suggestions`);
            const data = await res.json();
            setSuggestions(data);
        } catch (err) {
            console.error('Failed to fetch suggestions:', err);
        }
    };

    const handleAddTimeBox = async () => {
        const totalAllocated = timeBoxes.reduce((sum, tb) => sum + tb.allocated_hours, 0);

        if (totalAllocated + newHours > dailyGoal) {
            if (!window.confirm(`This will exceed your daily goal of ${dailyGoal} hours. Continue?`)) {
                return;
            }
        }

        try {
            await fetch(`${API_BASE_URL}/api/timebox/add`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    subject: newSubject,
                    allocated_hours: newHours
                })
            });

            await fetchTimeBoxes();
            setShowModal(false);
        } catch (err) {
            console.error('Failed to add time box:', err);
        }
    };

    const handleDelete = async (subject: string) => {
        try {
            await fetch(`${API_BASE_URL}/api/timebox/delete/${encodeURIComponent(subject)}`, {
                method: 'DELETE'
            });
            await fetchTimeBoxes();
        } catch (err) {
            console.error('Failed to delete time box:', err);
        }
    };

    const handleStartFocus = (_subject: string) => {
        navigate('/pomodoro');
    };

    const handleOptimize = async () => {
        setIsOptimizing(true);
        try {
            const context = {
                current_allocations: timeBoxes,
                daily_goal: dailyGoal
            };

            const response = await brainService.think(
                "Review my time boxing allocations. If they are unbalanced or missing key areas, suggest a better distribution using the UPDATE_TIMEBOXES action.",
                context
            );

            // Check if Brain suggested an update
            const updateAction = response.suggested_actions.find(a => a.type === 'UPDATE_TIMEBOXES');
            if (updateAction) {
                if (window.confirm(`Strategos suggests: ${response.response_text}\n\nApply these changes?`)) {
                    await brainService.executeAction('UPDATE_TIMEBOXES', updateAction.payload);
                    await fetchTimeBoxes();
                }
            } else {
                alert(`Strategos Analysis: ${response.response_text}`);
            }
        } catch (err) {
            console.error("Optimization failed:", err);
            alert("Strategos is currently offline.");
        } finally {
            setIsOptimizing(false);
        }
    };

    const totalAllocated = timeBoxes.reduce((sum, tb) => sum + tb.allocated_hours, 0);
    const totalSpent = timeBoxes.reduce((sum, tb) => sum + tb.spent_hours, 0);
    const remainingHours = Math.max(0, dailyGoal - totalAllocated);

    // Chart Data
    const chartData = timeBoxes.map(tb => ({
        name: tb.subject,
        value: tb.allocated_hours
    }));

    if (remainingHours > 0) {
        chartData.push({ name: 'Remaining', value: remainingHours });
    }

    const COLORS = ['#d4a574', '#8b0000', '#2ecc71', '#3498db', '#9b59b6', '#f1c40f', '#e67e22', '#34495e'];

    return (
        <motion.div
            className="timebox-container"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
        >
            <div className="timebox-header">
                <motion.h1
                    initial={{ scale: 0.9 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 200 }}
                >
                    Time Boxing Strategy
                </motion.h1>
                <p>Master your schedule, Kratos.</p>

                <div className="goal-config">
                    <span className="goal-label">Daily Target:</span>
                    <input
                        type="number"
                        className="goal-input"
                        value={dailyGoal}
                        onChange={(e) => setDailyGoal(Number(e.target.value))}
                        min="1"
                        max="24"
                    />
                    <span className="goal-label">Hours</span>
                </div>
                <button
                    className="optimize-btn"
                    onClick={handleOptimize}
                    disabled={isOptimizing}
                    style={{ marginLeft: '20px', padding: '8px 16px', background: 'linear-gradient(45deg, #f1c40f, #f39c12)', border: 'none', borderRadius: '4px', color: '#000', fontWeight: 'bold', cursor: 'pointer' }}
                >
                    {isOptimizing ? 'Optimizing...' : '⚡ Optimize Schedule'}
                </button>
            </div>

            <div className="timebox-content-grid">
                <div className="timebox-left-panel">
                    <div className="timebox-summary">
                        <motion.div className="summary-card" whileHover={{ scale: 1.05 }}>
                            <span className="summary-label">Allocated</span>
                            <span className="summary-value">{totalAllocated}h</span>
                        </motion.div>
                        <motion.div className="summary-card" whileHover={{ scale: 1.05 }}>
                            <span className="summary-label">Executed</span>
                            <span className="summary-value">{totalSpent.toFixed(1)}h</span>
                        </motion.div>
                        <motion.div className="summary-card" whileHover={{ scale: 1.05 }}>
                            <span className="summary-label">Remaining Capacity</span>
                            <span className="summary-value">{remainingHours}h</span>
                        </motion.div>
                    </div>

                    <div className="timebox-list">
                        <AnimatePresence>
                            {timeBoxes.map(box => {
                                const percentage = (box.spent_hours / box.allocated_hours) * 100;
                                const isOvertime = box.spent_hours > box.allocated_hours;

                                return (
                                    <motion.div
                                        key={box.subject}
                                        className={`timebox-card ${isOvertime ? 'overtime' : ''}`}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: 20 }}
                                        layout
                                    >
                                        <div className="timebox-info">
                                            <h3>{box.subject}</h3>
                                            <div className="timebox-stats">
                                                <span>{box.spent_hours.toFixed(1)}h / {box.allocated_hours}h</span>
                                                {isOvertime && <span className="overtime-badge">Overtime</span>}
                                            </div>
                                        </div>

                                        <div className="progress-bar-container">
                                            <motion.div
                                                className={`progress-bar ${isOvertime ? 'overtime' : ''}`}
                                                initial={{ width: 0 }}
                                                animate={{ width: `${Math.min(percentage, 100)}%` }}
                                                transition={{ duration: 1, ease: "easeOut" }}
                                            />
                                            <div className="progress-segments"></div>
                                        </div>

                                        <div className="card-actions">
                                            <button className="focus-btn" onClick={() => handleStartFocus(box.subject)} title="Start Focus Session">
                                                ▶
                                            </button>
                                            <button className="delete-btn" onClick={() => handleDelete(box.subject)} title="Delete Timebox">
                                                ×
                                            </button>
                                        </div>
                                    </motion.div>
                                );
                            })}
                        </AnimatePresence>

                        {timeBoxes.length === 0 && (
                            <motion.div
                                className="no-timeboxes"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                            >
                                No battles planned for today.
                            </motion.div>
                        )}
                    </div>

                    <motion.button
                        className="add-timebox-btn"
                        onClick={() => setShowModal(true)}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        + Forge New Timebox
                    </motion.button>
                </div>

                <div className="timebox-right-panel">
                    <div className="chart-container">
                        <h3>Allocation Distribution</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={chartData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {chartData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.name === 'Remaining' ? '#34495e' : COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <RechartsTooltip
                                    contentStyle={{ backgroundColor: '#1a1d24', border: '1px solid #d4a574' }}
                                    itemStyle={{ color: '#ecf0f1' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                        <div className="chart-legend">
                            {chartData.map((entry, index) => (
                                <div key={index} className="legend-item">
                                    <span className="legend-color" style={{ backgroundColor: entry.name === 'Remaining' ? '#34495e' : COLORS[index % COLORS.length] }}></span>
                                    <span className="legend-label">{entry.name}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            <AnimatePresence>
                {showModal && (
                    <motion.div
                        className="modal-overlay"
                        onClick={() => setShowModal(false)}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                    >
                        <motion.div
                            className="modal-content"
                            onClick={(e) => e.stopPropagation()}
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.8, opacity: 0 }}
                        >
                            <h2>Forge Timebox</h2>

                            <label>Subject</label>
                            <select value={newSubject} onChange={(e) => setNewSubject(e.target.value)}>
                                <option>General Studies I</option>
                                <option>General Studies II</option>
                                <option>General Studies III</option>
                                <option>General Studies IV</option>
                                <option>Essay</option>
                                <option>CSAT</option>
                                <option>Optional Paper 1</option>
                                <option>Optional Paper 2</option>
                                <option>Current Affairs</option>
                                <option>Revision</option>
                            </select>

                            <label>Allocated Hours</label>
                            <input
                                type="number"
                                min="0.5"
                                max="8"
                                step="0.5"
                                value={newHours}
                                onChange={(e) => setNewHours(Number(e.target.value))}
                            />

                            {suggestions.length > 0 && (
                                <div className="suggestions-section">
                                    <h4>Recommended for You (Weak Areas)</h4>
                                    <div className="suggestions-list">
                                        {suggestions.map((s, i) => (
                                            <div
                                                key={i}
                                                className="suggestion-chip"
                                                onClick={() => {
                                                    setNewSubject(s.subject);
                                                    setNewHours(s.recommended_hours);
                                                }}
                                            >
                                                <span className="suggestion-subject">{s.subject}</span>
                                                <span className="suggestion-reason">{s.reason}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <div className="modal-actions">
                                <motion.button
                                    className="save-btn"
                                    onClick={handleAddTimeBox}
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                >
                                    Confirm
                                </motion.button>
                                <motion.button
                                    className="cancel-btn"
                                    onClick={() => setShowModal(false)}
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                >
                                    Cancel
                                </motion.button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

export default TimeBoxing;
