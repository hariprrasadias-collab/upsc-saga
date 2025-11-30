import os

file_path = 'd:/upsc-second-brain/frontend/src/components/Planning/StudyPlanDashboard.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start of the nexus block
target = "} else if (viewMode === 'nexus') {"
parts = content.split(target)

if len(parts) > 1:
    # Keep everything before the nexus block
    pre_nexus = parts[0]
    
    # Define the correct ending
    new_ending = """} else if (viewMode === 'nexus') {
            return <NexusGraph />;
        }
    };

    const dashboardData = {
        study_analytics: {
            total_hours: studyAnalytics.totalHours,
            sessions_completed: studyAnalytics.sessionsCompleted,
            efficiency: studyAnalytics.efficiency
        }
    };

    return (
        <div className={`study-plan-dashboard ${isFlowMode ? 'flow-mode-active' : ''}`}>
            <div className="planner-header">
                {/* Row 1: Branding & Identity */}
                <div className="header-branding">
                    <h1> Mimir's Advanced Scheduler</h1>
                    <div className="gamification-hud">
                        <div className="xp-container" title={`XP: ${xp} / ${nextLevelXp}`}>
                            <div className="level-badge">Lvl {level}</div>
                            <div className="xp-bar-bg">
                                <div className="xp-bar-fill" style={{ width: `${(xp % 100) / 100 * 100}%` }}></div>
                            </div>
                        </div>
                        <button
                            className={`god-mode-toggle ${godMode ? 'active' : ''}`}
                            onClick={() => setGodMode(!godMode)}
                            title="Toggle God Mode (Debug Stats)"
                        >
                            ⚡
                        </button>
                    </div>
                </div>

                {/* Row 2: Toolbar (Navigation & Controls) */}
                <div className="header-toolbar">
                    <div className="toolbar-left">
                        {filterTopic && (
                            <button className="clear-filter-btn" onClick={() => setFilterTopic(null)}>
                                Filter: {filterTopic}
                            </button>
                        )}
                        <div className="view-tabs">
                            <button className={viewMode === 'daily' ? 'active' : ''} onClick={() => setViewMode('daily')}>Daily</button>
                            <button className={viewMode === 'weekly' ? 'active' : ''} onClick={() => setViewMode('weekly')}>Weekly</button>
                            <button className={viewMode === 'monthly' ? 'active' : ''} onClick={() => setViewMode('monthly')}>Monthly</button>
                            <button className={viewMode === 'yearly' ? 'active' : ''} onClick={() => setViewMode('yearly')}>Yearly</button>
                            <button className={viewMode === 'overall' ? 'active' : ''} onClick={() => setViewMode('overall')}>Overall</button>
                            <button className={viewMode === 'nexus' ? 'active' : ''} onClick={() => setViewMode('nexus')}> The Nexus</button>
                            <button className={viewMode === 'flashcards' ? 'active' : ''} onClick={() => setViewMode('flashcards')}> Flashcards</button>
                        </div>
                    </div>

                    <div className="toolbar-right">
                        <div className="controls">
                            <button
                                className={`toggle-btn ${isDynamicMode ? 'active' : ''}`}
                                onClick={() => setIsDynamicMode(!isDynamicMode)}
                                title="Dynamic Mode: Automatically reschedules pending tasks"
                            >
                                {isDynamicMode ? ' Auto-Pilot ON' : ' Static Mode'}
                            </button>
                            <button
                                className={`jarvis-btn ${isOptimizing ? 'pulsing' : ''}`}
                                onClick={runJarvisOptimization}
                                disabled={isOptimizing}
                                title="Run Genetic Algorithm to optimize schedule"
                            >
                                {isOptimizing ? ' Evolving...' : ' Jarvis Optimize'}
                            </button>
                            <button
                                className={`flow-btn ${isFlowMode ? 'active' : ''}`}
                                onClick={toggleFlowMode}
                                title="Bio-Adaptive Binaural Beats (40Hz Gamma)"
                            >
                                {isFlowMode ? ' Flow ON' : ' Flow OFF'}
                            </button>
                        </div>
                        {agentAction !== 'MAINTAIN_PACE' && (
                            <button
                                className="strategos-action-btn"
                                onClick={() => executeAgentAction(agentAction)}
                            >
                                {agentAction === 'SUGGEST_BREAK' ? ' Take Break' :
                                    agentAction === 'SCHEDULE_MOCK' ? ' Schedule Mock' :
                                        ' Acknowledge'}
                            </button>
                        )}
                    </div>
                </div>

                {/* God Mode Debug Panel */}
                {godMode && (
                    <div className="god-mode-panel">
                        <h3> GOD MODE: SYSTEM INTERNALS</h3>
                        <div className="debug-grid">
                            <div className="debug-item">
                                <label>Strategos Brain (DQN):</label>
                                <div className="dqn-stats">
                                    <div>Loss: {agent.getStats().loss}</div>
                                    <div>Epsilon: {agent.getStats().epsilon}</div>
                                    <div>Memory: {agent.getStats().memorySize}</div>
                                </div>
                            </div>
                            <div className="debug-item">
                                <label>Demon Confidence:</label>
                                <span>{demon.getConfidence()}%</span>
                            </div>
                            <div className="debug-item">
                                <label>Oracle Risk:</label>
                                <span>{oraclePrediction?.riskFactor}</span>
                            </div>
                        </div>
                    </div>
                )}

                {loading ? (
                    <div className="loading-state">
                        <div className="rune-spinner"></div>
                        <p>Consulting the Oracles...</p>
                    </div>
                ) : (
                    <>
                        <OracleDashboard data={dashboardData} />
                        {activePlan.length > 0 ? (
                            <div className="plan-timeline">
                                {/* Strategos Banner */}
                                <div className={`strategos-banner ${agentAction.toLowerCase().replace('_', '-')}`}>
                                    <div className="strategos-icon"></div>
                                    <div className="strategos-content">
                                        <span className="strategos-label">STRATEGOS AI COMMAND</span>
                                        <p>{agentSuggestion}</p>
                                    </div>
                                    {agentAction !== 'MAINTAIN_PACE' && (
                                        <button
                                            className="strategos-action-btn"
                                            onClick={() => executeAgentAction(agentAction)}
                                        >
                                            {agentAction === 'SUGGEST_BREAK' ? ' Take Break' :
                                                agentAction === 'SCHEDULE_MOCK' ? ' Schedule Mock' :
                                                    ' Acknowledge'}
                                        </button>
                                    )}
                                </div>
                                {renderContent()}
                            </div>
                        ) : (
                            <div className="empty-state">
                                <h2>No Plan Data Available</h2>
                                <p>Please click "Refresh Plan" or check your CSV file.</p>
                            </div>
                        )}
                    </>
                )}

                {selectedTask && (
                    <div className="modal-overlay" onClick={closeModal}>
                        <div className="task-modal" onClick={e => e.stopPropagation()}>
                            <div className="modal-header">
                                <h2>{selectedTask.subject}</h2>
                                <button onClick={closeModal}>X</button>
                            </div>
                            <div className="modal-body">
                                <div className="modal-row">
                                    <label>Topic:</label>
                                    <p>{selectedTask.activity}</p>
                                </div>
                                <div className="modal-row">
                                    <label>Time:</label>
                                    <p>{selectedTask.time}</p>
                                </div>
                                <div className="modal-row">
                                    <label>Status:</label>
                                    <span className={`status-badge ${selectedTask.status}`}>{selectedTask.status}</span>
                                </div>
                                {selectedTask.resource_link && (
                                    <div className="modal-row">
                                        <label>Resources:</label>
                                        <a href="#" onClick={(e) => e.preventDefault()}>{selectedTask.resource_link}</a>
                                    </div>
                                )}
                                <div className="modal-notes">
                                    <label>Notes:</label>
                                    <textarea placeholder="Add your notes here..."></textarea>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button
                                    className="debate-btn"
                                    onClick={() => {
                                        closeModal();
                                        console.log("Debate disabled");
                                    }}
                                >
                                    Debate This
                                </button>
                                <button
                                    className={`complete-btn ${selectedTask.status === 'completed' ? 'completed' : ''}`}
                                    onClick={() => toggleTaskStatus(selectedTask)}
                                >
                                    {selectedTask.status === 'completed' ? 'Mark Pending' : 'Mark Complete'}
                                </button>
                            </div>
                        </div>
                    </div>
                )}


                {ambushTopic && (
                    <div className="modal-overlay ambush-overlay">
                        <div className="ambush-modal">
                            <div className="ambush-header">
                                <h1> SUDDEN DEATH </h1>
                                <p>Nemesis has ambushed you!</p>
                            </div>
                            <div className="ambush-content">
                                <h3>Topic: {ambushTopic}</h3>
                                <p>Retention Critical! Prove your knowledge or suffer memory decay.</p>
                            </div>
                            <div className="ambush-actions">
                                <button
                                    className="fight-btn"
                                    onClick={() => {
                                        audioManager.play('click');
                                        audioManager.stopLoop('rage');
                                        alert(`Starting Flashcard Session for ${ambushTopic}`);
                                        setViewMode('flashcards');
                                        setAmbushTopic(null);
                                    }}
                                >
                                    FIGHT BACK (Start Quiz)
                                </button>
                                <button
                                    className="surrender-btn"
                                    onClick={() => {
                                        audioManager.stopLoop('rage');
                                        rescheduleTask(ambushTopic);
                                        alert(`${ambushTopic} has been rescheduled for tomorrow.`);
                                        setAmbushTopic(null);
                                    }}
                                >
                                    SURRENDER (Reschedule)
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        );
    };

    export default StudyPlanDashboard;
    """
    
    final_content = pre_nexus + new_ending
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
