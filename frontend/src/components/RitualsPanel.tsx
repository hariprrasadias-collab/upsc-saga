// /frontend/src/components/RitualsPanel.tsx
import React, { useState, useEffect, useCallback } from 'react';
import './RitualsPanel.css';
import type { Task } from '../App';
import StudyTimer from './StudyTimer';
import { generateCSVTaskId } from '../util/taskUtils';

interface RitualsPanelProps {
  tasks?: Task[];
  onTaskComplete: (taskId: number) => void;
  onPlanRituals: () => void;
}

interface Slot {
  id: string;
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

const RitualsPanel: React.FC<RitualsPanelProps> = ({ tasks = [], onTaskComplete, onPlanRituals }) => {
  const [csvTasks, setCsvTasks] = useState<Slot[]>([]);

  // --- CSV Fetching Logic (Mirrors WarMapContainer) ---
  const getTodayDateString = (): string => {
    const date = new Date();
    const offset = date.getTimezoneOffset();
    const localDate = new Date(date.getTime() - (offset * 60 * 1000));
    return localDate.toISOString().split('T')[0];
  };

  const todayStr = getTodayDateString();

  const parseCSV = (csvText: string): DayPlan[] => {
    const lines = csvText.split('\n').filter(line => line.trim() !== '');
    const dataRows = lines.slice(1); // Skip headers

    const dayMap: { [key: string]: DayPlan } = {};
    const completedTasks = new Set(JSON.parse(localStorage.getItem('completedTasks') || '[]'));

    dataRows.forEach((row, index) => {
      const columns = row.split(',').map(c => c.trim());
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

      // Use content-based ID to prevent collisions on CSV regeneration
      const taskId = generateCSVTaskId(date, time, subject, topic);
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

    return Object.values(dayMap);
  };

  const fetchCSVTasks = useCallback(async () => {
    try {
      const response = await fetch('/UPSC_Scheduler.csv');
      if (!response.ok) throw new Error('Failed to fetch CSV');
      const csvText = await response.text();
      const allPlans = parseCSV(csvText);
      const planForDate = allPlans.find(p => p.date === todayStr);
      setCsvTasks(planForDate ? planForDate.slots : []);
    } catch (err) {
      console.error("Failed to fetch CSV plan:", err);
      setCsvTasks([]);
    }
  }, [todayStr]);

  const toggleCSVTaskStatus = (task: Slot) => {
    const completedTasks = new Set(JSON.parse(localStorage.getItem('completedTasks') || '[]'));
    const isCompleted = completedTasks.has(task.id);

    if (isCompleted) {
      completedTasks.delete(task.id);
    } else {
      completedTasks.add(task.id);
    }

    localStorage.setItem('completedTasks', JSON.stringify(Array.from(completedTasks)));
    fetchCSVTasks();

    // Dispatch custom event for cross-component sync
    window.dispatchEvent(new Event('taskUpdate'));
  };

  useEffect(() => {
    fetchCSVTasks();

    // Listen for storage events to sync across tabs/components
    const handleStorageChange = () => fetchCSVTasks();
    window.addEventListener('storage', handleStorageChange);
    // Custom event for same-window updates (e.g. from War Map)
    window.addEventListener('taskUpdate', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('taskUpdate', handleStorageChange);
    };
  }, [fetchCSVTasks]);

  const hasTasks = tasks.length > 0 || csvTasks.length > 0;

  return (
    <div className="rituals-panel">
      <div className="rituals-header">
        <h2>TODAY'S RITUALS</h2>
      </div>

      <StudyTimer />

      <ul className="rituals-list">
        {!hasTasks ? (
          <p className="no-tasks-message">No rituals due today. Forge new ones on the War Map!</p>
        ) : (
          <>
            {/* CSV Tasks */}
            {csvTasks.map(task => (
              <li key={`csv-${task.id}`} className={`ritual-item${task.status === 'completed' ? ' completed' : ''}`}>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={task.status === 'completed'}
                    onChange={() => toggleCSVTaskStatus(task)}
                  />
                  <span className="checkbox-custom"></span>
                </label>
                <div className="task-info">
                  <span className="task-title">{task.subject} - {task.activity}</span>
                  <span className="task-xp" style={{ fontSize: '0.8rem', color: '#bdc3c7' }}>{task.time}</span>
                </div>
              </li>
            ))}

            {/* Backend Tasks */}
            {tasks.map(task => (
              <li key={task.id} className={`ritual-item${task.isCompleted ? ' completed' : ''}`}>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={task.isCompleted}
                    onChange={() => onTaskComplete(task.id)}
                    disabled={task.isCompleted}
                  />
                  <span className="checkbox-custom"></span>
                </label>
                <div className="task-info">
                  <span className="task-title">{task.title}</span>
                  {task.xp_reward > 0 && <span className="task-xp">+{task.xp_reward} XP</span>}
                </div>
              </li>
            ))}
          </>
        )}
      </ul>

      <button
        className="add-ritual-btn"
        style={{ marginTop: 'auto', alignSelf: 'center' }}
        onClick={onPlanRituals}
      >
        PLAN MORE RITUALS
      </button>
    </div>
  );
};

export default RitualsPanel;