// frontend/src/components/WarMap/WarMapContainer.tsx
import React, { useState, useEffect, useCallback } from 'react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import './WarMap.css';
import WarMapHeader from './WarMapHeader';
import type { Task, RawTaskFromAPI } from '../../App';

type ValuePiece = Date | null;
type Value = ValuePiece | [ValuePiece, ValuePiece];

interface WarMapContainerProps {
  // Define the expected function type clearly
  onTaskCompleted: () => Promise<void>;
}

const WarMapContainer: React.FC<WarMapContainerProps> = ({ onTaskCompleted }) => {
  const [date, setDate] = useState<Value>(new Date());
  const [dayTasks, setDayTasks] = useState<Task[]>([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);

  const getSelectedDateString = useCallback((): string => {
    const selectedDate = date instanceof Date ? date : new Date();
    const offset = selectedDate.getTimezoneOffset();
    const localDate = new Date(selectedDate.getTime() - (offset * 60 * 1000));
    return localDate.toISOString().split('T')[0];
  }, [date]);

  const dateStr = getSelectedDateString();

  const fetchTasksForDate = useCallback(async () => {
    setIsLoadingTasks(true);
    try {
      const response = await fetch(`http://localhost:5000/api/tasks?date=${dateStr}`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch tasks for date');
      }

      const rawTasks: RawTaskFromAPI[] = await response.json();
      const tasksForDay: Task[] = rawTasks.map(task => ({
        id: task.id,
        title: task.title,
        isCompleted: task.isCompleted === 1,
        xp_reward: task.xp_reward,
        associated_stat: task.associated_stat,
        due_date: task.due_date,
      }));
      setDayTasks(tasksForDay);

    } catch (error) {
      console.error('Error fetching day tasks:', error);
    } finally {
      setIsLoadingTasks(false);
    }
  }, [dateStr]);

  useEffect(() => {
    fetchTasksForDate();
  }, [fetchTasksForDate]);

  const handleTaskAddedOrCancelled = async () => {
    await fetchTasksForDate(); 
    await onTaskCompleted(); 
    setShowAddForm(false); 
  };

  const handleTaskComplete = async (taskId: number) => {
    try {
      const response = await fetch(`http://localhost:5000/api/tasks/${taskId}/complete`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to complete task');
      }

      await fetchTasksForDate(); 
      await onTaskCompleted(); 
    } catch (err) {
      console.error('Error completing task:', err);
      alert('Failed to complete task. See console for details.');
    }
  };

  return (
    <div className="war-map-container">
      <WarMapHeader
        showAddForm={showAddForm}
        onToggleAddForm={() => setShowAddForm(prev => !prev)}
        selectedDateStr={dateStr}
        onTaskActionComplete={handleTaskAddedOrCancelled}
      />

      {!showAddForm && (
        <div className="map-content-grid">
          <div className="calendar-section">
            <Calendar
              onChange={setDate}
              value={date}
              className="react-calendar-themed"
            />
          </div>

          <div className="day-tasks-section">
            <h2>Rituals for {dateStr}</h2>
            <div className="tasks-list-container">
              {isLoadingTasks ? (
                <div className="loading-message">Consulting the oracles...</div>
              ) : dayTasks.length > 0 ? (
                <ul className="war-map-task-list">
                  {dayTasks.map((task) => (
                    <li key={task.id} className={`war-map-task-item ${task.isCompleted ? 'completed' : ''}`}>
                      <div className="wm-task-checkbox-wrapper">
                        <input
                          type="checkbox"
                          id={`wm-task-${task.id}`}
                          checked={task.isCompleted}
                          onChange={() => handleTaskComplete(task.id)}
                          disabled={task.isCompleted}
                        />
                        <label htmlFor={`wm-task-${task.id}`} className="wm-task-title-label">
                          {task.title}
                        </label>
                      </div>
                      <span className="wm-task-xp">+{task.xp_reward} XP</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="empty-tasks-message">
                  No rituals planned for this day.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WarMapContainer;