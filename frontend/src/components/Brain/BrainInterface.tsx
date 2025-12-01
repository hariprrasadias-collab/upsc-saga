import React, { useState, useEffect } from 'react';
import './BrainInterface.css';
import { FaBrain, FaTimes, FaRobot, FaLightbulb, FaExclamationTriangle, FaCompressAlt } from 'react-icons/fa';
import AutonomySettings from './AutonomySettings';
import ExplainabilityDashboard from './ExplainabilityDashboard';
import ChatView from './ChatView';
import StatusView from './StatusView';
import InsightsView from './InsightsView';
import { useBrain } from './useBrain';

type TabType = 'chat' | 'status' | 'insights' | 'autonomy' | 'optimization';

const BrainInterface: React.FC = () => {
    // --- UI State ---
    const [isOpen, setIsOpen] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
    const [activeTab, setActiveTab] = useState<TabType>('chat');
    const [inputValue, setInputValue] = useState('');

    // --- Brain Logic ---
    const {
        messages,
        isThinking,
        synapses,
        insights,
        isLoadingInsights,
        error,
        fetchSynapses,
        fetchProactiveInsights,
        executeAction,
        optimizeSystem,
        sendMessage
    } = useBrain();

    // --- Effects ---
    useEffect(() => {
        if (isOpen && !isMinimized) {
            if (activeTab === 'status') fetchSynapses();
            if (activeTab === 'insights') fetchProactiveInsights();
        }
    }, [isOpen, isMinimized, activeTab, fetchSynapses, fetchProactiveInsights]);

    // --- Handlers ---
    const handleSendMessage = () => {
        if (!inputValue.trim()) return;
        sendMessage(inputValue);
        setInputValue('');
    };

    const handleOptimize = async () => {
        const success = await optimizeSystem();
        if (success) setActiveTab('chat');
    };

    const toggleOpen = () => {
        setIsOpen(!isOpen);
        setIsMinimized(false); // Reset minimize state when opening/closing
    };

    // --- Render Helpers ---
    const renderTabs = () => (
        <div className="brain-tabs">
            {[
                { id: 'chat', label: 'Chat', icon: null },
                { id: 'status', label: 'Synapses', icon: null },
                { id: 'insights', label: 'Insights', icon: null },
                { id: 'autonomy', label: 'Autonomy', icon: <FaRobot /> },
                { id: 'optimization', label: 'Optimize', icon: <FaLightbulb /> },
            ].map(tab => (
                <button
                    key={tab.id}
                    className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                    onClick={() => setActiveTab(tab.id as TabType)}
                    aria-label={`Switch to ${tab.label} tab`}
                >
                    {tab.icon} {tab.label}
                </button>
            ))}
        </div>
    );

    return (
        <div className={`brain-interface-container ${isMinimized ? 'minimized' : ''}`}>
            {/* Toggle Button (Visible when closed or minimized) */}
            {(!isOpen || isMinimized) && (
                <div
                    className={`brain-toggle-btn ${isOpen ? 'open' : ''}`}
                    onClick={toggleOpen}
                    aria-label="Toggle Brain Interface"
                    role="button"
                    tabIndex={0}
                >
                    <FaBrain className="brain-icon" />
                    <div className="brain-pulse"></div>
                </div>
            )}

            {/* Main Window */}
            {isOpen && !isMinimized && (
                <div className="brain-window" role="dialog" aria-label="Central Nervous System Interface">
                    <div className="brain-header">
                        <div className="brain-title">
                            <FaBrain />
                            <span>Central Nervous System</span>
                        </div>
                        <div className="brain-controls">
                            <button
                                className="brain-control-btn"
                                onClick={() => setIsMinimized(true)}
                                aria-label="Minimize"
                            >
                                <FaCompressAlt />
                            </button>
                            <button
                                className="brain-control-btn close"
                                onClick={() => setIsOpen(false)}
                                aria-label="Close"
                            >
                                <FaTimes />
                            </button>
                        </div>
                    </div>

                    {renderTabs()}

                    <div className="brain-content">
                        {error && (
                            <div className="error-toast" role="alert">
                                <FaExclamationTriangle /> {error}
                            </div>
                        )}

                        {activeTab === 'chat' && (
                            <ChatView
                                messages={messages}
                                isThinking={isThinking}
                                inputValue={inputValue}
                                setInputValue={setInputValue}
                                onSendMessage={handleSendMessage}
                                onExecuteAction={executeAction}
                            />
                        )}

                        {activeTab === 'status' && (
                            <StatusView
                                synapses={synapses}
                                onOptimize={handleOptimize}
                                isThinking={isThinking}
                            />
                        )}

                        {activeTab === 'insights' && (
                            <InsightsView
                                insights={insights}
                                isLoading={isLoadingInsights}
                                onExecuteAction={executeAction}
                            />
                        )}

                        {activeTab === 'autonomy' && <AutonomySettings />}

                        {activeTab === 'optimization' && <ExplainabilityDashboard />}
                    </div>
                </div>
            )}
        </div>
    );
};

export default BrainInterface;
