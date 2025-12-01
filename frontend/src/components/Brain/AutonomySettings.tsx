import React, { useState, useEffect } from 'react';
import './AutonomySettings.css';
import { FaRobot, FaShieldAlt, FaHistory, FaChartLine, FaCheck } from 'react-icons/fa';

interface AutonomyStats {
    total_actions: number;
    auto_executed_count: number;
    auto_execution_rate: number;
    average_success_score: number;
}

interface ActionLogItem {
    id: number;
    type: string;
    label: string;
    executed_by: 'manual' | 'auto';
    executed_at: string;
    status: 'success' | 'failure' | 'pending' | 'ignored';
    impact_score: number;
    reasoning: string;
}

interface LearnedPattern {
    type: string;
    data: any;
    confidence: number;
    observations: number;
}

const AutonomySettings: React.FC = () => {
    const [autonomyLevel, setAutonomyLevel] = useState<string>('manual');
    const [stats, setStats] = useState<AutonomyStats | null>(null);
    const [actionLog, setActionLog] = useState<ActionLogItem[]>([]);
    const [patterns, setPatterns] = useState<LearnedPattern[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'settings' | 'logs' | 'patterns'>('settings');

    useEffect(() => {
        fetchSettings();
        fetchActionLog();
        fetchPatterns();
    }, []);

    const fetchSettings = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/autonomy/settings');
            const data = await response.json();
            setAutonomyLevel(data.autonomy_level);
            setStats(data.stats);
        } catch (error) {
            console.error('Failed to fetch autonomy settings:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const fetchActionLog = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/autonomy/action_log?limit=20');
            const data = await response.json();
            setActionLog(data.actions || []);
        } catch (error) {
            console.error('Failed to fetch action log:', error);
        }
    };

    const fetchPatterns = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/autonomy/learned_patterns');
            const data = await response.json();
            setPatterns(data.patterns || []);
        } catch (error) {
            console.error('Failed to fetch learned patterns:', error);
        }
    };

    const handleLevelChange = async (newLevel: string) => {
        try {
            const response = await fetch('http://localhost:5000/api/autonomy/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ autonomy_level: newLevel }),
            });

            if (response.ok) {
                setAutonomyLevel(newLevel);
            }
        } catch (error) {
            console.error('Failed to update autonomy level:', error);
        }
    };

    const getImpactColor = (score: number) => {
        if (score > 0.5) return '#4caf50';
        if (score > 0) return '#8bc34a';
        if (score > -0.3) return '#ffeb3b';
        return '#f44336';
    };

    if (isLoading) {
        return <div className="autonomy-loading">Loading Neural Configuration...</div>;
    }

    return (
        <div className="autonomy-container">
            <div className="autonomy-header">
                <h2><FaRobot /> Autonomous Brain Control</h2>
                <div className="autonomy-tabs">
                    <button
                        className={activeTab === 'settings' ? 'active' : ''}
                        onClick={() => setActiveTab('settings')}
                    >
                        <FaShieldAlt /> Settings
                    </button>
                    <button
                        className={activeTab === 'logs' ? 'active' : ''}
                        onClick={() => setActiveTab('logs')}
                    >
                        <FaHistory /> Action Log
                    </button>
                    <button
                        className={activeTab === 'patterns' ? 'active' : ''}
                        onClick={() => setActiveTab('patterns')}
                    >
                        <FaChartLine /> Learned Patterns
                    </button>
                </div>
            </div>

            {activeTab === 'settings' && (
                <div className="autonomy-content settings-view">
                    <div className="level-selector">
                        <h3>Autonomy Level</h3>
                        <div className="level-options">
                            <div
                                className={`level-option ${autonomyLevel === 'manual' ? 'selected' : ''}`}
                                onClick={() => handleLevelChange('manual')}
                            >
                                <div className="level-icon"><FaCheck /></div>
                                <div className="level-info">
                                    <h4>Manual</h4>
                                    <p>Brain suggests actions, you approve everything.</p>
                                </div>
                            </div>
                            <div
                                className={`level-option ${autonomyLevel === 'semi_auto' ? 'selected' : ''}`}
                                onClick={() => handleLevelChange('semi_auto')}
                            >
                                <div className="level-icon"><FaShieldAlt /></div>
                                <div className="level-info">
                                    <h4>Semi-Auto</h4>
                                    <p>Auto-executes safe actions (curation, scheduling).</p>
                                </div>
                            </div>
                            <div
                                className={`level-option ${autonomyLevel === 'full_auto' ? 'selected' : ''}`}
                                onClick={() => handleLevelChange('full_auto')}
                            >
                                <div className="level-icon"><FaRobot /></div>
                                <div className="level-info">
                                    <h4>Full Auto</h4>
                                    <p>Independent operation with oversight.</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="autonomy-stats">
                        <h3>Performance Stats</h3>
                        <div className="stats-grid">
                            <div className="stat-card">
                                <span className="stat-value">{stats?.total_actions || 0}</span>
                                <span className="stat-label">Total Actions</span>
                            </div>
                            <div className="stat-card">
                                <span className="stat-value">{stats?.auto_executed_count || 0}</span>
                                <span className="stat-label">Auto-Executed</span>
                            </div>
                            <div className="stat-card">
                                <span className="stat-value">{(stats?.average_success_score || 0).toFixed(2)}</span>
                                <span className="stat-label">Avg Impact Score</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'logs' && (
                <div className="autonomy-content logs-view">
                    <div className="logs-list">
                        {actionLog.length === 0 ? (
                            <div className="empty-state">No actions recorded yet.</div>
                        ) : (
                            actionLog.map(action => (
                                <div key={action.id} className="log-item">
                                    <div className="log-header">
                                        <span className={`log-type ${action.type.toLowerCase()}`}>{action.type}</span>
                                        <span className="log-time">{new Date(action.executed_at).toLocaleString()}</span>
                                    </div>
                                    <div className="log-details">
                                        <p className="log-reason">{action.reasoning}</p>
                                        <div className="log-meta">
                                            <span className={`log-executor ${action.executed_by}`}>
                                                {action.executed_by === 'auto' ? <FaRobot /> : <FaCheck />} {action.executed_by}
                                            </span>
                                            <span className="log-impact" style={{ color: getImpactColor(action.impact_score) }}>
                                                Impact: {action.impact_score?.toFixed(2) || 'N/A'}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}

            {activeTab === 'patterns' && (
                <div className="autonomy-content patterns-view">
                    <div className="patterns-list">
                        {patterns.length === 0 ? (
                            <div className="empty-state">No patterns learned yet.</div>
                        ) : (
                            patterns.map((pattern, index) => (
                                <div key={index} className="pattern-card">
                                    <div className="pattern-header">
                                        <span className="pattern-type">{pattern.type.replace('_', ' ')}</span>
                                        <span className="pattern-confidence">
                                            {(pattern.confidence * 100).toFixed(0)}% Confidence
                                        </span>
                                    </div>
                                    <div className="pattern-body">
                                        <pre>{JSON.stringify(pattern.data, null, 2)}</pre>
                                    </div>
                                    <div className="pattern-footer">
                                        Observed {pattern.observations} times
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default AutonomySettings;
