// /frontend/src/components/Quests/AddQuestForm.tsx
import React, { useState } from 'react';
import './AddQuestForm.css'; // New CSS file for this form

interface AddQuestFormProps {
  onQuestCreated: () => void; // Callback to refresh quests and close form
  onCancel: () => void; // Callback to close form without creating quest
}

const AddQuestForm: React.FC<AddQuestFormProps> = ({ onQuestCreated, onCancel }) => {
  const [title, setTitle] = useState('');
  const [xpReward, setXpReward] = useState<number>(100); // Default XP for quests might be higher
  const [associatedStat, setAssociatedStat] = useState<string | null>(null);
  const [dueDate, setDueDate] = useState<string>(''); // Quests can have optional due dates
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    if (!title.trim()) {
      setError('Quest Title cannot be empty.');
      setSubmitting(false);
      return;
    }
    if (xpReward <= 0) {
      setError('XP Reward must be a positive number.');
      setSubmitting(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/quests', { // New endpoint for quests
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: title.trim(),
          xp_reward: xpReward,
          associated_stat: associatedStat,
          due_date: dueDate || null, // Pass null if empty string
          isCompleted: 0, // New quests are not completed
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create quest');
      }

      onQuestCreated(); // Trigger refresh in parent and close form
    } catch (err) {
      console.error('Error creating quest:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unknown error occurred while creating the quest.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="add-quest-form">
      <h3>Embark on a New Quest</h3>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="quest-title">Quest Title:</label>
          <input
            type="text"
            id="quest-title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., Master UPSC History Syllabus"
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

        <div className="form-group">
          <label htmlFor="due-date">Due Date (Optional):</label>
          <input
            type="date"
            id="due-date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            disabled={submitting}
          />
        </div>

        <div className="form-actions">
          <button type="button" onClick={onCancel} disabled={submitting}>
            Cancel
          </button>
          <button type="submit" disabled={submitting}>
            {submitting ? 'Initiating...' : 'Initiate Quest'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AddQuestForm;