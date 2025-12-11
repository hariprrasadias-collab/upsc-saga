import React, { useEffect, useState } from 'react';
import { FaChessKing, FaHeartbeat, FaExclamationTriangle, FaRocket } from 'react-icons/fa';
import type { Action } from './types';

interface StrategosViewProps {
    onExecuteAction: (action: Action) => Promise<any>;
}

interface BrainStatus {
    current_strategy: any[];
    bio_status: {
        status: string;
        energy: number;
        alert: string | null;
    } | null;
}

const StrategosView: React.FC<StrategosViewProps> = ({ onExecuteAction: _onExecuteAction }) => {
    const [status, setStatus] = useState<BrainStatus | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStatus();
    }, []);

    const fetchStatus = async () => {
        try {
            const res = await fetch('/api/brain/status');
            const data = await res.json();
            setStatus(data);
        } catch (err) {
            console.error("Failed to fetch Strategos status:", err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="strategos-loading">Accessing War Room...</div>;

    const strategy = status?.current_strategy;
    const bio = status?.bio_status;

    return (
        <div className="strategos-view">
            <div className="strategos-header">
                <h3><FaChessKing /> STRATEGOS: Grand Strategy</h3>
            </div>

            <div className="strategos-grid">
                {/* BIO-STATUS PANEL */}
                <div className="strategos-card bio-card">
                    <h4><FaHeartbeat /> Bio-Status</h4>
                    {bio ? (
                        <div className="bio-metrics">
                            <div className="metric-row">
                                <span>Condition:</span>
                                <span className={`status-badge ${bio.status.toLowerCase()}`}>{bio.status}</span>
                            </div>
                            <div className="metric-row">
                                <span>Energy:</span>
                                <div className="energy-bar-container">
                                    <div
                                        className="energy-bar"
                                        style={{ width: `${bio.energy}%`, backgroundColor: bio.energy > 50 ? '#00ff00' : '#ff4400' }}
                                    />
                                </div>
                                <span>{bio.energy}%</span>
                            </div>
                            {bio.alert && (
                                <div className="bio-alert">
                                    <FaExclamationTriangle /> {bio.alert}
                                </div>
                            )}
                        </div>
                    ) : (
                        <p>Panopticon Offline</p>
                    )}
                </div>

                {/* MISSION CONTROL PANEL */}
                <div className="strategos-card mission-card">
                    <h4><FaRocket /> Mission Probability</h4>
                    <div className="mission-gauge">
                        <div className="gauge-body">
                            <div
                                className="gauge-fill"
                                style={{
                                    transform: `rotate(${((status?.bio_status?.energy || 50) / 100) * 180}deg)`
                                }}
                            />
                            <div className="gauge-cover">
                                <span className="probability-value">{status?.bio_status?.energy || 0}%</span>
                                <span className="probability-label">Success Chance</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* STRATEGY PANEL */}
                <div className="strategos-card strategy-card">
                    <h4>Current Directive (Golden Path)</h4>
                    {strategy && strategy.length > 0 ? (
                        <div className="strategy-list">
                            {strategy.slice(0, 5).map((_step, idx) => (
                                <div key={idx} className="strategy-step">
                                </div>
                            ))}
                            {strategy.length > 5 && <div className="more-steps">...and {strategy.length - 5} more steps</div>}
                        </div>
                    ) : (
                        <div className="no-strategy">
                            <p>No Active Directive.</p>
                            <button onClick={() => window.location.href = '/golden-path'}>
                                Initialize Golden Path
                            </button>
                        </div>
                    )}
                </div>
            </div>

            <style>{`
                .strategos-view {
                    padding: 15px;
                    color: #eee;
                }
                .strategos-header h3 {
                    color: #ffd700;
                    border-bottom: 1px solid #ffd700;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }
                .strategos-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                }
                .strategos-card {
                    background: rgba(0, 0, 0, 0.3);
                    border: 1px solid #333;
                    padding: 15px;
                    border-radius: 8px;
                }
                .bio-card h4 { color: #ff4444; margin-top: 0; }
                .strategy-card h4 { color: #00ff00; margin-top: 0; }
                
                .metric-row {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                }
                .energy-bar-container {
                    flex-grow: 1;
                    height: 8px;
                    background: #333;
                    margin: 0 10px;
                    border-radius: 4px;
                }
                .energy-bar { height: 100%; border-radius: 4px; transition: width 0.5s; }
                
                .strategy-step {
                    display: flex;
                    align-items: center;
                    padding: 8px;
                    border-bottom: 1px solid #222;
                }
                .step-marker {
                    width: 24px;
                    height: 24px;
                    background: #333;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-right: 10px;
                    font-size: 0.8rem;
                }
                .step-content { flex-grow: 1; display: flex; flex-direction: column; }
                .step-label { font-weight: bold; }
                .step-meta { font-size: 0.75rem; color: #888; }
                .current-icon { color: #00ff00; }
                
                .no-strategy button {
                    background: #ffd700;
                    color: #000;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    margin-top: 10px;
                }
                .mission-card h4 { color: #00bfff; margin-top: 0; }
                .mission-gauge {
                    position: relative;
                    width: 150px;
                    height: 75px;
                    margin: 0 auto;
                    overflow: hidden;
                }
                .gauge-body {
                    width: 100%;
                    height: 100%;
                    background: #333;
                    border-top-left-radius: 100px;
                    border-top-right-radius: 100px;
                    position: relative;
                }
                .gauge-fill {
                    position: absolute;
                    top: 100%;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: #00ff00;
                    transform-origin: center top;
                    transition: transform 1s ease-out;
                }
                .gauge-cover {
                    position: absolute;
                    bottom: 0;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 80%;
                    height: 80%;
                    background: #1a1a1a;
                    border-top-left-radius: 100px;
                    border-top-right-radius: 100px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: flex-end;
                    padding-bottom: 5px;
                }
                .probability-value { font-size: 1.5rem; font-weight: bold; color: #fff; }
                .probability-label { font-size: 0.6rem; color: #888; text-transform: uppercase; }
            `}</style>
        </div>
    );
};

export default StrategosView;
