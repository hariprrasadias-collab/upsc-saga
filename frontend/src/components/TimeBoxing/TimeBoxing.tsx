import React, { useState, useEffect } from 'react';
import './TimeBoxing.css';

interface TimeBox {
    subject: string;
    allocated_hours: number;
    spent_hours: number;
}

const TimeBoxing: React.FC = () => {
    const [timeBoxes, setTimeBoxes] = useState<TimeBox[]>([]);
    const [showModal, setShowModal] = useState(false);
    const [newSubject, setNewSubject] = useState('General Studies I');
    const [newHours, setNewHours] = useState(2);

    const TOTAL_HOURS_PER_DAY = 8;

    useEffect(() => {
        fetchTimeBoxes();
    }, []);

    const fetchTimeBoxes = async () => {
        try {
            const res = await fetch('http://localhost:5000/api/timebox/get');
            const data = await res.json();
            setTimeBoxes(data);
        } catch (err) {
            console.error('Failed to fetch time boxes:', err);
        }
    };

    const handleAddTimeBox = async () => {
        const totalAllocated = timeBoxes.reduce((sum, tb) => sum + tb.allocated_hours, 0);

        if (totalAllocated + newHours > TOTAL_HOURS_PER_DAY) {
            alert(`Cannot allocate more than ${TOTAL_HOURS_PER_DAY} hours total!`);
            return;
        }

        try {
            await fetch('http://localhost:5000/api/timebox/add', {
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
            await fetch(`http://localhost:5000/api/timebox/delete/${encodeURIComponent(subject)}`, {
                method: 'DELETE'
            });
            await fetchTimeBoxes();
        } catch (err) {
            console.error('Failed to delete time box:', err);
        }
    };

    const totalAllocated = timeBoxes.reduce((sum, tb) => sum + tb.allocated_hours, 0);
    const totalSpent = timeBoxes.reduce((sum, tb) => sum + tb.spent_hours, 0);
    const remainingHours = TOTAL_HOURS_PER_DAY - totalAllocated;

    return (
        <div className="timebox-container">
            <div className="timebox-header">
                <h1>⏰ Time Boxing Planner</h1>
                <p>Allocate your daily study hours across subjects</p>
            </div>

            <div className="timebox-summary">
                <div className="summary-card">
                    <span className="summary-label">Total Allocated</span>
                    <span className="summary-value">{totalAllocated}h / {TOTAL_HOURS_PER_DAY}h</span>
                </div>
                <div className="summary-card">
                    <span className="summary-label">Spent Today</span>
                    <span className="summary-value">{totalSpent.toFixed(1)}h</span>
                </div>
                <div className="summary-card">
                    <span className="summary-label">Remaining</span>
                    <span className="summary-value">{remainingHours}h</span>
                </div>
            </div>

            <div className="timebox-list">
                {timeBoxes.map(box => {
                    const percentage = (box.spent_hours / box.allocated_hours) * 100;
                    const isOvertime = box.spent_hours > box.allocated_hours;

                    return (
                        <div key={box.subject} className={`timebox-card ${isOvertime ? 'overtime' : ''}`}>
                            <div className="timebox-info">
                                <h3>{box.subject}</h3>
                                <div className="timebox-stats">
                                    <span>{box.spent_hours.toFixed(1)}h / {box.allocated_hours}h</span>
                                    {isOvertime && <span className="overtime-badge">⚠️ Overtime</span>}
                                </div>
                            </div>

                            <div className="progress-bar-container">
                                <div
                                    className={`progress-bar ${isOvertime ? 'overtime' : ''}`}
                                    style={{ width: `${Math.min(percentage, 100)}%` }}
                                />
                            </div>

                            <button className="delete-btn" onClick={() => handleDelete(box.subject)}>
                                ×
                            </button>
                        </div>
                    );
                })}

                {timeBoxes.length === 0 && (
                    <div className="no-timeboxes">
                        No time boxes set. Click "+ Add Time Box" to begin.
                    </div>
                )}
            </div>

            <button className="add-timebox-btn" onClick={() => setShowModal(true)}>
                + Add Time Box
            </button>

            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h2>Add Time Box</h2>

                        <label>Subject:</label>
                        <select value={newSubject} onChange={(e) => setNewSubject(e.target.value)}>
                            <option>General Studies I</option>
                            <option>General Studies II</option>
                            <option>General Studies III</option>
                            <option>General Studies IV</option>
                            <option>Essay</option>
                            <option>CSAT</option>
                            <option>Optional Paper 1</option>
                            <option>Optional Paper 2</option>
                        </select>

                        <label>Allocated Hours:</label>
                        <input
                            type="number"
                            min="0.5"
                            max="8"
                            step="0.5"
                            value={newHours}
                            onChange={(e) => setNewHours(Number(e.target.value))}
                        />

                        <div className="modal-actions">
                            <button className="save-btn" onClick={handleAddTimeBox}>Save</button>
                            <button className="cancel-btn" onClick={() => setShowModal(false)}>Cancel</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TimeBoxing;
