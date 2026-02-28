import { API_BASE_URL } from '../../config';

// /frontend/src/components/Quests/AddQuestForm.tsx
import React, { useState } from 'react';
import './AddQuestForm.css';

interface AddQuestFormProps {
  onQuestCreated: () => void;
  onCancel: () => void;
}

const AddQuestForm: React.FC<AddQuestFormProps> = ({ onQuestCreated, onCancel }) => {
  const [title, setTitle] = useState('');
  
  // FIX: Use string | number so we can have an empty input without NaN errors
  const [xpReward, setXpReward] = useState<string | number>(200); 
  
  const [associatedStat, setAssociatedStat] = useState<string | null>(null);
  const [dueDate, setDueDate] = useState<string>('');
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

    // Convert to number safely
    const finalXp = Number(xpReward);
    if (!finalXp || finalXp <= 0) {
      setError('XP Reward must be a positive number.');
      setSubmitting(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/quests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: title.trim(),
          xp_reward: finalXp,
          associated_stat: associatedStat,
          due_date: dueDate || null,
          isCompleted: 0,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create quest');
      }

      onQuestCreated();
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
            // FIX: Handle empty string to prevent NaN
            onChange={(e) => setXpReward(e.target.value === '' ? '' : parseInt(e.target.value))}
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