// /frontend/src/components/WarMap/AddTaskForm.tsx
import React, { useState } from 'react';
import './AddTaskForm.css'; // Make sure this CSS file exists

interface AddTaskFormProps {
  selectedDateStr: string; // The date for which the task is being added
  onTaskCreated: () => void; // Callback to refresh tasks and close form
  onCancel: () => void; // Callback to close form without creating task
}

const AddTaskForm: React.FC<AddTaskFormProps> = ({ selectedDateStr, onTaskCreated, onCancel }) => {
  const [title, setTitle] = useState('');
  const [xpReward, setXpReward] = useState<number>(50); // Default XP
  const [associatedStat, setAssociatedStat] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    if (!title.trim()) {
      setError('Ritual Title cannot be empty.');
      setSubmitting(false);
      return;
    }
    if (xpReward <= 0) {
      setError('XP Reward must be a positive number.');
      setSubmitting(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: title.trim(),
          xp_reward: xpReward,
          associated_stat: associatedStat,
          due_date: selectedDateStr, // Use the selected date from WarMap
          isCompleted: 0, // New tasks are not completed
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create ritual');
      }

      onTaskCreated(); // Trigger refresh in parent and close form
    } catch (err) {
      console.error('Error creating task:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unknown error occurred while creating the ritual.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="add-task-form">
      <h3>Forge New Ritual for {selectedDateStr}</h3>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="ritual-title">Ritual Title:</label>
          <input
            type="text"
            id="ritual-title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., Complete Chapter 3 of Polity"
            required
            disabled={submitting}
          />
        </div>

        <div className="form-group">
          <label htmlFor="xp-reward">XP Reward:</label>
          <input
            type="number"
            id="xp-reward"
            value={xpReward}
            onChange={(e) => setXpReward(parseInt(e.target.value))}
            min="1"
            required
            disabled={submitting}
          />
        </div>

        <div className="form-group">
          <label htmlFor="associated-stat">Associated Stat:</label>
          <select
            id="associated-stat"
            value={associatedStat || ''}
            onChange={(e) => setAssociatedStat(e.target.value || null)}
            disabled={submitting}
          >
            <option value="">None</option>
            <option value="strength_stat">Strength (GS-I)</option>
            <option value="runic_stat">Runic (GS-II)</option>
            <option value="vitality_stat">Vitality (GS-III)</option>
            <option value="luck_stat">Luck (GS-IV & Essay)</option>
          </select>
        </div>

        <div className="form-actions">
          <button type="button" onClick={onCancel} disabled={submitting}>
            Cancel
          </button>
          <button type="submit" disabled={submitting}>
            {submitting ? 'Forging...' : 'Forge Ritual'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AddTaskForm;