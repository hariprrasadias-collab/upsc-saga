// /frontend/src/components/BossArena/BossArena.tsx
import React, { useState, useEffect, useCallback } from 'react';
import './BossArena.css';

interface Battle {
    id: number;
    boss_name: string;
    subject: string;
    total_marks: number;
    cutoff_marks: number;
    my_score: number;
    is_victory: boolean;
    date_fought: string;
}

// Props to notify App to refresh XP stats
interface BossArenaProps {
    onBattleComplete: () => void;
}

const BossArena: React.FC<BossArenaProps> = ({ onBattleComplete }) => {
    const [battles, setBattles] = useState<Battle[]>([]);
    const [showModal, setShowModal] = useState(false);
    const [loading, setLoading] = useState(true);

    // Form State
    const [bossName, setBossName] = useState('');
    const [subject, setSubject] = useState('General Studies I');
    const [totalMarks, setTotalMarks] = useState(200);
    const [cutoffMarks, setCutoffMarks] = useState(90);
    const [myScore, setMyScore] = useState(0);

    const fetchBattles = useCallback(async () => {
        try {
            const res = await fetch('http://localhost:5000/api/battles');
            if (res.ok) {
                const data = await res.json();
                setBattles(data);
            }
        } catch (err) {
            console.error("Failed to load battle history", err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchBattles();
    }, [fetchBattles]);

    const handleFight = async (e: React.FormEvent) => {
        e.preventDefault();
        
        try {
            const res = await fetch('http://localhost:5000/api/battles', {
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
                await fetchBattles(); // Refresh list
                onBattleComplete(); // Refresh User XP in Sidebar
                setShowModal(false); // Close modal
                // Reset form
                setBossName('');
                setMyScore(0);
            }
        } catch (err) {
            console.error("Battle error", err);
        }
    };

    return (
        <div className="arena-container">
            <h1 className="arena-header">The Proving Grounds</h1>

            <div className="battle-list">
                {loading ? (
                    <div style={{textAlign:'center'}}>Summoning opponents...</div>
                ) : battles.length === 0 ? (
                    <div style={{textAlign:'center', opacity: 0.7}}>No battles recorded. The arena awaits.</div>
                ) : (
                    battles.map(battle => (
                        <div key={battle.id} className={`battle-card ${battle.is_victory ? 'victory' : 'defeat'}`}>
                            <div className="boss-info">
                                <h3>{battle.boss_name}</h3>
                                <div className="boss-subject">{battle.subject}</div>
                            </div>
                            <div className="score-display">
                                <div className="score-big" style={{color: battle.is_victory ? '#d4a574' : '#e74c3c'}}>
                                    {battle.my_score} / {battle.total_marks}
                                </div>
                                <div className="score-cutoff">Cutoff: {battle.cutoff_marks}</div>
                            </div>
                        </div>
                    ))
                )}
            </div>

            <button className="challenge-btn" onClick={() => setShowModal(true)}>
                CHALLENGE A BOSS
            </button>

            {/* BATTLE MODAL */}
            {showModal && (
                <div className="arena-modal-overlay">
                    <div className="arena-modal">
                        <h2>ENTER THE ARENA</h2>
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
                            
                            <div style={{display:'flex', gap:'10px'}}>
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
                                style={{borderColor: '#e74c3c', fontSize: '1.5rem', fontWeight:'bold'}}
                                required
                            />

                            <button type="submit" className="fight-btn">STRIKE!</button>
                            <button type="button" className="cancel-fight" onClick={() => setShowModal(false)}>Flee</button>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default BossArena;