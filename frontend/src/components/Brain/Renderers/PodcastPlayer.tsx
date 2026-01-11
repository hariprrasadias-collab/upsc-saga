import React, { useState, useEffect, useRef } from 'react';
import './Renderers.css';

interface PodcastRendererProps {
    content: string;
    title: string;
}

const PodcastPlayer: React.FC<PodcastRendererProps> = ({ content, title }) => {
    // State
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentLineIndex, setCurrentLineIndex] = useState(-1);
    const [dialogue, setDialogue] = useState<{ speaker: string, text: string }[]>([]);
    const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
    const [voicesLoaded, setVoicesLoaded] = useState(false);
    const [playbackRate, setPlaybackRate] = useState(1.1); // Default slightly energetic
    const [isZenMode, setIsZenMode] = useState(false);
    const [isSupported, setIsSupported] = useState(true);

    // Refs
    const scriptRef = useRef<HTMLDivElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    // Persistence Key
    const storageKey = `podcast_progress_${title.replace(/\s+/g, '_')}`;

    // 1. Initial Setup: Parse Content & Load Voices
    useEffect(() => {
        // Check Support
        if (!('speechSynthesis' in window)) {
            setIsSupported(false);
            return;
        }

        // Parse Dialogue
        const lines = content.split('\n').filter(line => line.trim().length > 0);
        const parsed: { speaker: string, text: string }[] = [];

        lines.forEach(line => {
            const cleanLine = line.trim();
            if (!cleanLine || cleanLine === 'Narrator' || cleanLine.startsWith('(') || cleanLine.startsWith('[')) return;

            // Regex: "**Name (emotion):** Text" or "Name: Text"
            const match = cleanLine.match(/^[\*\_]*([A-Za-z\s]+?)(?:\s*\(.*?\))?[\*\_]*:\s*(.+)/);

            if (match) {
                parsed.push({ speaker: match[1].trim(), text: match[2].trim() });
            } else {
                parsed.push({ speaker: 'Narrator', text: cleanLine });
            }
        });
        setDialogue(parsed);

        // Load Voices - PRIORITY SELECTION
        const loadVoices = () => {
            const vs = window.speechSynthesis.getVoices();
            if (vs.length > 0) {
                setVoices(vs);
                setVoicesLoaded(true);
            }
        };

        loadVoices();
        if (window.speechSynthesis.onvoiceschanged !== undefined) {
            window.speechSynthesis.onvoiceschanged = loadVoices;
        }

        // Restore Progress
        const saved = localStorage.getItem(storageKey);
        if (saved) {
            const parsedIdx = parseInt(saved, 10);
            if (!isNaN(parsedIdx) && parsedIdx < parsed.length) {
                setCurrentLineIndex(parsedIdx);
            }
        }

        return () => { window.speechSynthesis.onvoiceschanged = null; };
    }, [content, storageKey]);

    // Save Progress
    useEffect(() => {
        if (currentLineIndex >= 0) {
            localStorage.setItem(storageKey, currentLineIndex.toString());
        }
    }, [currentLineIndex, storageKey]);

    // Keyboard Shortcuts
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;

            if (e.code === 'Space') {
                e.preventDefault();
                setIsPlaying(prev => !prev);
            }
            if (e.code === 'ArrowRight') {
                e.preventDefault();
                jumpToLine(Math.min(dialogue.length - 1, currentLineIndex + 1));
            }
            if (e.code === 'ArrowLeft') {
                e.preventDefault();
                jumpToLine(Math.max(0, currentLineIndex - 1));
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [currentLineIndex, dialogue.length]);

    // Auto-Scroll
    useEffect(() => {
        if (scriptRef.current && currentLineIndex >= 0) {
            const children = scriptRef.current.children;
            if (children && children[currentLineIndex]) {
                children[currentLineIndex].scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    }, [currentLineIndex]);

    // --- ROOM TONE GENERATOR (Subconscious Realism) ---
    const audioContextRef = useRef<AudioContext | null>(null);
    const noiseNodeRef = useRef<AudioBufferSourceNode | null>(null);
    const gainNodeRef = useRef<GainNode | null>(null);

    useEffect(() => {
        if (!isSupported) return;

        if (isPlaying) {
            // Initialize Audio Context on user interaction
            if (!audioContextRef.current) {
                try {
                    const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
                    if (AudioContext) audioContextRef.current = new AudioContext();
                } catch (e) {
                    console.error("AudioContext not supported", e);
                }
            }

            const ctx = audioContextRef.current;
            if (ctx && ctx.state === 'suspended') ctx.resume();

            if (ctx) {
                try {
                    // Create Pink Noise
                    const bufferSize = 2 * ctx.sampleRate;
                    const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
                    const output = noiseBuffer.getChannelData(0);
                    let lastOut = 0;

                    for (let i = 0; i < bufferSize; i++) {
                        const white = Math.random() * 2 - 1;
                        output[i] = (lastOut + (0.02 * white)) / 1.02;
                        lastOut = output[i];
                        output[i] *= 3.5; // (roughly normalize to 0..1)
                    }

                    const noise = ctx.createBufferSource();
                    noise.buffer = noiseBuffer;
                    noise.loop = true;

                    const gain = ctx.createGain();
                    gain.gain.value = 0.008; // Very faint (Subconscious)

                    noise.connect(gain);
                    gain.connect(ctx.destination);
                    noise.start();

                    noiseNodeRef.current = noise;
                    gainNodeRef.current = gain;
                } catch (e) {
                    console.error("Audio generation failed", e);
                }
            }

        } else {
            // Stop Noise
            if (noiseNodeRef.current) {
                try { noiseNodeRef.current.stop(); } catch (e) { }
                noiseNodeRef.current = null;
            }
        }

        return () => {
            if (noiseNodeRef.current) {
                try { noiseNodeRef.current.stop(); } catch (e) { }
            }
        };
    }, [isPlaying, isSupported]);

    // 2. The Director (TTS Logic)
    useEffect(() => {
        if (!isSupported) return;

        if (!isPlaying) {
            window.speechSynthesis.cancel();
            return;
        }

        const speakLine = (index: number) => {
            if (index >= dialogue.length) {
                setIsPlaying(false);
                setCurrentLineIndex(0); // Reset to start
                return;
            }

            setCurrentLineIndex(index);
            const line = dialogue[index];

            // CLEAN Text
            const spokenText = line.text
                .replace(/[\*\_]+/g, "")
                .replace(/\[.*?\]/g, "")
                .replace(/\(.*?\)/g, "");

            const utterance = new SpeechSynthesisUtterance(spokenText);

            // --- VOICE CASTING (Priority System) ---
            const enVoices = voices.filter(v => v.lang.startsWith('en'));
            const pool = enVoices.length > 0 ? enVoices : voices;

            const isStudent = line.speaker.toLowerCase().includes('student') || line.speaker.toLowerCase().includes('curious');
            // Removed unused isExpert variable

            // Find Voices - Try "Google" or "Natural" first
            const googleFemale = pool.find(v => v.name.includes('Google US English') || v.name.includes('Google UK English Female'));
            const googleMale = pool.find(v => v.name.includes('Google UK English Male') || v.name.includes('Google') && !v.name.includes('Female'));
            const microsoftFemale = pool.find(v => v.name.includes('Zira') || v.name.includes('Eva') || v.name.includes('Natural'));
            const microsoftMale = pool.find(v => v.name.includes('David') || v.name.includes('Mark') || v.name.includes('Natural'));

            // Assignment Logic
            if (isStudent) {
                // Try to find a high-quality female voice
                utterance.voice = googleFemale || microsoftFemale || pool.find(v => v.name.includes('Female')) || pool[1] || pool[0];
            } else {
                // Try to find a high-quality male voice
                utterance.voice = googleMale || microsoftMale || pool.find(v => v.name.includes('Male')) || pool[0];
            }

            // --- STABLE AUDIO ENGINE (Anti-Robotic) ---

            // 1. BASE STATS
            // We lock PITCH to avoid robotic wobble. We vary SPEED to convey emotion.
            let pitch = 1.0;
            let rate = 1.1;
            let volume = 1.0;

            if (isStudent) {
                pitch = 1.05; // Slightly higher, clean
                rate = 1.15 * playbackRate; // Energetic
            } else {
                pitch = 0.95; // Slightly deeper, clean
                rate = 1.0 * playbackRate; // Calm
            }

            // 2. EMOTION via SPEED
            const rawText = line.text.toLowerCase();

            // Excitement -> Speed Up
            if (rawText.endsWith('!') || rawText.includes('wow') || rawText.includes('amazing') || rawText.includes('wild')) {
                rate *= 1.2;
            }
            // Questions -> Slow Down
            else if (rawText.endsWith('?') || rawText.includes('wait') || rawText.includes('really')) {
                rate *= 0.9;
            }
            // Thinking -> Pause/Slow
            else if (rawText.includes('...') || rawText.includes('hmm')) {
                rate *= 0.85;
            }
            // Banter -> Fast
            else if (rawText.split(' ').length < 6) {
                rate *= 1.1;
            }

            // Filler Optimization
            if (rawText.startsWith('like') || rawText.includes(' you know ')) {
                rate *= 1.15;
                volume = 0.9;
            }

            // Humanize Volume (Micro-Jitter)
            volume = volume * (0.95 + (Math.random() * 0.1)); // Range: 0.95 - 1.05

            // Apply
            utterance.pitch = pitch;
            utterance.rate = Math.min(Math.max(rate, 0.5), 2.5);
            utterance.volume = Math.min(volume, 1);

            // 3. ZERO-LATENCY PACING
            let pauseDuration = 50; // Tight gap

            if (rawText.endsWith('.')) pauseDuration = 200;
            if (rawText.endsWith(',')) pauseDuration = 120; // Short Breath
            if (rawText.includes('...')) pauseDuration = 400; // Thinking
            if (rawText.endsWith('?')) pauseDuration = 450;
            if (rawText.endsWith('!')) {
                pauseDuration = 10;
                // HAPTIC FEEDBACK (Impact)
                if (navigator.vibrate) navigator.vibrate(50);
            }

             // Haptics for Keywords
            if (rawText.includes('important') || rawText.includes('key')) {
                if (navigator.vibrate) navigator.vibrate(30);
            }

            utterance.onend = () => {
                setTimeout(() => speakLine(index + 1), pauseDuration);
            };

            window.speechSynthesis.speak(utterance);
        };

        if (!window.speechSynthesis.speaking) {
            speakLine(currentLineIndex >= 0 ? currentLineIndex : 0);
        } else {
            window.speechSynthesis.resume();
        }

    }, [isPlaying, dialogue, voices, playbackRate, isSupported]);

    useEffect(() => {
        return () => window.speechSynthesis.cancel();
    }, []);

    const jumpToLine = (index: number) => {
        window.speechSynthesis.cancel();
        setCurrentLineIndex(index);
    };

    // Derived State
    const currentSpeaker = currentLineIndex >= 0 ? dialogue[currentLineIndex].speaker : (dialogue[0]?.speaker || '');
    const isStudentSpeaking = currentSpeaker.toLowerCase().includes('student') || currentSpeaker.toLowerCase().includes('curious');
    const isExpertSpeaking = currentSpeaker.toLowerCase().includes('expert') || currentSpeaker.toLowerCase().includes('professor') || currentSpeaker.toLowerCase().includes('host');
    const ambientColor = isStudentSpeaking ? 'rgba(163, 113, 247, 0.2)' : (isExpertSpeaking ? 'rgba(0, 255, 242, 0.2)' : 'transparent');

    // Fix: Remove unused isExpert check in voice logic if not needed, or use it.
    // The previous error was: 'isExpert' is declared but its value is never read.
    // In "const isExpert = ...", it was defined but not used.
    // Wait, the error was on line 222.
    // Line 222 in original was: const isExpert = line.speaker.toLowerCase().includes('expert') || ...
    // It seems it was unused inside speakLine.

    const handleSpeedToggle = () => {
        const potential = [0.8, 1.0, 1.25, 1.5, 2.0];
        const idx = potential.indexOf(playbackRate);
        const next = potential[(idx + 1) % potential.length];
        setPlaybackRate(next);
    };

    // Progress
    const progress = dialogue.length > 0 ? (currentLineIndex / dialogue.length) * 100 : 0;

    if (!isSupported) {
        return <div className="podcast-error">⚠️ Audio features not supported in this browser.</div>;
    }

    return (
        <div
            ref={containerRef}
            className={`podcast-player-container glass-card ${isZenMode ? 'zen-mode' : ''}`}
            style={{
                // Phase 7: Sentient Lighting Logic
                boxShadow: isPlaying ? (() => {
                    const txt = dialogue[currentLineIndex]?.text.toLowerCase() || '';
                    let glow = ambientColor; // Default to speaker color
                    if (txt.includes('!')) glow = 'rgba(255, 68, 68, 0.6)'; // Excitement
                    if (txt.includes('wow') || txt.includes('amazing')) glow = 'rgba(255, 215, 0, 0.6)'; // Wonder
                    if (txt.includes('?')) glow = 'rgba(163, 113, 247, 0.6)'; // Question
                    return `0 20px 60px ${glow}`;
                })() : '0 20px 50px rgba(0,0,0,0.5)',
                transition: 'all 0.5s',
                border: isPlaying ? (isStudentSpeaking ? '1px solid rgba(163, 113, 247, 0.5)' : '1px solid rgba(0, 255, 242, 0.5)') : '1px solid rgba(255,255,255,0.1)',
                position: isZenMode ? 'fixed' : 'relative',
                top: isZenMode ? 0 : 'auto',
                left: isZenMode ? 0 : 'auto',
                width: isZenMode ? '100vw' : '100%',
                height: isZenMode ? '100vh' : 'auto',
                zIndex: isZenMode ? 1000 : 1,
                background: isZenMode ? '#0a0a14' : undefined,
                display: 'flex',
                flexDirection: 'column'
            }}
        >

            {/* STUDIO VISUALS - DYNAMIC CAM + 3D PARALLAX + SENTIENT LIGHTING */}
            <div
                className="podcast-studio-visual"
                onMouseMove={(e) => {
                    const el = e.currentTarget;
                    const rect = el.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    const centerX = rect.width / 2;
                    const centerY = rect.height / 2;
                    
                    // Tilt Calculation
                    const rotateX = ((y - centerY) / centerY) * -5; // Max 5deg
                    const rotateY = ((x - centerX) / centerX) * 5;
                    
                    el.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(${isPlaying ? 1.02 : 1})`;
                }}
                onMouseLeave={(e) => {
                    e.currentTarget.style.transform = `perspective(1000px) rotateX(0) rotateY(0) scale(1)`;
                }}
                style={{
                    flex: isZenMode ? 1 : '0 0 auto',
                    transition: 'transform 0.1s ease-out, opacity 0.5s, box-shadow 0.5s', 
                    transform: isPlaying
                        ? (isExpertSpeaking ? 'scale(1.05) translateX(-10px)' : (isStudentSpeaking ? 'scale(1.05) translateX(10px)' : 'scale(1)'))
                        : 'scale(1)',
                    position: 'relative',
                    overflow: 'hidden',
                    transformStyle: 'preserve-3d'
                }}
            >
                {/* 1. FILM GRAIN OVERLAY */}
                <div style={{
                    position: 'absolute', inset: 0,
                    backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 200 200\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noiseFilter\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.65\' numOctaves=\'3\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noiseFilter)\' opacity=\'0.15\'/%3E%3C/svg%3E")',
                    opacity: 0.15,
                    pointerEvents: 'none',
                    zIndex: 2,
                    mixBlendMode: 'overlay'
                }}></div>

                {/* 2. SUPER CAPTIONS (Smart Highlight) */}
                {isPlaying && currentLineIndex >= 0 && (
                    <div style={{
                        position: 'absolute',
                        bottom: '30px',
                        left: '0',
                        width: '100%',
                        textAlign: 'center',
                        zIndex: 25, // Above Emojis
                        pointerEvents: 'none',
                        padding: '0 20px',
                        transform: 'translateZ(50px)' // Pops out
                    }}>
                        <div style={{
                            color: isStudentSpeaking ? '#e0caff' : '#cafffc',
                            fontSize: dialogue[currentLineIndex].text.length < 50 ? '1.5rem' : '1.2rem',
                            fontWeight: '800',
                            lineHeight: '1.3',
                            background: 'rgba(0,0,0,0.75)',
                            padding: '16px 28px',
                            borderRadius: '24px',
                            display: 'inline-block',
                            backdropFilter: 'blur(12px)',
                            animation: 'fadeInUp 0.1s ease-out',
                            border: '1px solid rgba(255,255,255,0.15)',
                            boxShadow: '0 10px 40px rgba(0,0,0,0.5)'
                        }}>
                             {dialogue[currentLineIndex].text.split(' ').map((word, i) => {
                                // Keyword Detection (Capitalized or Specific)
                                const clean = word.replace(/[^a-zA-Z]/g, '');
                                const isKey = /^[A-Z][a-z]+/.test(clean) && clean.length > 3;
                                const isImpact = ['?', '!', 'crucial', 'important', 'key', 'must'].some(k => word.toLowerCase().includes(k));
                                
                                return (
                                    <span key={i} style={{ 
                                        color: isKey ? '#ffd700' : (isImpact ? '#ff4d4d' : 'inherit'),
                                        textShadow: isKey ? '0 0 10px rgba(255, 215, 0, 0.5)' : 'none',
                                        display: 'inline-block',
                                        transform: isImpact ? 'scale(1.15)' : 'scale(1)',
                                        marginRight: '6px',
                                        transition: 'transform 0.2s'
                                    }}>
                                        {word}
                                    </span>
                                );
                            })}
                        </div>
                    </div>
                )}

                {/* 3. EMOJI REACTIONS */}
                {isPlaying && currentLineIndex >= 0 && (
                    <div className="reaction-zone" style={{ position: 'absolute', top: '20%', left: '50%', transform: 'translateX(-50%) translateZ(30px)', zIndex: 20 }}>
                        {(dialogue[currentLineIndex].text.toLowerCase().includes('wow') || dialogue[currentLineIndex].text.includes('!')) && (
                            <div style={{ fontSize: '6rem', animation: 'floatUp 0.8s ease-out forwards', filter: 'drop-shadow(0 0 20px rgba(255,165,0,0.6))' }}>🔥</div>
                        )}
                        {(dialogue[currentLineIndex].text.toLowerCase().includes('haha') || dialogue[currentLineIndex].text.toLowerCase().includes('funny')) && (
                            <div style={{ fontSize: '6rem', animation: 'floatUp 0.8s ease-out forwards', filter: 'drop-shadow(0 0 20px rgba(255,255,0,0.6))' }}>😂</div>
                        )}
                        {(dialogue[currentLineIndex].text.includes('?')) && (
                            <div style={{ fontSize: '6rem', animation: 'floatUp 0.8s ease-out forwards', filter: 'drop-shadow(0 0 20px rgba(0,255,255,0.6))' }}>🤔</div>
                        )}
                    </div>
                )}

                <div
                    className={`avatar host ${isExpertSpeaking && isPlaying ? 'speaking active-cam' : 'inactive-cam'}`}
                    style={{
                        transform: isExpertSpeaking && isPlaying ? 'scale(1.15) translateZ(20px)' : 'scale(0.95)',
                        opacity: isStudentSpeaking && isPlaying ? 0.5 : 1,
                        transition: 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)'
                    }}
                >
                    <div className="avatar-icon">👨‍🏫</div>
                    <div className="avatar-label">Expert</div>
                </div>

                <div className="visualizer-waves" style={{ transform: 'translateZ(10px)' }}>
                    {/* ... (keep waves) ... */}
                    {isPlaying ? (
                        [...Array(5)].map((_, i) => (
                            <div key={i} className="wave-circle" style={{
                                animationDelay: `${i * 0.2}s`,
                                background: isStudentSpeaking ? '#a371f7' : '#00fff2',
                                height: `${40 + (Math.random() * 40)}px`, 
                                opacity: 0.8
                            }}></div>
                        ))
                    ) : (
                        <div style={{ color: 'white', opacity: 0.5, fontSize: '0.8rem' }}>READY</div>
                    )}
                </div>

                <div
                    className={`avatar guest ${isStudentSpeaking && isPlaying ? 'speaking active-cam' : 'inactive-cam'}`}
                    style={{
                        transform: isStudentSpeaking && isPlaying ? 'scale(1.15) translateZ(20px)' : 'scale(0.95)',
                        opacity: isExpertSpeaking && isPlaying ? 0.5 : 1,
                        transition: 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)'
                    }}
                >
                    <div className="avatar-icon">👩‍🎓</div>
                    <div className="avatar-label">Student</div>
                </div>
            </div>

            {/* HEADER & CONTROLS */}
            <div style={{ padding: '0 20px', position: 'relative', zIndex: 2 }}>
                <div className="player-header">
                    <div className="track-info" style={{ width: '100%' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <h3>{title}</h3>
                            <button
                                onClick={() => setIsZenMode(!isZenMode)}
                                style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.2rem' }}
                                title={isZenMode ? "Exit Zen Mode" : "Enter Zen Mode"}
                            >
                                {isZenMode ? '↙️' : '↗️'}
                            </button>
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '5px' }}>
                            <span className="artist" style={{ fontSize: '0.75rem', opacity: 0.75, display: 'flex', alignItems: 'center', gap: '8px' }}>
                                {isPlaying && (
                                    <span style={{
                                        color: '#ff4444',
                                        fontWeight: 'bold',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '4px',
                                        fontSize: '0.7rem',
                                        animation: 'pulse 2s infinite'
                                    }}>
                                        <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#ff4444' }}></div>
                                        LIVE
                                    </span>
                                )}
                                🎙️ AI Cast • {voices.length} Engines • {Math.round(progress)}% Complete
                            </span>
                        </div>
                    </div>
                </div>

                <div className="player-controls">
                    <button
                        className={`play-btn ${isPlaying ? 'playing' : ''}`}
                        onClick={() => setIsPlaying(!isPlaying)}
                        disabled={!voicesLoaded && voices.length === 0}
                        style={{ opacity: (!voicesLoaded && voices.length === 0) ? 0.5 : 1 }}
                        title="Spacebar to Toggle"
                    >
                        {isPlaying ? '⏸' : '▶'}
                    </button>

                    <button className="speed-btn" onClick={handleSpeedToggle} title="Playback Speed" style={{ 
                        background: 'rgba(255,255,255,0.1)', 
                        border: '1px solid rgba(255,255,255,0.2)', 
                        color: 'white', 
                        padding: '8px 12px',
                        borderRadius: '20px',
                        cursor: 'pointer',
                        fontSize: '0.8rem',
                        marginLeft: '10px'
                    }}>
                        {playbackRate}x
                    </button>

                    {/* Progress Bar */}
                    <div className="waveform-container" style={{ cursor: 'pointer', flex: 1, marginLeft: '15px' }} onClick={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect();
                        const x = e.clientX - rect.left;
                        const pct = x / rect.width;
                        const idx = Math.floor(pct * dialogue.length);
                        jumpToLine(idx);
                    }}>
                        <div
                            style={{
                                height: '100%',
                                background: isStudentSpeaking ? '#a371f7' : '#00fff2',
                                width: `${progress}%`,
                                transition: 'width 0.3s ease-out',
                                borderRadius: '4px',
                                boxShadow: '0 0 10px rgba(255,255,255,0.3)'
                            }}
                        >
                            {/* Animated Bars Effect */}
                             {[...Array(20)].map((_, i) => (
                                <div key={i} className={`wave-bar ${isPlaying ? 'animating' : ''}`} 
                                    style={{ 
                                        animationDelay: `${i * 0.05}s`,
                                        height: '100%',
                                        width: '2px',
                                        background: 'rgba(255,255,255,0.2)',
                                        display: 'inline-block',
                                        marginRight: '2px'
                                    }} 
                                />
                             ))}
                        </div>
                    </div>

                    <div className="time-display" style={{ minWidth: '45px' }}>
                        {currentLineIndex > -1 ? `${Math.floor(progress)}%` : '0%'}
                    </div>
                </div>
            </div>

            {/* SCRIPT */}
            <div className="script-teleprompter" style={{ maxHeight: isZenMode ? '60vh' : '300px', overflowY: 'auto' }}>
                <div className="script-header" style={{
                    marginBottom: '10px', fontSize: '0.75rem', color: '#666', textTransform: 'uppercase', letterSpacing: '1px',
                    display: 'flex', justifyContent: 'space-between'
                }}>
                    <span>Live Transcript</span>
                </div>
                <div className="script-content" ref={scriptRef}>
                    {dialogue.map((line, i) => {
                        const isStud = line.speaker.toLowerCase().includes('student') || line.speaker.toLowerCase().includes('curious');
                        const isActive = i === currentLineIndex;
                        const isShort = line.text.split(' ').length < 5;

                        return (
                            <div
                                key={i}
                                onClick={() => jumpToLine(i)}
                                className={`chat-bubble ${isActive ? 'active-highlight' : ''}`}
                                style={{
                                    marginBottom: '10px',
                                    opacity: currentLineIndex === -1 || isActive ? 1 : 0.4,
                                    borderLeft: isActive ? `4px solid ${isStud ? '#a371f7' : '#00fff2'}` : '4px solid transparent',
                                    paddingLeft: '10px',
                                    transition: 'all 0.3s',
                                    transform: isActive ? 'scale(1.01) translateX(5px)' : 'scale(1)',
                                    cursor: 'pointer',
                                    background: isActive ? 'rgba(255,255,255,0.05)' : 'transparent',
                                    borderRadius: '0 8px 8px 0'
                                }}
                            >
                                <strong style={{ color: isStud ? '#a371f7' : '#00fff2', fontSize: '0.75rem', textTransform: 'uppercase', marginRight: '10px' }}>
                                    {line.speaker}
                                </strong>
                                <span style={{ fontSize: '0.9rem', lineHeight: '1.4', fontStyle: isShort ? 'italic' : 'normal' }}>
                                    {line.text}
                                </span>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default PodcastPlayer;
