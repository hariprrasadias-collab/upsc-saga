import React, { useState, useRef, useEffect } from 'react';
import './AmbientSoundPlayer.css';

export interface AmbientSound {
    id: string;
    name: string;
    icon: string;
    url: string;
}

// Free ambient sound URLs (using Google Actions Sound Library for reliability)
const AMBIENT_SOUNDS: AmbientSound[] = [
    { id: 'rain', name: 'Rain', icon: '🌧️', url: 'https://actions.google.com/sounds/v1/weather/rain_heavy_loud.ogg' },
    { id: 'forest', name: 'Forest', icon: '🌲', url: 'https://actions.google.com/sounds/v1/ambiences/jungle_atmosphere_night.ogg' },
    { id: 'ocean', name: 'Ocean', icon: '🌊', url: 'https://actions.google.com/sounds/v1/water/waves_crashing.ogg' },
    { id: 'fire', name: 'Fireplace', icon: '🔥', url: 'https://actions.google.com/sounds/v1/ambiences/fire.ogg' },
    { id: 'whitenoise', name: 'Wind', icon: '💨', url: 'https://actions.google.com/sounds/v1/weather/wind.ogg' }
];

export const AmbientSoundPlayer: React.FC = () => {
    const [activeSounds, setActiveSounds] = useState<Set<string>>(new Set());
    const [volumes, setVolumes] = useState<Map<string, number>>(new Map());
    const [masterVolume, setMasterVolume] = useState(0.5);
    const audioRefs = useRef<Map<string, HTMLAudioElement>>(new Map());

    // Initialize audio elements
    useEffect(() => {
        AMBIENT_SOUNDS.forEach(sound => {
            if (!audioRefs.current.has(sound.id)) {
                const audio = new Audio(sound.url);
                audio.loop = true;
                audio.volume = (volumes.get(sound.id) || 0.5) * masterVolume;
                audioRefs.current.set(sound.id, audio);
            }
        });

        return () => {
            audioRefs.current.forEach(audio => {
                audio.pause();
                audio.src = '';
            });
            audioRefs.current.clear();
        };
    }, []);

    // Update volumes when master or individual changes
    useEffect(() => {
        audioRefs.current.forEach((audio, id) => {
            audio.volume = (volumes.get(id) || 0.5) * masterVolume;
        });
    }, [masterVolume, volumes]);

    const toggleSound = (soundId: string) => {
        const audio = audioRefs.current.get(soundId);
        if (!audio) return;

        const newActiveSounds = new Set(activeSounds);

        if (activeSounds.has(soundId)) {
            audio.pause();
            audio.currentTime = 0;
            newActiveSounds.delete(soundId);
        } else {
            audio.play().catch(err => console.log('Audio play failed:', err));
            newActiveSounds.add(soundId);
        }

        setActiveSounds(newActiveSounds);
    };

    const setVolume = (soundId: string, volume: number) => {
        const newVolumes = new Map(volumes);
        newVolumes.set(soundId, volume);
        setVolumes(newVolumes);

        const audio = audioRefs.current.get(soundId);
        if (audio) {
            audio.volume = volume * masterVolume;
        }
    };

    const stopAll = () => {
        audioRefs.current.forEach(audio => {
            audio.pause();
            audio.currentTime = 0;
        });
        setActiveSounds(new Set());
    };

    return (
        <div className="ambient-sound-player">
            <div className="sound-header">
                <span className="sound-title">🎵 AMBIENT SOUNDS</span>
                {activeSounds.size > 0 && (
                    <button onClick={stopAll} className="stop-all-btn">Stop All</button>
                )}
            </div>

            <div className="master-volume">
                <label>
                    <span>Master Volume</span>
                    <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={masterVolume}
                        onChange={(e) => setMasterVolume(parseFloat(e.target.value))}
                        className="volume-slider master"
                    />
                    <span className="volume-value">{Math.round(masterVolume * 100)}%</span>
                </label>
            </div>

            <div className="sounds-grid">
                {AMBIENT_SOUNDS.map(sound => {
                    const isActive = activeSounds.has(sound.id);
                    const volume = volumes.get(sound.id) || 0.5;

                    return (
                        <div key={sound.id} className={`sound-card ${isActive ? 'active' : ''}`}>
                            <button
                                className="sound-toggle"
                                onClick={() => toggleSound(sound.id)}
                            >
                                <span className="sound-icon">{sound.icon}</span>
                                <span className="sound-name">{sound.name}</span>
                            </button>

                            {isActive && (
                                <div className="sound-volume-control">
                                    <input
                                        type="range"
                                        min="0"
                                        max="1"
                                        step="0.1"
                                        value={volume}
                                        onChange={(e) => setVolume(sound.id, parseFloat(e.target.value))}
                                        className="volume-slider"
                                    />
                                    <span className="volume-value">{Math.round(volume * 100)}%</span>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            <div className="sound-tip">
                💡 Tip: Mix multiple sounds for a custom ambience
            </div>
        </div>
    );
};

