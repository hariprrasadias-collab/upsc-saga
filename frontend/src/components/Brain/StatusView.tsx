import React from 'react';
import { FaBolt } from 'react-icons/fa';
import type { Synapse } from './types';

interface StatusViewProps {
    synapses: Synapse[];
    onOptimize: () => void;
    isThinking: boolean;
}

const StatusView: React.FC<StatusViewProps> = ({ synapses, onOptimize, isThinking }) => {
    return (
        <div className="status-view">
            <button className="optimize-btn" onClick={onOptimize} disabled={isThinking}>
                <FaBolt /> Run System Optimization
            </button>
            <h3>Connected Synapses</h3>
            <div className="synapse-list">
                {synapses.map((synapse, idx) => (
                    <div key={idx} className="synapse-card">
                        <div className="synapse-icon"><FaBolt /></div>
                        <div className="synapse-info">
                            <h4>{synapse.name}</h4>
                            <span className="synapse-category">{synapse.category}</span>
                        </div>
                        <div className={`synapse-status ${synapse.status}`}></div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default StatusView;
