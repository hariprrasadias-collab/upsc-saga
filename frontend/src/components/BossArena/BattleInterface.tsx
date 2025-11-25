import React, { useState, useEffect } from 'react';
import './BossArena.css';
import { audioManager } from '../../util/AudioManager';

interface Boss {
    id: number;
    boss_name: string;
    total_hp: number;
    image_url: string;
}

interface Question {
    id: number;
    text: string;
    options: string[];
    correct_index: number;
}

interface BattleInterfaceProps {
    boss: Boss;
    onBattleEnd: () => void;
}

const BattleInterface: React.FC<BattleInterfaceProps> = ({ boss, onBattleEnd }) => {
    const [questions, setQuestions] = useState<Question[]>([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [bossHp, setBossHp] = useState(boss.total_hp);
    const [maxBossHp, setMaxBossHp] = useState(boss.total_hp);
    const [playerHp, setPlayerHp] = useState(3);
    const [loading, setLoading] = useState(true);
    const [battleState, setBattleState] = useState<'active' | 'victory' | 'defeat'>('active');
    const [damageDealt, setDamageDealt] = useState(0);
    const [damageTaken, setDamageTaken] = useState(0);
    const [shake, setShake] = useState<'boss' | 'player' | null>(null);
    const [loot, setLoot] = useState<string[]>([]);

    useEffect(() => {
        startBattle();
    }, []);

    const startBattle = async () => {
        try {
            const res = await fetch('http://localhost:5000/api/arena/fight/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ boss_id: boss.id })
            });
            const data = await res.json();
            setQuestions(data.questions);
            setBossHp(data.boss.hp);
            setMaxBossHp(data.boss.hp);
            setPlayerHp(data.player_hp);
            setLoading(false);
            audioManager.play('click'); // Placeholder for battle music start
        } catch (err) {
            console.error("Failed to start battle:", err);
        }
    };

    const handleAnswer = (index: number) => {
        const currentQ = questions[currentQuestionIndex];
        const isCorrect = index === currentQ.correct_index;

        if (isCorrect) {
            // Damage Boss
            const newBossHp = bossHp - 1;
            setBossHp(newBossHp);
            setDamageDealt(prev => prev + 1);
            setShake('boss');
            audioManager.play('success');

            if (newBossHp <= 0) {
                endBattle('VICTORY');
            } else {
                nextQuestion();
            }
        } else {
            // Damage Player
            const newPlayerHp = playerHp - 1;
            setPlayerHp(newPlayerHp);
            setDamageTaken(prev => prev + 1);
            setShake('player');
            audioManager.play('error');

            if (newPlayerHp <= 0) {
                endBattle('DEFEAT');
            } else {
                nextQuestion();
            }
        }

        setTimeout(() => setShake(null), 500);
    };

    const nextQuestion = () => {
        if (currentQuestionIndex < questions.length - 1) {
            setTimeout(() => setCurrentQuestionIndex(prev => prev + 1), 1000);
        } else {
            // Out of questions but boss still alive? Treat as defeat or draw?
            // For now, if boss still has HP, it's a defeat (ran out of ammo)
            if (bossHp > 0) {
                endBattle('DEFEAT');
            }
        }
    };

    const endBattle = async (outcome: 'VICTORY' | 'DEFEAT') => {
        setBattleState(outcome.toLowerCase() as any);

        try {
            const res = await fetch('http://localhost:5000/api/arena/fight/end', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    boss_id: boss.id,
                    damage_dealt: damageDealt + (outcome === 'VICTORY' ? 1 : 0), // Include killing blow
                    damage_taken: damageTaken + (outcome === 'DEFEAT' ? 1 : 0),
                    outcome
                })
            });
            const data = await res.json();
            if (data.loot) {
                setLoot(data.loot);
            }
            if (outcome === 'VICTORY') audioManager.play('levelUp');
        } catch (err) {
            console.error("Failed to record battle:", err);
        }
    };

    if (loading) return <div className="loading-battle">Entering Arena...</div>;

    if (battleState !== 'active') {
        return (
            <div className={`battle-result ${battleState}`}>
                <h1>{battleState === 'victory' ? 'VICTORY!' : 'DEFEATED'}</h1>
                <div className="battle-stats">
                    <p>Damage Dealt: {damageDealt}</p>
                    <p>Damage Taken: {damageTaken}</p>
                </div>
                {loot.length > 0 && (
                    <div className="loot-section">
                        <h3>Loot Earned:</h3>
                        <ul>
                            {loot.map((item, i) => <li key={i}>{item}</li>)}
                        </ul>
                    </div>
                )}
                <button className="return-btn" onClick={onBattleEnd}>Return to Arena</button>
            </div>
        );
    }

    const currentQ = questions[currentQuestionIndex];

    return (
        <div className="battle-interface">
            {/* HUD */}
            <div className="battle-hud">
                <div className={`player-health ${shake === 'player' ? 'shake' : ''}`}>
                    <div className="health-label">YOU</div>
                    <div className="health-bar-container">
                        <div
                            className="health-bar-fill player"
                            style={{ width: `${(playerHp / 3) * 100}%` }}
                        ></div>
                    </div>
                    <div className="hp-text">{playerHp} / 3</div>
                </div>

                <div className="vs-badge">VS</div>

                <div className={`boss-health ${shake === 'boss' ? 'shake' : ''}`}>
                    <div className="health-label">{boss.boss_name}</div>
                    <div className="health-bar-container">
                        <div
                            className="health-bar-fill boss"
                            style={{ width: `${(bossHp / maxBossHp) * 100}%` }}
                        ></div>
                    </div>
                    <div className="hp-text">{bossHp} / {maxBossHp}</div>
                </div>
            </div>

            {/* Battle Area */}
            <div className="battle-area">
                <div className={`boss-sprite ${shake === 'boss' ? 'damage-flash' : ''}`}>
                    {/* Placeholder or Image */}
                    <div className="boss-avatar-large">{boss.boss_name[0]}</div>
                </div>
            </div>

            {/* Question Controls */}
            <div className="battle-controls">
                <div className="question-display">
                    <h3>{currentQ.text}</h3>
                </div>
                <div className="options-grid">
                    {currentQ.options.map((opt, i) => (
                        <button key={i} className="option-btn" onClick={() => handleAnswer(i)}>
                            {opt}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default BattleInterface;
