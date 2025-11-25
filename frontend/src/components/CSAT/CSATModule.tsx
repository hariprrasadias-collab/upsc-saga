import React, { useState } from 'react';
import './CSAT.css';
import PracticeMode from './PracticeMode';
import FormulaSheet from './FormulaSheet';

const CSATModule: React.FC = () => {
    const [activeTab, setActiveTab] = useState<'practice' | 'formulas'>('practice');

    return (
        <div className="csat-container">
            <header className="csat-header">
                <div className="header-content">
                    <h1>CSAT Preparation</h1>
                    <p>Master Quant, Reasoning, and Reading Comprehension</p>
                </div>
                <div className="csat-tabs">
                    <button
                        className={`tab-btn ${activeTab === 'practice' ? 'active' : ''}`}
                        onClick={() => setActiveTab('practice')}
                    >
                        Practice Mode
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'formulas' ? 'active' : ''}`}
                        onClick={() => setActiveTab('formulas')}
                    >
                        Formula Sheet
                    </button>
                </div>
            </header>

            <div className="csat-content">
                {activeTab === 'practice' && <PracticeMode />}
                {activeTab === 'formulas' && <FormulaSheet />}
            </div>
        </div>
    );
};

export default CSATModule;
