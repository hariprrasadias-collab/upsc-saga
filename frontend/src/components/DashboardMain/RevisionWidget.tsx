import React, { useState, useEffect } from 'react';
import './RevisionWidget.css';
import { parseCSV, type Slot } from '../../util/csvParser';
import { usePomodoro } from '../../contexts/PomodoroContext';

import { audioManager } from '../../util/AudioManager';

const RevisionWidget: React.FC = () => {
    const [revisionTasks, setRevisionTasks] = useState<Slot[]>([]);
    const [loading, setLoading] = useState(true);
    const { startTask } = usePomodoro();

    const fetchRevisionTasks = async () => {
        try {
            const response = await fetch('/UPSC_Scheduler.csv');
            if (!response.ok) throw new Error('Failed to fetch schedule');

            const csvText = await response.text();
            const plan = parseCSV(csvText);

            // Filter logic:
            // STRICTLY tasks explicitly marked as "Revision", "Revise", or "Review"
            // per user request ("only review task")

            const allTasks = plan.flatMap(day => day.slots);

            const targets = allTasks.filter(task => {
                const activity = task.activity.toLowerCase();
                const subject = task.subject.toLowerCase();

                const isRevision =
                    activity.includes('revise') ||
                    activity.includes('revision') ||
                    activity.includes('review') ||
                    subject === 'revision' ||
                    subject === 'review';

                const isPending = task.status === 'pending';

                // Only show pending revision tasks
                return isPending && isRevision;
            });

            // Sort: By date, then by time
            targets.sort((a, b) => {
                return (a.originalDate || '').localeCompare(b.originalDate || '');
            });

            setRevisionTasks(targets);
        } catch (err) {
            console.error('Failed to load revision targets', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRevisionTasks();

        // Listen for task updates from other components
        const handleUpdate = () => fetchRevisionTasks();
        window.addEventListener('taskUpdate', handleUpdate);
        return () => window.removeEventListener('taskUpdate', handleUpdate);
    }, []);

    const [completingId, setCompletingId] = useState<string | null>(null);

    const handleComplete = (task: Slot) => {
        audioManager.play('success');
        setCompletingId(task.id);

        // Delay actual removal to allow animation to play
        setTimeout(() => {
            // Update local storage
            const completedTasks = new Set(JSON.parse(localStorage.getItem('completedTasks') || '[]'));
            completedTasks.add(task.id);
            localStorage.setItem('completedTasks', JSON.stringify(Array.from(completedTasks)));

            // Dispatch event
            window.dispatchEvent(new Event('taskUpdate'));

            // Optimistic update
            setRevisionTasks(prev => prev.filter(t => t.id !== task.id));
            setCompletingId(null);
        }, 800); // Match CSS animation duration
    };

    const formatDate = (dateStr?: string) => {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);

        if (date.toDateString() === today.toDateString()) return 'Today';
        if (date.toDateString() === yesterday.toDateString()) return 'Yesterday';
        if (date.toDateString() === tomorrow.toDateString()) return 'Tomorrow';

        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    };

    if (loading) return <div className="revision-widget loading"><div className="rune-loader"></div></div>;

    return (
        <div className="revision-widget">
            <div className="widget-header">
                <h3>⚔️ REVISION TARGETS</h3>
                <span className="due-count">{revisionTasks.length} PENDING</span>
            </div>

            {revisionTasks.length === 0 ? (
                <div className="revision-empty-state">
                    <div className="empty-icon">🛡️</div>
                    <p>No enemies remain. Rest, warrior.</p>
                </div>
            ) : (
                <div className="due-list">
                    {revisionTasks.slice(0, 5).map(task => (
                        <div
                            key={task.id}
                            className={`due-item ${completingId === task.id ? 'completing' : ''}`}
                        >
                            <div className="due-info">
                                <div className="due-subject">{task.subject}</div>
                                <div className="due-title">{task.activity}</div>
                                {task.originalDate && <div className="due-date">{formatDate(task.originalDate)}</div>}
                            </div>
                            <div className="due-actions">
                                <button
                                    className="focus-btn"
                                    onClick={() => {
                                        // Auto-start Pomodoro
                                        // Infer duration? Default to 25 for now.
                                        // Check if it's a break task (unlikely here but safe to check)
                                        const isBreak = task.activity.toLowerCase().includes('break');
                                        startTask(task.id, task.activity, 25, isBreak);
                                    }}
                                    title="Focus (Start Timer)"
                                    aria-label="Start Focus Timer"
                                    disabled={completingId === task.id}
                                >
                                    <span aria-hidden="true">👁️</span>
                                </button>
                                <button
                                    className="quick-revise-btn"
                                    onClick={() => handleComplete(task)}
                                    title="Mark Complete"
                                    aria-label="Mark Task Complete"
                                    disabled={completingId === task.id}
                                >
                                    <span aria-hidden="true">⚔️</span>
                                </button>
                            </div>
                        </div>
                    ))}
                    {revisionTasks.length > 5 && (
                        <div className="more-count">
                            + {revisionTasks.length - 5} more battles awaiting
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default RevisionWidget;
