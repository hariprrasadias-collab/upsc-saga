// /frontend/src/components/WarMap/WarMapContainer.tsx
import React, { useState, useEffect, useCallback } from 'react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css'; // Default calendar styles, we'll override
import './WarMap.css'; // Custom WarMap styles
import WarMapHeader from './WarMapHeader'; // The header component, now handles AddTaskForm
import type { Task, RawTaskFromAPI } from '../../App'; // Re-import Task and RawTaskFromAPI interfaces

type ValuePiece = Date | null;
type Value = ValuePiece | [ValuePiece, ValuePiece];

interface WarMapContainerProps {
  onTaskCompleted: () => Promise<void>;// To refresh dashboard after any task action
}

const WarMapContainer: React.FC<WarMapContainerProps> = ({ onTaskCompleted }) => {
  const [date, setDate] = useState<Value>(new Date());
  const [dayTasks, setDayTasks] = useState<Task[]>([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false); // State for Add Task form visibility

  const getSelectedDateString = useCallback((): string => {
    const selectedDate = date instanceof Date ? date : new Date();
    // Adjust for UTC offset to get YYYY-MM-DD local date string
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
    // IMPORTANT: Do NOT reset showAddForm here. If user changes date while form is open,
    // they might lose input. The form will be closed by handleTaskAddedOrCancelled.
  }, [fetchTasksForDate]);

  const handleTaskAddedOrCancelled = async () => {
    await fetchTasksForDate(); // Refresh the tasks for the currently selected date
    await onTaskCompleted(); // Notify App.tsx to refresh dashboard stats/daily tasks
    setShowAddForm(false); // Always close the form after creation or cancellation
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

      await fetchTasksForDate(); // Refresh tasks displayed in the calendar view
      await onTaskCompleted(); // Refresh dashboard data
    } catch (err) {
      console.error('Error completing task:', err);
      alert('Failed to complete task. See console for details.');
    }
  };

  return (
    <div className="war-map-container">
      {/* WarMapHeader now controls AddTaskForm internally */}
      <WarMapHeader
        showAddForm={showAddForm}
        onToggleAddForm={() => setShowAddForm(prev => !prev)}
        selectedDateStr={dateStr}
        onTaskActionComplete={handleTaskAddedOrCancelled} // This handles both creation and cancellation
      />

      {/* Only show the content grid if the form is NOT visible */}
      {!showAddForm && (
        <div className="map-content-grid">
          {/* Calendar Section */}
          <div className="calendar-section">
            <Calendar
              onChange={setDate}
              value={date}
              className="react-calendar-themed"
            />
          </div>

          {/* Task List Section */}
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
                      {/* Optional: you could show (Done) here if task.isCompleted for clarity */}
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