import { API_BASE_URL } from '../../config';

// frontend/src/components/WarMap/WarMapContainer.tsx
import React, { useState, useEffect, useCallback } from 'react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import './WarMap.css';
import WarMapHeader from './WarMapHeader';
import type { Task, RawTaskFromAPI } from '../../contexts/GlobalContext';
import { generateCSVTaskId } from '../../util/taskUtils';
import { brainService } from '../../services/BrainService';

type ValuePiece = Date | null;
type Value = ValuePiece | [ValuePiece, ValuePiece];

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

interface WarMapContainerProps {
  onTaskCompleted: () => Promise<void>;
}

const WarMapContainer: React.FC<WarMapContainerProps> = ({ onTaskCompleted }) => {
  const [date, setDate] = useState<Value>(new Date());
  const [dayTasks, setDayTasks] = useState<Task[]>([]);
  const [csvTasks, setCsvTasks] = useState<Slot[]>([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);

  // Briefing State
  const [briefing, setBriefing] = useState<string | null>(null);
  const [isBriefingLoading, setIsBriefingLoading] = useState(false);

  const getSelectedDateString = useCallback((): string => {
    const selectedDate = date instanceof Date ? date : new Date();
    const offset = selectedDate.getTimezoneOffset();
    const localDate = new Date(selectedDate.getTime() - (offset * 60 * 1000));
    return localDate.toISOString().split('T')[0];
  }, [date]);

  const dateStr = getSelectedDateString();

  // --- CSV Fetching Logic ---
  const parseCSV = (csvText: string): DayPlan[] => {
    const lines = csvText.split('\n').filter(line => line.trim() !== '');
    const dataRows = lines.slice(1); // Skip headers

    const dayMap: { [key: string]: DayPlan } = {};
    const completedTasks = new Set(JSON.parse(localStorage.getItem('completedTasks') || '[]'));

    dataRows.forEach((row) => {
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
      const planForDate = allPlans.find(p => p.date === dateStr);
      setCsvTasks(planForDate ? planForDate.slots : []);
    } catch (err) {
      console.error("Failed to fetch CSV plan:", err);
      setCsvTasks([]);
    }
  }, [dateStr]);

  const toggleCSVTaskStatus = (task: Slot) => {
    const completedTasks = new Set(JSON.parse(localStorage.getItem('completedTasks') || '[]'));
    const isCompleted = completedTasks.has(task.id);

    if (isCompleted) {
      completedTasks.delete(task.id);
    } else {
      completedTasks.add(task.id);
    }

    localStorage.setItem('completedTasks', JSON.stringify(Array.from(completedTasks)));

    // Refresh tasks to reflect status change
    fetchCSVTasks();

    // Trigger any parent updates if necessary (though this is local state mostly)
    onTaskCompleted();

    // Dispatch event for other components
    window.dispatchEvent(new Event('taskUpdate'));
  };

  // --- Backend Task Fetching (Existing) ---
  const fetchTasksForDate = useCallback(async () => {
    setIsLoadingTasks(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/tasks?date=${dateStr}`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch tasks for date');
      }

      const jsonResponse = await response.json();
      let rawTasks: RawTaskFromAPI[] = jsonResponse.success === false ? [] : (jsonResponse.data || jsonResponse);

      if (!Array.isArray(rawTasks)) {
        console.error("Expected array but got:", jsonResponse);
        rawTasks = [];
      }

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
    fetchCSVTasks();
  }, [fetchTasksForDate, fetchCSVTasks]);

  const handleTaskAddedOrCancelled = async () => {
    await fetchTasksForDate();
    await onTaskCompleted();
    setShowAddForm(false);
  };

  const handleTaskComplete = async (taskId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}/complete`, {
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

  const handleRequestBriefing = async () => {
    setIsBriefingLoading(true);
    try {
      // Construct context from current tasks
      const tasksContext = [...csvTasks, ...dayTasks].map(t =>
        'subject' in t ? `${t.subject}: ${t.activity} (${t.status})` : `${t.title} (${t.isCompleted ? 'Done' : 'Pending'})`
      ).join('\n');

      const response = await brainService.think(
        `Give me a strategic briefing for ${dateStr}. Here is my schedule:\n${tasksContext}`,
        { date: dateStr }
      );
      setBriefing(response.response_text);
    } catch (error) {
      setBriefing("The Oracles are silent. Connection failed.");
    } finally {
      setIsBriefingLoading(false);
    }
  };

  return (
    <div className="war-map-container">
      <WarMapHeader
        showAddForm={showAddForm}
        onToggleAddForm={() => setShowAddForm(prev => !prev)}
        selectedDateStr={dateStr}
        onTaskActionComplete={handleTaskAddedOrCancelled}
        onRequestBriefing={handleRequestBriefing}
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
              ) : (dayTasks.length > 0 || csvTasks.length > 0) ? (
                <ul className="war-map-task-list">
                  {/* CSV Study Plan Tasks */}
                  {csvTasks.map((task) => (
                    <li key={`csv-${task.id}`} className={`war-map-task-item csv-task ${task.status === 'completed' ? 'completed' : ''}`}>
                      <div className="wm-task-checkbox-wrapper">
                        <input
                          type="checkbox"
                          id={`csv-task-${task.id}`}
                          checked={task.status === 'completed'}
                          onChange={() => toggleCSVTaskStatus(task)}
                          className="google-calendar-checkbox"
                        />
                        <div className="google-event-content">
                          <label htmlFor={`csv-task-${task.id}`} className="wm-task-title-label google-link">
                            {task.subject} - {task.activity}
                            <span className="event-time"> ({task.time})</span>
                          </label>
                          {task.resource_link && (
                            <div className="google-event-description">
                              <a href={task.resource_link} target="_blank" rel="noreferrer" className="description-line">
                                🔗 Resources
                              </a>
                            </div>
                          )}
                        </div>
                      </div>
                    </li>
                  ))}

                  {/* Local Tasks */}
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

      {/* Briefing Modal */}
      {(briefing || isBriefingLoading) && (
        <div className="modal-overlay" onClick={() => !isBriefingLoading && setBriefing(null)}>
          <div className="briefing-modal" onClick={e => e.stopPropagation()}>
            <div className="briefing-header">
              <h2>🔮 Oracle's Briefing</h2>
              {!isBriefingLoading && <button onClick={() => setBriefing(null)}>×</button>}
            </div>
            <div className="briefing-content">
              {isBriefingLoading ? (
                <div className="loading-spinner">Communing with the Cortex...</div>
              ) : (
                <p>{briefing}</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WarMapContainer;