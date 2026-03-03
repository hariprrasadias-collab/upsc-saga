import { API_BASE_URL } from '../../config';

// /frontend/src/components/Quests/QuestsPage.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './QuestsPage.css';
import type { Task, RawTaskFromAPI } from '../../contexts/GlobalContext';
import AddQuestForm from './AddQuestForm';
import { brainService } from '../../services/BrainService';

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
      const response = await fetch(`${API_BASE_URL}/api/quests`);

      if (!response.ok) {
        throw new Error('Failed to fetch quests');
      }

      const jsonResponse = await response.json();
      const rawTasks: RawTaskFromAPI[] = jsonResponse.success === false ? [] : (jsonResponse.data || jsonResponse);

      if (!Array.isArray(rawTasks)) {
        throw new Error('API returned invalid format for quests');
      }

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
      const response = await fetch(`${API_BASE_URL}/api/quests/${questId}/complete`, {
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

  const handleGenerateQuests = async () => {
    setIsLoading(true);
    try {
      const result = await brainService.executeAction('GENERATE_QUESTS', {});
      if (result.success) {
        alert(result.message);
        await fetchQuests();
      } else {
        alert("Failed to generate quests: " + result.message);
      }
    } catch (err) {
      console.error("Brain Quest Generation Error:", err);
      alert("The Oracle is silent.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="quests-page-container">
      <div className="quests-header">
        <h1>Quests Journal</h1>
        <p>Embark on grand campaigns and achieve long-term objectives.</p>
        <div className="quest-actions">
          <button className="add-quest-btn" onClick={() => setShowAddForm(true)}>
            New Campaign (Add Quest)
          </button>
          <button
            className="add-quest-btn brain-quest-btn"
            onClick={handleGenerateQuests}
            style={{ marginLeft: '10px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
            disabled={isLoading}
          >
            {isLoading ? 'Consulting Oracle...' : '🔮 Generate Quests (Brain)'}
          </button>
        </div>
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
            <motion.div layout className="quest-grid">
              <AnimatePresence>
                {quests.map((quest) => (
                  <motion.div
                    key={quest.id}
                    className={`quest-card ${quest.isCompleted ? 'completed' : ''}`}
                    initial={{ opacity: 0, scale: 0.9, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.5, filter: 'blur(10px)', transition: { duration: 0.5 } }}
                    layout
                  >
                    <div className="quest-card-header">
                      <h3 className="quest-title">{quest.title}</h3>
                      <span className="quest-xp">+{quest.xp_reward} XP</span>
                    </div>

                    <div className="quest-card-body">
                      {quest.due_date && <span className="quest-due-date">Due: {quest.due_date}</span>}
                      {quest.associated_stat && <span className="quest-stat-badge">{quest.associated_stat.toUpperCase()}</span>}
                    </div>

                    <div className="quest-card-footer">
                      <button
                        className={`quest-action-btn ${quest.isCompleted ? 'btn-completed' : ''}`}
                        onClick={() => handleQuestComplete(quest.id)}
                        disabled={quest.isCompleted}
                      >
                        {quest.isCompleted ? 'CLAIMED' : 'COMPLETE MISSION'}
                      </button>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </motion.div>
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