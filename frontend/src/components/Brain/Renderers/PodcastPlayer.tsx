import React, { useState, useEffect } from 'react';
import './Renderers.css';

interface PodcastRendererProps {
    content: string;
    title: string;
}

const PodcastPlayer: React.FC<PodcastRendererProps> = ({ content, title }) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [progress, setProgress] = useState(0);

    // Mock progress for visual effect
    useEffect(() => {
        let interval: any;
        if (isPlaying && progress < 100) {
            interval = setInterval(() => {
                setProgress(p => (p >= 100 ? 0 : p + 1));
            }, 100);

            // TTS Logic
            if (!window.speechSynthesis.speaking) {
                const utterance = new SpeechSynthesisUtterance(content);
                // Create a cleaner version of text for speech (remove Speaker names if possible)
                // For now, reading raw content is fine, maybe slightly sped up
                utterance.rate = 1.1;
                utterance.pitch = 1.0;

                // Try to find a good English voice
                const voices = window.speechSynthesis.getVoices();
                const preferredVoice = voices.find(v => v.name.includes('Google US English') || v.name.includes('Samantha'));
                if (preferredVoice) utterance.voice = preferredVoice;

                utterance.onend = () => {
                    setIsPlaying(false);
                    setProgress(100);
                };

                window.speechSynthesis.speak(utterance);
            } else {
                window.speechSynthesis.resume();
            }

        } else if (!isPlaying) {
            window.speechSynthesis.pause();
        }

        return () => clearInterval(interval);
    }, [isPlaying]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            window.speechSynthesis.cancel();
        };
    }, []);

    return (
        <div className="podcast-player-container glass-card">
            <div className="player-header">
                <div className="album-art">🎙️</div>
                <div className="track-info">
                    <h3>{title}</h3>
                    <span className="artist">Artificial Intelligence Host (TTS Enabled)</span>
                </div>
            </div>

            <div className="player-controls">
                <button
                    className={`play-btn ${isPlaying ? 'playing' : ''}`}
                    onClick={() => setIsPlaying(!isPlaying)}
                >
                    {isPlaying ? '⏸' : '▶'}
                </button>

                {/* Waveform Visualizer */}
                <div className="waveform-container">
                    {[...Array(20)].map((_, i) => (
                        <div
                            key={i}
                            className={`wave-bar ${isPlaying ? 'animating' : ''}`}
                            style={{ animationDelay: `${i * 0.1}s` }}
                        ></div>
                    ))}
                </div>

                <div className="time-display">
                    {Math.floor(progress / 60)}:{(progress % 60).toString().padStart(2, '0')}
                </div>
            </div>

            <div className="script-teleprompter">
                <h3>Transport Script</h3>
                <div className="script-content">
                    {content.split('\n').map((line, i) => (
                        <p key={i}>{line}</p>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default PodcastPlayer;
