import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './Panopticon.css';
import { brainService } from '../../services/BrainService';
import MarkdownRenderer from '../Shared/MarkdownRenderer';

interface BioMetric {
    date: string;
    sleep_hours: number;
    mood_score: number;
    energy_level: number;
    notes: string;
}

interface Correlation {
    metric_name: string;
    performance_metric: string;
    correlation_coefficient: number;
    insight_text: string;
}

const Panopticon: React.FC = () => {
    const [metrics, setMetrics] = useState<BioMetric[]>([]);
    const [correlations, setCorrelations] = useState<Correlation[]>([]);
    const [showLogModal, setShowLogModal] = useState(false);
    const [loading, setLoading] = useState(true);
    const [biohack, setBiohack] = useState<string | null>(null);
    const [isThinking, setIsThinking] = useState(false);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/panopticon/dashboard`);
            const data = await response.json();
            if (data.success) {
                setMetrics(data.data.recent_metrics);
                setCorrelations(data.data.correlations);
            }
        } catch (error) {
            console.error('Failed to fetch Panopticon data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleGetBiohack = async () => {
        setIsThinking(true);
        try {
            // Use latest metrics if available
            const latest = metrics[0] || {};
            const payload = {
                metrics: {
                    sleep: latest.sleep_hours,
                    energy: latest.energy_level,
                    mood: latest.mood_score
                }
            };
            const result = await brainService.executeAction('SUGGEST_BIOHACK', payload);
            if (result.success) {
                setBiohack(result.suggestion);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setIsThinking(false);
        }
    };

    return (
        <div className="panopticon-container">
            <header className="panopticon-header">
                <h1>The Panopticon 👁️</h1>
                <p>Bio-Rhythm Correlation Engine</p>
                <h1>The Panopticon 👁️</h1>
                <p>Bio-Rhythm Correlation Engine</p>
                <button
                    onClick={handleGetBiohack}
                    disabled={isThinking}
                    className="btn-primary"
                    style={{ marginLeft: '20px', borderRadius: '20px' }}
                >
                    {isThinking ? 'Analyzing...' : '🧠 Strategos Analysis'}
                </button>
            </header>

            {biohack && (
                <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="biohack-panel glass-panel"
                    style={{
                        borderColor: 'var(--color-accent-blue)',
                        padding: '15px',
                        margin: '0 20px 20px',
                        borderRadius: '8px',
                        color: 'var(--color-text-primary)'
                    }}
                >
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <h3 className="neon-text-blue">🧬 Optimization Protocol</h3>
                        <button  onClick={() => setBiohack(null)} style={{ background: 'none', border: 'none', color: 'var(--color-text-primary)', cursor: 'pointer' }} aria-label="Close"><span aria-hidden="true">✕</span></button>
                    </div>
                    <MarkdownRenderer content={biohack} />
                </motion.div>
            )}

            <div className="panopticon-grid">
                {/* Correlation Cards */}
                <section className="correlations-section">
                    <h2 className="neon-text-blue">Neural Links</h2>
                    <div className="cards-row">
                        {correlations.map((corr, idx) => (
                            <motion.div
                                key={idx}
                                className="correlation-card glass-panel"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.1 }}
                            >
                                <div className="corr-header">
                                    <span className="metric-tag">{corr.metric_name.replace('_', ' ')}</span>
                                    <span className="arrow">→</span>
                                    <span className="perf-tag">{corr.performance_metric.replace('_', ' ')}</span>
                                </div>
                                <div className="corr-value" style={{
                                    color: corr.correlation_coefficient > 0.5 ? 'var(--color-accent-green)' :
                                        corr.correlation_coefficient < -0.5 ? 'var(--color-error)' : 'var(--color-text-secondary)'
                                }}>
                                    r = {corr.correlation_coefficient.toFixed(2)}
                                </div>
                                <p className="insight-text">{corr.insight_text}</p>
                            </motion.div>
                        ))}
                        {correlations.length === 0 && !loading && (
                            <div className="empty-state">
                                Not enough data to find correlations yet. Keep logging!
                            </div>
                        )}
                    </div>
                </section>

                {/* Recent Logs */}
                <section className="history-section">
                    <div className="section-header">
                        <h2 className="neon-text-orange">Recent Bio-Logs</h2>
                        <button className="log-btn btn-primary" onClick={() => setShowLogModal(true)}>
                            + Log Daily Stats
                        </button>
                    </div>
                    <div className="logs-list">
                        {metrics.map((m, idx) => (
                            <div key={idx} className="log-item glass-panel">
                                <span className="log-date">{m.date}</span>
                                <div className="log-stats">
                                    <span>😴 {m.sleep_hours}h</span>
                                    <span>😊 {m.mood_score}/10</span>
                                    <span>⚡ {m.energy_level}/10</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            </div>

            {/* Log Modal */}
            <AnimatePresence>
                {showLogModal && (
                    <LogModal onClose={() => setShowLogModal(false)} onSave={fetchDashboardData} />
                )}
            </AnimatePresence>
        </div>
    );
};

const LogModal: React.FC<{ onClose: () => void, onSave: () => void }> = ({ onClose, onSave }) => {
    const [formData, setFormData] = useState({
        date: new Date().toISOString().split('T')[0],
        sleep_hours: 7,
        mood_score: 5,
        energy_level: 5,
        notes: ''
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await fetch(`${API_BASE_URL}/api/panopticon/log`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            onSave();
            onClose();
        } catch (error) {
            console.error('Failed to log metrics:', error);
        }
    };

    return (
        <div className="modal-backdrop" onClick={onClose}>
            <motion.div
                className="log-modal"
                onClick={(e: React.MouseEvent) => e.stopPropagation()}
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
            >
                <h2>Daily Bio-Log</h2>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Date</label>
                        <input
                            type="date"
                            value={formData.date}
                            onChange={e => setFormData({ ...formData, date: e.target.value })}
                        />
                    </div>
                    <div className="form-group">
                        <label>Sleep Hours ({formData.sleep_hours}h)</label>
                        <input
                            type="range" min="0" max="12" step="0.5"
                            value={formData.sleep_hours}
                            onChange={e => setFormData({ ...formData, sleep_hours: parseFloat(e.target.value) })}
                        />
                    </div>
                    <div className="form-group">
                        <label>Mood ({formData.mood_score}/10)</label>
                        <input
                            type="range" min="1" max="10"
                            value={formData.mood_score}
                            onChange={e => setFormData({ ...formData, mood_score: parseInt(e.target.value) })}
                        />
                    </div>
                    <div className="form-group">
                        <label>Energy ({formData.energy_level}/10)</label>
                        <input
                            type="range" min="1" max="10"
                            value={formData.energy_level}
                            onChange={e => setFormData({ ...formData, energy_level: parseInt(e.target.value) })}
                        />
                    </div>
                    <div className="form-actions">
                        <button type="button" onClick={onClose}>Cancel</button>
                        <button type="submit" className="save-btn">Save Log</button>
                    </div>
                </form>
            </motion.div>
        </div>
    );
};

export default Panopticon;
