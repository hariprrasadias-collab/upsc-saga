import React, { useState, useEffect, useRef } from 'react';
import './Renderers.css';

interface PodcastRendererProps {
    content: string;
    title: string;
}

const PodcastPlayer: React.FC<PodcastRendererProps> = ({ content, title }) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [progress, setProgress] = useState(0);
    const [speed, setSpeed] = useState(1.0);
    const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

    // Initialize/Re-initialize Utterance
    useEffect(() => {
        const utterance = new SpeechSynthesisUtterance(content);
        utterance.rate = speed;
        utterance.pitch = 1.0;

        const voices = window.speechSynthesis.getVoices();
        const preferredVoice = voices.find(v => v.name.includes('Google US English') || v.name.includes('Samantha'));
        if (preferredVoice) utterance.voice = preferredVoice;

        utterance.onend = () => {
            setIsPlaying(false);
            setProgress(100);
        };

        utteranceRef.current = utterance;

        // Cleanup on unmount or content change
        return () => {
            window.speechSynthesis.cancel();
        };
    }, [content]);

    // Handle Speed Change - Restart if playing to apply rate
    useEffect(() => {
        if (utteranceRef.current) {
            utteranceRef.current.rate = speed;
        }

        if (isPlaying) {
            // Cancel current speech and restart with new rate
            window.speechSynthesis.cancel();
            if (utteranceRef.current) {
                 window.speechSynthesis.speak(utteranceRef.current);
            }
        }
    }, [speed]);

    // Playback Control
    useEffect(() => {
        let interval: any;

        if (isPlaying) {
            if (!window.speechSynthesis.speaking) {
                 if (utteranceRef.current) {
                     utteranceRef.current.rate = speed;
                     window.speechSynthesis.speak(utteranceRef.current);
                 }
            } else {
                 window.speechSynthesis.resume();
            }

             interval = setInterval(() => {
                setProgress(p => (p >= 100 ? 0 : p + 1));
            }, 1000 / speed);

        } else {
            // Pause
            window.speechSynthesis.pause();
            clearInterval(interval);
        }

        return () => clearInterval(interval);
    }, [isPlaying]);

    const handleSpeedChange = () => {
        const speeds = [0.75, 1.0, 1.25, 1.5, 2.0];
        const nextIdx = (speeds.indexOf(speed) + 1) % speeds.length;
        setSpeed(speeds[nextIdx]);
    };

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

                 <button className="speed-btn" onClick={handleSpeedChange} title="Playback Speed">
                    {speed}x
                </button>

                {/* Waveform Visualizer */}
                <div className="waveform-container" style={{display: 'flex', alignItems: 'center', height: '30px', gap: '3px', flexGrow: 1, margin: '0 15px'}}>
                    {[...Array(20)].map((_, i) => (
                        <div
                            key={i}
                            className={`wave-bar ${isPlaying ? 'animating' : ''}`}
                            style={{
                                flex: 1,
                                backgroundColor: '#4ade80',
                                borderRadius: '2px',
                                height: '10%',
                                animation: isPlaying ? `wave 1s ease-in-out infinite` : 'none',
                                animationDelay: `${i * 0.05}s`
                            }}
                        ></div>
                    ))}
                </div>
                <style>{`
                    @keyframes wave {
                        0%, 100% { height: 10%; opacity: 0.5; }
                        50% { height: 100%; opacity: 1; }
                    }
                `}</style>

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
