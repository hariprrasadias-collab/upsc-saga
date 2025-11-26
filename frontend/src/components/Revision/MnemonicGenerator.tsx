import React, { useState } from 'react';
import './MnemonicGenerator.css';

interface MnemonicGeneratorProps {
    onMnemonicGenerated?: (mnemonic: string) => void;
}

const MnemonicGenerator: React.FC<MnemonicGeneratorProps> = ({ onMnemonicGenerated }) => {
    const [text, setText] = useState('');
    const [mnemonicType, setMnemonicType] = useState('facts');
    const [mnemonic, setMnemonic] = useState('');
    const [generating, setGenerating] = useState(false);

    const handleGenerate = async () => {
        if (!text.trim()) {
            alert('Please enter some content');
            return;
        }

        setGenerating(true);
        try {
            const response = await fetch('http://localhost:5000/api/revision/mnemonic', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: text,
                    type: mnemonicType
                })
            });

            const data = await response.json();
            if (data.success) {
                setMnemonic(data.mnemonic);
                if (onMnemonicGenerated) {
                    onMnemonicGenerated(data.mnemonic);
                }
            } else {
                alert('Failed to generate mnemonic');
            }
        } catch (error) {
            console.error('Error generating mnemonic:', error);
            alert('Error generating mnemonic');
        } finally {
            setGenerating(false);
        }
    };

    const handleCopy = () => {
        navigator.clipboard.writeText(mnemonic);
        alert('Mnemonic copied to clipboard!');
    };

    return (
        <div className="mnemonic-generator">
            <h2>🧠 Mnemonic Generator</h2>
            <p className="mnemonic-subtitle">Create memory aids for UPSC topics</p>

            <div className="mnemonic-form">
                <label className="input-label">What do you want to remember?</label>
                <textarea
                    className="mnemonic-textarea"
                    placeholder="Enter facts, dates, list of items, or concept..."
                    rows={5}
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                />

                <label className="input-label">Mnemonic Type</label>
                <div className="type-selector">
                    <button
                        className={`type-btn ${mnemonicType === 'facts' ? 'active' : ''}`}
                        onClick={() => setMnemonicType('facts')}
                    >
                        📚 Facts
                    </button>
                    <button
                        className={`type-btn ${mnemonicType === 'dates' ? 'active' : ''}`}
                        onClick={() => setMnemonicType('dates')}
                    >
                        📅 Dates
                    </button>
                    <button
                        className={`type-btn ${mnemonicType === 'list' ? 'active' : ''}`}
                        onClick={() => setMnemonicType('list')}
                    >
                        📝 List
                    </button>
                    <button
                        className={`type-btn ${mnemonicType === 'concept' ? 'active' : ''}`}
                        onClick={() => setMnemonicType('concept')}
                    >
                        💡 Concept
                    </button>
                </div>

                <button
                    className="generate-mnemonic-btn"
                    onClick={handleGenerate}
                    disabled={generating || !text.trim()}
                >
                    {generating ? '✨ Creating Memory Aid...' : '🎯 Generate Mnemonic'}
                </button>
            </div>

            {mnemonic && (
                <div className="mnemonic-result">
                    <div className="result-header">
                        <h3>Your Mnemonic:</h3>
                        <button className="copy-btn" onClick={handleCopy}>
                            📋 Copy
                        </button>
                    </div>
                    <div className="mnemonic-box">
                        <p>{mnemonic}</p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MnemonicGenerator;
