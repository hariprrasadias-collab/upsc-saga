import React, { useState, useEffect } from 'react';
import './BossArena.css';
import { audioManager } from '../../util/AudioManager';

interface Boss {
    id: string | number;
    type: 'YEAR' | 'SUBJECT' | 'CUSTOM';
    name: string;
    hp: number;
    max_hp: number;
    xp_reward: number;
    loot: string[];
}

interface Question {
    id: number;
    text: string;
    options: string[];
    correct_option: string;
    explanation: string;
}

interface BattleInterfaceProps {
    boss: Boss;
    onBattleEnd: () => void;
}

const BattleInterface: React.FC<BattleInterfaceProps> = ({ boss, onBattleEnd }) => {
    const [questions, setQuestions] = useState<Question[]>([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [bossHp, setBossHp] = useState(boss.hp);
    const [maxBossHp, setMaxBossHp] = useState(boss.max_hp);
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
            const res = await fetch('/api/arena/fight/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    boss_type: boss.type,
                    boss_id: boss.id
                })
            });
            const data = await res.json();
            setQuestions(data.questions);
            setBossHp(data.boss.hp);
            setMaxBossHp(data.boss.max_hp);
            setPlayerHp(data.player_hp);
            setLoading(false);
            audioManager.play('click');
        } catch (err) {
            console.error("Failed to start battle:", err);
        }
    };

    const updateChallengeProgress = async (type: string, increment: number = 1) => {
        try {
            const res = await fetch('/api/challenges/daily');
            if (res.ok) {
                const challenge = await res.json();
                if (challenge && challenge.type === type && !challenge.completed) {
                    const newProgress = Math.min(challenge.progress + increment, challenge.target_value);
                    await fetch('/api/challenges/progress', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ progress: newProgress })
                    });
                }
            }
        } catch (err) {
            console.error("Failed to update challenge progress:", err);
        }
    };

    const handleAnswer = (index: number) => {
        const currentQ = questions[currentQuestionIndex];
        const selectedOption = ['A', 'B', 'C', 'D'][index];
        const isCorrect = selectedOption === currentQ.correct_option;

        if (isCorrect) {
            const newBossHp = bossHp - 1;
            setBossHp(newBossHp);
            setDamageDealt(prev => prev + 1);
            setShake('boss');
            audioManager.play('success');
            updateChallengeProgress('mcq', 1);

            if (newBossHp <= 0) {
                endBattle('VICTORY');
            } else {
                nextQuestion();
            }
        } else {
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
            if (bossHp > 0) {
                endBattle('DEFEAT');
            }
        }
    };

    const endBattle = async (outcome: 'VICTORY' | 'DEFEAT') => {
        setBattleState(outcome.toLowerCase() as any);

        try {
            const res = await fetch('/api/arena/fight/end', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    boss_type: boss.type,
                    boss_id: boss.id,
                    damage_dealt: damageDealt + (outcome === 'VICTORY' ? 1 : 0),
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

    if (loading) {
        return <div className="loading">Loading battle arena...</div>;
    }

    if (!questions || questions.length === 0) {
        return (
            <div className="battle-result">
                <h2>No Questions Available</h2>
                <p>The Oracle could not find any challenges for this battle.</p>
                <button className="return-btn" onClick={onBattleEnd}>Return to Arena</button>
            </div>
        );
    }

    if (battleState !== 'active') {
        return (
            <div className={`battle-result ${battleState}`}>
                <h1>{battleState === 'victory' ? '⚔️ VICTORY ⚔️' : '💀 DEFEATED 💀'}</h1>
                <div className="battle-stats">
                    <p>Damage Dealt: {damageDealt}</p>
                    <p>Damage Taken: {damageTaken}</p>
                    {battleState === 'victory' && loot.length > 0 && (
                        <div className="loot-display">
                            <h3>Loot:</h3>
                            <ul>
                                {loot.map((item, idx) => <li key={idx}>{item}</li>)}
                            </ul>
                        </div>
                    )}
                </div>
                <button className="return-btn" onClick={onBattleEnd}>Return to Arena</button>
            </div>
        );
    }

    const currentQ = questions[currentQuestionIndex];
    const bossHpPercent = (bossHp / maxBossHp) * 100;
    const playerHpPercent = (playerHp / 3) * 100;

    return (
        <div className="battle-interface">
            {/* End Battle Button in top-right */}
            <button className="end-battle-btn" onClick={onBattleEnd} title="End battle and return">
                ✕ End Battle
            </button>

            {/* HUD */}
            <div className="battle-hud">
                <div className={`player-health ${shake === 'player' ? 'shake' : ''}`}>
                    <div className="health-label">YOU</div>
                    <div className="health-bar-container">
                        <div
                            className="health-bar-fill player"
                            style={{ width: `${playerHpPercent}%` }}
                        ></div>
                    </div>
                    <div className="hp-text">{playerHp} / 3</div>
                </div>

                <div className="vs-badge">VS</div>

                <div className={`boss-health ${shake === 'boss' ? 'shake' : ''}`}>
                    <div className="health-label">{boss.name}</div>
                    <div className="health-bar-container">
                        <div
                            className="health-bar-fill boss"
                            style={{ width: `${bossHpPercent}%` }}
                        ></div>
                    </div>
                    <div className="hp-text">{bossHp} / {maxBossHp}</div>
                </div>
            </div>

            {/* Battle Area */}
            <div className="battle-area">
                <div className={`boss-sprite ${shake === 'boss' ? 'damage-flash' : ''}`}>
                    <div className="boss-avatar-large">{boss.name[0]}</div>
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
