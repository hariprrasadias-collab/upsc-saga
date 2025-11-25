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
  onTaskCompleted: () => Promise<void>;
}

const WarMapContainer: React.FC<WarMapContainerProps> = ({ onTaskCompleted }) => {
  const [date, setDate] = useState<Value>(new Date());
  const [dayTasks, setDayTasks] = useState<Task[]>([]);
  const [googleEvents, setGoogleEvents] = useState<any[]>([]);
  const [completedGoogleEvents, setCompletedGoogleEvents] = useState<Set<string>>(new Set());
  const [isLoadingTasks, setIsLoadingTasks] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [isGoogleConnected, setIsGoogleConnected] = useState(false);

  // New states for event management
  const [editingEventId, setEditingEventId] = useState<string | null>(null);
  const [eventXP, setEventXP] = useState<Record<string, number>>({});
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);

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

  const fetchGoogleEvents = useCallback(async () => {
    try {
      const res = await fetch(`http://localhost:5000/api/warmap/google-events?date=${dateStr}`);
      if (res.ok) {
        const events = await res.json();
        setGoogleEvents(events);

        // Fetch XP metadata for each event
        for (const event of events) {
          const metaRes = await fetch(`http://localhost:5000/api/warmap/google-events/${event.id}/metadata`);
          if (metaRes.ok) {
            const metadata = await metaRes.json();
            setEventXP(prev => ({ ...prev, [event.id]: metadata.xp_reward || 0 }));
          }
        }
      } else {
        console.error("Failed to fetch Google events");
      }
    } catch (err) {
      console.error("Error fetching Google events:", err);
    }
  }, [dateStr]);

  const checkConnectionStatus = useCallback(async () => {
    try {
      const res = await fetch('http://localhost:5000/api/warmap/status');
      if (res.ok) {
        const data = await res.json();
        if (data.connected) {
          setIsGoogleConnected(true);
        }
      }
    } catch (err) {
      console.error("Error checking connection status:", err);
    }
  }, []);

  useEffect(() => {
    fetchTasksForDate();
  }, [fetchTasksForDate]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('status') === 'connected') {
      setIsGoogleConnected(true);
      window.history.replaceState({}, '', window.location.pathname);
    } else {
      checkConnectionStatus();
    }
  }, [checkConnectionStatus]);

  useEffect(() => {
    if (isGoogleConnected) {
      fetchGoogleEvents();
    }
  }, [dateStr, isGoogleConnected, fetchGoogleEvents]);

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

  const handleConnectGoogle = () => {
    window.location.href = 'http://localhost:5000/api/warmap/google-auth';
  };

  const handleGoogleEventToggle = async (eventId: string) => {
    const isCurrentlyCompleted = completedGoogleEvents.has(eventId);

    // Update local state immediately
    setCompletedGoogleEvents(prev => {
      const newSet = new Set(prev);
      if (isCurrentlyCompleted) {
        newSet.delete(eventId);
      } else {
        newSet.add(eventId);
      }
      return newSet;
    });

    // Sync to Google Calendar
    try {
      const endpoint = isCurrentlyCompleted ? 'uncomplete' : 'complete';
      await fetch(`http://localhost:5000/api/warmap/google-events/${eventId}/${endpoint}`, {
        method: 'POST'
      });
    } catch (err) {
      console.error('Failed to sync completion:', err);
    }

    // Sync with main app (Rituals Panel)
    await onTaskCompleted();
  };

  const handleDeleteEvent = async (eventId: string) => {
    if (!window.confirm('Are you sure you want to delete this event from Google Calendar? This cannot be undone.')) {
      setShowDeleteConfirm(null);
      return;
    }

    try {
      const res = await fetch(`http://localhost:5000/api/warmap/google-events/${eventId}`, {
        method: 'DELETE'
      });

      if (res.ok) {
        await fetchGoogleEvents();
        setShowDeleteConfirm(null);
      } else {
        alert('Failed to delete event');
      }
    } catch (err) {
      console.error('Error deleting event:', err);
      alert('Failed to delete event');
    }
  };

  const handleSaveXP = async (eventId: string, xp: number) => {
    try {
      await fetch(`http://localhost:5000/api/warmap/google-events/${eventId}/metadata`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ xp_reward: xp })
      });
      setEventXP(prev => ({ ...prev, [eventId]: xp }));
      setEditingEventId(null);
    } catch (err) {
      console.error('Error saving XP:', err);
    }
  };

  return (
    <div className="war-map-container">
      <WarMapHeader
        showAddForm={showAddForm}
        onToggleAddForm={() => setShowAddForm(prev => !prev)}
        selectedDateStr={dateStr}
        onTaskActionComplete={handleTaskAddedOrCancelled}
        onConnectGoogle={handleConnectGoogle}
        isGoogleConnected={isGoogleConnected}
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
              ) : (dayTasks.length > 0 || googleEvents.length > 0) ? (
                <ul className="war-map-task-list">
                  {/* Google Calendar Events */}
                  {googleEvents.map((event) => {
                    const isCompleted = completedGoogleEvents.has(event.id);
                    const xp = eventXP[event.id] || 0;

                    return (
                      <li key={`g-${event.id}`} className={`war-map-task-item google-event ${isCompleted ? 'completed' : ''}`}>
                        <div className="wm-task-checkbox-wrapper">
                          <input
                            type="checkbox"
                            id={`google-event-${event.id}`}
                            checked={isCompleted}
                            onChange={() => handleGoogleEventToggle(event.id)}
                            className="google-calendar-checkbox"
                          />
                          <div className="google-event-content">
                            <label htmlFor={`google-event-${event.id}`} className="wm-task-title-label google-link">
                              {event.title}
                              <span className="event-time"> ({new Date(event.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })})</span>
                            </label>
                            {event.description && (
                              <div className="google-event-description">
                                {event.description.split('\n').map((line: string, i: number) => (
                                  <div key={i} className="description-line">{line}</div>
                                ))}
                              </div>
                            )}

                            {/* XP Editor */}
                            <div className="event-xp-section">
                              {editingEventId === event.id ? (
                                <div className="xp-editor">
                                  <input
                                    type="number"
                                    value={xp}
                                    onChange={(e) => setEventXP(prev => ({ ...prev, [event.id]: parseInt(e.target.value) || 0 }))}
                                    placeholder="XP"
                                    className="xp-input"
                                  />
                                  <button onClick={() => handleSaveXP(event.id, xp)} className="save-xp-btn">✓</button>
                                  <button onClick={() => setEditingEventId(null)} className="cancel-xp-btn">✗</button>
                                </div>
                              ) : (
                                <div className="xp-display">
                                  <span className="xp-value">{xp > 0 ? `+${xp} XP` : 'No XP'}</span>
                                  <button onClick={() => setEditingEventId(event.id)} className="edit-xp-btn">Edit XP</button>
                                </div>
                              )}
                            </div>

                            {/* Event Actions */}
                            <div className="event-actions">
                              <button
                                onClick={() => handleDeleteEvent(event.id)}
                                className="delete-event-btn"
                                title="Delete from Google Calendar"
                              >
                                🗑️ Delete
                              </button>
                            </div>
                          </div>
                        </div>
                      </li>
                    );
                  })}

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
    </div>
  );
};

export default WarMapContainer;