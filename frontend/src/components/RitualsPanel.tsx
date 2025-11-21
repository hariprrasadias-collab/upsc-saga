// /frontend/src/components/RitualsPanel.tsx
import React from 'react';
import './RitualsPanel.css';
// Import Task interface from App.tsx
import type { Task } from '../App';

interface RitualsPanelProps {
  tasks: Task[];
  onTaskComplete: (taskId: number) => void;
}

const RitualsPanel: React.FC<RitualsPanelProps> = ({ tasks, onTaskComplete }) => {
  return (
    <div className="rituals-panel">
      <div className="rituals-header">
        <h2>TODAY'S RITUALS</h2>
      </div>
      <ul className="rituals-list">
        {tasks.length === 0 ? (
          <p className="no-tasks-message">No rituals due today. Forge new ones on the War Map!</p>
        ) : (
          tasks.map(task => (
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
                <span className="task-xp">+{task.xp_reward} XP</span>
              </div>
            </li>
          ))
        )}
      </ul>
      <button className="add-ritual-btn" style={{ marginTop: 'auto', alignSelf: 'center' }}>
        PLAN MORE RITUALS
      </button>
    </div>
  );
};

export default RitualsPanel;