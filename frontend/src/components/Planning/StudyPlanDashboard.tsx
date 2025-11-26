import React, { useState } from 'react';
import './StudyPlanDashboard.css';

interface Slot {
    time: string;
    hours: number;
    type: string;
    subject?: string;
    activity?: string;
    duration?: number;
}

interface DayPlan {
    date: string;
    day: string;
    slots: Slot[];
}

const StudyPlanDashboard: React.FC = () => {
    const [plan, setPlan] = useState<DayPlan[]>([]);
    const [loading, setLoading] = useState(false);
    const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);

    const generatePlan = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:5000/api/planner/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ start_date: startDate })
            });
            const data = await res.json();
            if (data.success) {
                setPlan(data.plan);
            }
        } catch (err) {
            console.error("Failed to generate plan:", err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="study-plan-dashboard">
            <div className="planner-header">
                <h1>📅 Mimir's 2-Year Strategy</h1>
                <div className="controls">
                    <input
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                    />
                    <button onClick={generatePlan} disabled={loading}>
                        {loading ? 'Generating...' : '🔮 Generate Plan'}
                    </button>
                </div>
            </div>

            {plan.length > 0 && (
                <div className="plan-timeline">
                    {plan.slice(0, 30).map((day, idx) => ( // Show first 30 days for now
                        <div key={idx} className="day-card">
                            <div className="day-header">
                                <span className="day-date">{day.date}</span>
                                <span className="day-name">{day.day}</span>
                            </div>
                            <div className="day-slots">
                                {day.slots.map((slot, sIdx) => (
                                    <div key={sIdx} className={`slot-card ${slot.subject ? slot.subject.toLowerCase() : 'free'}`}>
                                        <div className="slot-time">{slot.time}</div>
                                        <div className="slot-activity">
                                            {slot.activity || "Free Time"}
                                        </div>
                                        {slot.subject && <div className="slot-subject">{slot.subject}</div>}
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default StudyPlanDashboard;
