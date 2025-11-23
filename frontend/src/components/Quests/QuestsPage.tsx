// /frontend/src/components/Quests/QuestsPage.tsx
import React, { useState, useEffect, useCallback } from 'react';
import './QuestsPage.css';
import type { Task, RawTaskFromAPI } from '../../App'; // Import types from App
import AddQuestForm from './AddQuestForm';

interface QuestsPageProps {
  onTaskCompleted: () => Promise<void>;
}

const QuestsPage: React.FC<QuestsPageProps> = ({ onTaskCompleted }) => {
  const [quests, setQuests] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);

  // --- FIX: Fetch from the specific /api/quests endpoint ---
  const fetchQuests = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // CRITICAL FIX: Use '/api/quests', NOT '/api/tasks'
      const response = await fetch('http://localhost:5000/api/quests');
      
      if (!response.ok) {
        throw new Error('Failed to fetch quests');
      }
      
      const rawTasks: RawTaskFromAPI[] = await response.json();
      
      // Map API data to frontend Task interface
      const allQuests: Task[] = rawTasks.map(task => ({
        id: task.id,
        title: task.title,
        isCompleted: task.isCompleted === 1, // Convert 1/0 to boolean
        xp_reward: task.xp_reward,
        associated_stat: task.associated_stat,
        due_date: task.due_date,
      }));
      
      setQuests(allQuests);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unknown error occurred while fetching quests.");
      }
      console.error('Error fetching quests:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load quests on mount
  useEffect(() => {
    fetchQuests();
  }, [fetchQuests]);

  const handleQuestComplete = async (questId: number) => {
    try {
      const response = await fetch(`http://localhost:5000/api/quests/${questId}/complete`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to complete quest');
      }

      await fetchQuests();   // Refresh list locally
      await onTaskCompleted(); // Trigger global update (XP, Level, Sidebar)
    } catch (err) {
      console.error('Error completing quest:', err);
      alert('Failed to complete quest. See console for details.');
    }
  };

  // Callback for when the form submits successfully
  const handleQuestAddedOrCancelled = async () => {
    await fetchQuests(); // Re-fetch the list to see the new quest immediately
    setShowAddForm(false);
    await onTaskCompleted(); // Update dashboard stats just in case
  };

  return (
    <div className="quests-page-container">
      <div className="quests-header">
        <h1>Quests Journal</h1>
        <p>Embark on grand campaigns and achieve long-term objectives.</p>
        <button className="add-quest-btn" onClick={() => setShowAddForm(true)}>
          New Campaign (Add Quest)
        </button>
      </div>

      {showAddForm && (
        <AddQuestForm
          onQuestCreated={handleQuestAddedOrCancelled}
          onCancel={handleQuestAddedOrCancelled}
        />
      )}

      {!showAddForm && (
        <div className="quests-list-section">
          <h2>Active Campaigns</h2>
          {isLoading ? (
            <div className="loading-message">Unfurling the quest scrolls...</div>
          ) : error ? (
            <div className="error-message">Error: {error}</div>
          ) : quests.length > 0 ? (
            <ul className="quest-list">
              {quests.map((quest) => (
                <li key={quest.id} className={`quest-item ${quest.isCompleted ? 'completed' : ''}`}>
                  <div className="quest-checkbox-wrapper">
                    <input
                      type="checkbox"
                      id={`quest-${quest.id}`}
                      checked={quest.isCompleted}
                      onChange={() => handleQuestComplete(quest.id)}
                      disabled={quest.isCompleted}
                    />
                    <label htmlFor={`quest-${quest.id}`} className="quest-title-label">
                      {quest.title}
                      {quest.due_date && <span className="quest-due-date"> (Due: {quest.due_date})</span>}
                    </label>
                  </div>
                  <span className="quest-xp">+{quest.xp_reward} XP</span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="empty-quests-message">
              No active campaigns. Time to forge a new destiny!
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default QuestsPage;