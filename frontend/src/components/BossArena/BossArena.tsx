import { API_BASE_URL } from '../../config';

import React, { useState, useEffect, useCallback } from 'react';
import './BossArena.css';
import BattleInterface from './BattleInterface';
import { brainService } from '../../services/BrainService';

interface Battle {
    id: string;
    boss_name: string;
    subject: string;
    total_marks: number;
    cutoff_marks: number;
    my_score: number;
    is_victory: boolean;
    date_fought: string;
    type: 'Mock Test' | 'Answer Writing' | 'Boss Fight';
}

interface Boss {
    id: string | number;
    type: 'YEAR' | 'SUBJECT' | 'CUSTOM';
    name: string;
    hp: number;
    max_hp: number;
    xp_reward: number;
    loot: string[];
}

interface BossArenaProps {
    onBattleComplete: () => void;
}

const BossArena: React.FC<BossArenaProps> = ({ onBattleComplete }) => {
    const [battles, setBattles] = useState<Battle[]>([]);
    const [yearBosses, setYearBosses] = useState<Boss[]>([]);
    const [subjectBosses, setSubjectBosses] = useState<Boss[]>([]);
    const [customBosses, setCustomBosses] = useState<Boss[]>([]);
    const [showModal, setShowModal] = useState(false);
    const [loading, setLoading] = useState(true);
    const [activeBattleBoss, setActiveBattleBoss] = useState<Boss | null>(null);
    const [isSummoning, setIsSummoning] = useState(false);

    const [bossName, setBossName] = useState('');
    const [subject, setSubject] = useState('General Studies I');
    const [totalMarks, setTotalMarks] = useState(200);
    const [cutoffMarks, setCutoffMarks] = useState(90);
    const [myScore, setMyScore] = useState(0);

    const fetchBattles = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/battles`);
            if (res.ok) {
                const raw = await res.json();
                const data = raw.success === false ? [] : (raw.data || raw);
                setBattles(Array.isArray(data) ? data : []);
            }
        } catch (err) {
            console.error("Failed to load battle history", err);
        }
    }, []);

    const fetchBosses = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/arena/bosses`);
            if (res.ok) {
                const raw = await res.json();
                const data = raw.data || raw;
                setYearBosses(Array.isArray(data.year_bosses) ? data.year_bosses : []);
                setSubjectBosses(Array.isArray(data.subject_bosses) ? data.subject_bosses : []);
                setCustomBosses(Array.isArray(data.custom_bosses) ? data.custom_bosses : []);
            }
        } catch (err) {
            console.error("Failed to load bosses", err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchBattles();
        fetchBosses();
    }, [fetchBattles, fetchBosses]);

    const handleFight = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const res = await fetch(`${API_BASE_URL}/api/battles/manual`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    boss_name: bossName,
                    subject: subject,
                    total_marks: totalMarks,
                    cutoff_marks: cutoffMarks,
                    my_score: myScore
                })
            });

            if (res.ok) {
                const result = await res.json();
                alert(result.is_victory ? "VICTORY! BOSS SLAIN!" : "DEFEAT. TRAIN HARDER.");
                await fetchBattles();
                onBattleComplete();
                setShowModal(false);
                setBossName('');
                setMyScore(0);
            }
        } catch (err) {
            console.error("Battle error", err);
        }
    };

    const handleSummonNemesis = async () => {
        setIsSummoning(true);
        try {
            // Ask Brain to summon a boss based on weak areas
            const result = await brainService.executeAction('SUMMON_BOSS', {});
            if (result.success) {
                alert(result.message);
                fetchBosses();
            } else {
                alert("Summoning failed: " + result.message);
            }
        } catch (err) {
            console.error("Summoning error:", err);
            alert("The Arena is silent.");
        } finally {
            setIsSummoning(false);
        }
    };

    const startBossBattle = (boss: Boss) => {
        setActiveBattleBoss(boss);
    };

    const handleBattleEnd = () => {
        setActiveBattleBoss(null);
        fetchBattles();
        onBattleComplete();
    };

    if (activeBattleBoss) {
        return <BattleInterface boss={activeBattleBoss} onBattleEnd={handleBattleEnd} />;
    }

    return (
        <div className="arena-container">
            <div className="arena-header">
                <h1 className="arena-title">The Proving Grounds</h1>
                <p className="arena-subtitle">Face mighty bosses and prove your knowledge</p>
                <button
                    className="summon-btn"
                    onClick={handleSummonNemesis}
                    disabled={isSummoning}
                    style={{ marginTop: '15px', background: 'linear-gradient(45deg, #8e44ad, #c0392b)', border: 'none', padding: '10px 20px', color: 'white', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
                >
                    {isSummoning ? 'Summoning...' : '👹 Summon Nemesis (Brain)'}
                </button>
            </div>

            {/* Year Titans Section */}
            <h2 style={{ fontSize: '28px', margin: '30px 0 20px', color: '#ff4081' }}>⚔️ Year Titans</h2>
            <div className="boss-grid">
                {yearBosses.map(boss => {
                    const difficultyLevel = boss.hp <= boss.max_hp * 0.3 ? 'hard' : boss.hp <= boss.max_hp * 0.7 ? 'medium' : 'easy';
                    return (
                        <div key={'year-' + boss.id} className={`boss-card ${difficultyLevel}`}>
                            <div className="boss-image-container">
                                <div className="boss-avatar-placeholder">{boss.name.substring(4, 8)}</div>
                            </div>
                            <div className="boss-info">
                                <h3 className="boss-name">{boss.name}</h3>
                                <div className="boss-meta">
                                    <span className="boss-subject">📅 History</span>
                                    <span className={`boss-difficulty ${difficultyLevel}`}>
                                        {difficultyLevel.charAt(0).toUpperCase() + difficultyLevel.slice(1)}
                                    </span>
                                </div>
                                <p className="boss-desc">
                                    Challenge the {boss.name.split(' ')[1]} year examination. Test your knowledge across all subjects.
                                </p>
                                <div className="boss-stats">
                                    <div className="stat">
                                        <span className="label">Health</span>
                                        <span className="value">{boss.hp}/{boss.max_hp}</span>
                                    </div>
                                    <div className="stat">
                                        <span className="label">Reward</span>
                                        <span className="value">{boss.xp_reward} XP</span>
                                    </div>
                                </div>
                                <button className="challenge-btn" onClick={() => startBossBattle(boss)}>
                                    ⚔️ Challenge
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Subject Golems Section */}
            <h2 style={{ fontSize: '28px', margin: '40px 0 20px', color: '#ff4081' }}>🛡️ Subject Golems</h2>
            <div className="boss-grid">
                {subjectBosses.map(boss => {
                    const difficultyLevel = boss.hp <= boss.max_hp * 0.3 ? 'hard' : boss.hp <= boss.max_hp * 0.7 ? 'medium' : 'easy';
                    return (
                        <div key={'sub-' + boss.id} className={`boss-card ${difficultyLevel}`}>
                            <div className="boss-image-container">
                                <div className="boss-avatar-placeholder">{boss.name[0]}</div>
                            </div>
                            <div className="boss-info">
                                <h3 className="boss-name">{boss.name}</h3>
                                <div className="boss-meta">
                                    <span className="boss-subject">📚 {boss.name}</span>
                                    <span className={`boss-difficulty ${difficultyLevel}`}>
                                        {difficultyLevel.charAt(0).toUpperCase() + difficultyLevel.slice(1)}
                                    </span>
                                </div>
                                <p className="boss-desc">
                                    Master the {boss.name} domain. Face questions from this crucial subject area.
                                </p>
                                <div className="boss-stats">
                                    <div className="stat">
                                        <span className="label">Health</span>
                                        <span className="value">{boss.hp}/{boss.max_hp}</span>
                                    </div>
                                    <div className="stat">
                                        <span className="label">Reward</span>
                                        <span className="value">{boss.xp_reward} XP</span>
                                    </div>
                                </div>
                                <button className="challenge-btn" onClick={() => startBossBattle(boss)}>
                                    ⚔️ Challenge
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Custom Bosses Section */}
            {customBosses.length > 0 && (
                <>
                    <h2 style={{ fontSize: '28px', margin: '40px 0 20px', color: '#9b59b6' }}>👹 Custom Challenges</h2>
                    <div className="boss-grid">
                        {customBosses.map(boss => {
                            const difficultyLevel = 'medium';
                            return (
                                <div key={'custom-' + boss.id} className={`boss-card ${difficultyLevel}`}>
                                    <div className="boss-image-container">
                                        <div className="boss-avatar-placeholder" style={{ background: '#8e44ad' }}>C</div>
                                    </div>
                                    <div className="boss-info">
                                        <h3 className="boss-name">{boss.name}</h3>
                                        <div className="boss-meta">
                                            <span className="boss-subject">🎯 Custom</span>
                                            <span className="boss-difficulty medium">Medium</span>
                                        </div>
                                        <p className="boss-desc">
                                            A custom challenge created from the Archives. Prove your mastery over these specific topics.
                                        </p>
                                        <div className="boss-stats">
                                            <div className="stat">
                                                <span className="label">Health</span>
                                                <span className="value">{boss.hp}/{boss.max_hp}</span>
                                            </div>
                                            <div className="stat">
                                                <span className="label">Reward</span>
                                                <span className="value">{boss.xp_reward} XP</span>
                                            </div>
                                        </div>
                                        <button className="challenge-btn" onClick={() => startBossBattle(boss)}>
                                            ⚔️ Challenge
                                        </button>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </>
            )}

            {/* Battle History */}
            <div className="battle-list" style={{ marginTop: '50px' }}>
                <h2>Battle History</h2>
                {loading ? (
                    <div style={{ textAlign: 'center' }}>Summoning opponents...</div>
                ) : battles.length === 0 ? (
                    <div style={{ textAlign: 'center', opacity: 0.7 }}>No battles recorded. The arena awaits.</div>
                ) : (
                    battles.map(battle => (
                        <div key={battle.id} className={`battle-card ${battle.is_victory ? 'victory' : 'defeat'}`}>
                            <div className="boss-info">
                                <h3>{battle.boss_name}</h3>
                                <div className="boss-subject">
                                    <span className="battle-type">{battle.type}</span> • {battle.subject}
                                </div>
                            </div>
                            <div className="score-display">
                                <div className="score-big" style={{ color: battle.is_victory ? '#d4a574' : '#e74c3c' }}>
                                    {battle.my_score} / {battle.total_marks}
                                </div>
                                <div className="score-cutoff">Cutoff: {battle.cutoff_marks}</div>
                            </div>
                        </div>
                    ))
                )}
            </div>

            <button className="challenge-btn" onClick={() => setShowModal(true)} style={{ marginTop: '30px' }}>
                LOG MANUAL BATTLE
            </button>

            {/* Battle Modal */}
            {showModal && (
                <div className="arena-modal-overlay">
                    <div className="arena-modal">
                        <h2>LOG PAST BATTLE</h2>
                        <form className="arena-form" onSubmit={handleFight}>
                            <input
                                type="text"
                                placeholder="Boss Name (e.g. Vision Test 1)"
                                value={bossName}
                                onChange={e => setBossName(e.target.value)}
                                required
                            />
                            <select value={subject} onChange={e => setSubject(e.target.value)}>
                                <option>General Studies I</option>
                                <option>General Studies II</option>
                                <option>General Studies III</option>
                                <option>General Studies IV</option>
                                <option>Essay</option>
                                <option>Optional Paper 1</option>
                                <option>Optional Paper 2</option>
                            </select>

                            <div style={{ display: 'flex', gap: '10px' }}>
                                <input
                                    type="number"
                                    placeholder="Total Marks"
                                    value={totalMarks}
                                    onChange={e => setTotalMarks(Number(e.target.value))}
                                />
                                <input
                                    type="number"
                                    placeholder="Cutoff"
                                    value={cutoffMarks}
                                    onChange={e => setCutoffMarks(Number(e.target.value))}
                                />
                            </div>

                            <input
                                type="number"
                                step="0.01"
                                placeholder="YOUR SCORE (Damage Dealt)"
                                value={myScore}
                                onChange={e => setMyScore(Number(e.target.value))}
                                style={{ borderColor: '#e74c3c', fontSize: '1.5rem', fontWeight: 'bold' }}
                                required
                            />

                            <button type="submit" className="fight-btn">RECORD</button>
                            <button type="button" className="cancel-fight" onClick={() => setShowModal(false)}>Cancel</button>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default BossArena;