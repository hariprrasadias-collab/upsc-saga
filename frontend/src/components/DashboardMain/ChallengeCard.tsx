// Daily Challenge Card Component
import React, { useState, useEffect } from 'react';
import './ChallengeCard.css';
import { API_BASE_URL } from '../../config';
import { useGlobal } from '../../contexts/GlobalContext';
import { useToast, ToastContainer } from '../Toast';

interface Challenge {
    id: number;
    title: string;
    description: string;
    type: string;
    target_value: number;
    xp_reward: number;
    completed: boolean;
    progress: number;
}

const ChallengeCard: React.FC = () => {
    const [challenge, setChallenge] = useState<Challenge | null>(null);
    const [loading, setLoading] = useState(true);
    const [streak, setStreak] = useState(0);

    const { refreshDashboard } = useGlobal();
    const { toasts, addToast, removeToast } = useToast();

    useEffect(() => {
        fetchChallenge();
        fetchStreak();
    }, []);

    const fetchChallenge = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/challenges/daily`);
            if (res.ok) {
                const data = await res.json();
                setChallenge(data);
            }
        } catch (err) {
            console.error('Error fetching challenge:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchStreak = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/challenges/streak`);
            if (res.ok) {
                const data = await res.json();
                setStreak(data.current_streak || 0);
            }
        } catch (err) {
            console.error('Error fetching streak:', err);
        }
    };

    const handleComplete = async () => {
        if (!challenge || challenge.completed) return;

        try {
            const res = await fetch(`${API_BASE_URL}/api/challenges/complete`, {
                method: 'POST'
            });

            if (res.ok) {
                const data = await res.json();
                addToast(`Challenge completed! +${data.xp_awarded} XP`, 'success');
                fetchChallenge();
                fetchStreak();

                // Refresh page stats using global context instead of page reload
                await refreshDashboard();
            } else {
                addToast('Failed to complete challenge', 'error');
            }
        } catch (err) {
            console.error('Error completing challenge:', err);
            addToast('Error completing challenge', 'error');
        }
    };

    if (loading) {
        return (
            <div className="challenge-card loading">
                <p>Loading today's challenge...</p>
            </div>
        );
    }

    if (!challenge) {
        return (
            <div className="challenge-card error">
                <p>No challenge available today</p>
            </div>
        );
    }

    const progress = challenge.completed ? 100 : (challenge.progress / challenge.target_value) * 100;

    return (
        <div className={`challenge-card ${challenge.completed ? 'completed' : ''}`}>
            {/* Toast Container for notifications */}
            <ToastContainer toasts={toasts} removeToast={removeToast} />

            <div className="challenge-header">
                <h3>🎯 Daily Challenge</h3>
                <div className="streak-badge">
                    🔥 {streak} day{streak !== 1 ? 's' : ''}
                </div>
            </div>

            <div className="challenge-body">
                <h4>{challenge.title}</h4>
                <p>{challenge.description}</p>

                <div className="challenge-progress">
                    <div
                        className="progress-bar"
                        role="progressbar"
                        aria-valuenow={challenge.completed ? challenge.target_value : challenge.progress}
                        aria-valuemin={0}
                        aria-valuemax={challenge.target_value}
                        aria-label={`Progress for ${challenge.title}`}
                    >
                        <div
                            className="progress-fill"
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>
                    <span className="progress-text">
                        {challenge.progress} / {challenge.target_value}
                    </span>
                </div>

                <div className="challenge-footer">
                    <span className="reward">+{challenge.xp_reward} XP</span>
                    {challenge.completed ? (
                        <div className="completed-badge">✅ Completed</div>
                    ) : (
                        <button
                            className="complete-btn"
                            onClick={handleComplete}
                        >
                            Mark Complete
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ChallengeCard;
