import { API_BASE_URL } from '../../config';

// frontend/src/components/WarMap/WarMapContainer.tsx
import React, { useState, useEffect, useCallback } from 'react';
import 'react-calendar/dist/Calendar.css';
import './WarMap.css';
import WarMapHeader from './WarMapHeader';
import TacticalBriefing from './TacticalBriefing';
import TerritoryNodeMap from './TerritoryNodeMap';
import type { Task, RawTaskFromAPI } from '../../contexts/GlobalContext';
import { generateCSVTaskId } from '../../util/taskUtils';

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
  const [dayTasks, setDayTasks] = useState<Task[]>([]);
  const [csvTasks, setCsvTasks] = useState<Slot[]>([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(false);
  const [briefingRefresh, setBriefingRefresh] = useState(0);

  const getSelectedDateString = useCallback((): string => {
    const selectedDate = new Date();
    const offset = selectedDate.getTimezoneOffset();
    const localDate = new Date(selectedDate.getTime() - (offset * 60 * 1000));
    return localDate.toISOString().split('T')[0];
  }, []);

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
      // Inform briefing to recount pending tasks 
      setBriefingRefresh(prev => prev + 1);
    } catch (err) {
      console.error('Error completing task:', err);
      alert('Failed to complete task. See console for details.');
    }
  };

  return (
    <div className="war-map-container">
      <WarMapHeader
        selectedDateStr={dateStr}
        showAddForm={false}
        onToggleAddForm={() => { }}
        onTaskActionComplete={() => { }}
      />

      <div className="command-center-layout">
        <div className="command-left-panel">
          <TacticalBriefing refreshTrigger={briefingRefresh} dayTasks={dayTasks} csvTasks={csvTasks} />

          <div className="daily-targets-panel panel-glass">
            <div className="panel-header">
              <h3>⚡ ACTIVE TARGETS ({dayTasks.length + csvTasks.length})</h3>
            </div>

            {isLoadingTasks ? (
              <div className="loading-state">Synchronizing Database...</div>
            ) : (
              <div className="tasks-scroll-list custom-scrollbar">
                {/* Database Tasks */}
                {dayTasks.map(task => (
                  <div key={`db-${task.id}`} className={`target-item ${task.isCompleted ? 'completed' : ''}`}>
                    <div className="target-info">
                      <strong>{task.title}</strong>
                      <span className="reward-badge">+{task.xp_reward} {task.associated_stat?.toUpperCase()}</span>
                    </div>
                    <button
                      className={`status-btn ${task.isCompleted ? 'done' : 'engage'}`}
                      onClick={() => !task.isCompleted && handleTaskComplete(task.id!)}
                    >
                      {task.isCompleted ? 'SECURED' : 'ENGAGE'}
                    </button>
                  </div>
                ))}

                {/* CSV Study Tasks */}
                {csvTasks.map(slot => {
                  const isCompleted = slot.status === 'completed';
                  return (
                    <div key={slot.id} className={`target-item csv-task ${isCompleted ? 'completed' : ''}`}>
                      <div className="target-info">
                        <div className="time-badge">{slot.time}</div>
                        <strong>{slot.subject}</strong>
                        <div className="topic-text">{slot.activity}</div>
                      </div>
                      <button
                        className={`status-btn ${isCompleted ? 'done' : 'engage'}`}
                        onClick={() => toggleCSVTaskStatus(slot)}
                      >
                        {isCompleted ? 'SECURED' : 'ENGAGE'}
                      </button>
                    </div>
                  );
                })}

                {dayTasks.length === 0 && csvTasks.length === 0 && (
                  <div className="empty-state">No active targets assigned.</div>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="command-right-panel">
          <TerritoryNodeMap />
        </div>
      </div>
    </div>
  );
};

export default WarMapContainer;