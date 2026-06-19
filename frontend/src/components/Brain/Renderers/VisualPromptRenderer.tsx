import React, { useState, useEffect } from 'react';
import './Renderers.css';
import { FaDownload, FaCopy, FaRocket, FaMagic, FaCog, FaChevronDown, FaChevronUp, FaRandom, FaExpand, FaPalette, FaSave, FaThLarge, FaSquare, FaMicrophone, FaBolt, FaFileAlt } from 'react-icons/fa';
import { API_BASE_URL } from '../../../config';

interface VisualPromptRendererProps {
    content: string; // The raw prompt text
}

interface ImageHistoryItem {
    url: string;
    prompt: string;
    seed: number;
    model: string;
    timestamp: number;
}

interface Preset {
    name: string;
    model: string;
    aspectRatio: string;
    negativePrompt: string;
    tags: string[];
}

const MODELS = [
    { id: 'flux', name: 'Flux (Standard)' },
    { id: 'flux-realism', name: 'Flux Realism' },
    { id: 'flux-anime', name: 'Flux Anime' },
    { id: 'flux-3d', name: 'Flux 3D' },
    { id: 'any-dark', name: 'Any Dark' },
    { id: 'turbo', name: 'Turbo (Fast)' },
    { id: 'midjourney', name: 'Midjourney Style' },
];

const ASPECT_RATIOS = [
    { id: '16:9', width: 800, height: 450, label: 'Cinematic (16:9)' },
    { id: '1:1', width: 512, height: 512, label: 'Square (1:1)' },
    { id: '4:3', width: 800, height: 600, label: 'Classic (4:3)' },
    { id: '3:4', width: 600, height: 800, label: 'Portrait (3:4)' },
    { id: '9:16', width: 450, height: 800, label: 'Mobile (9:16)' },
];

const STYLE_MATRIX = {
    "Lighting": ["Cinematic Lighting", "Volumetric Fog", "Bioluminescent", "Golden Hour", "Neon Lights", "Studio Lighting", "Ray Tracing"],
    "Camera": ["Wide Angle", "Macro Lens", "Bokeh", "Fish Eye", "Drone View", "Isometric", "GoPro"],
    "Art Style": ["Cyberpunk", "Steampunk", "Watercolor", "Oil Painting", "Ukiyo-e", "Synthwave", "Pixel Art", "Vaporwave", "Concept Art"],
    "Vibe": ["Ethereal", "Gritty", "Dreamy", "Apocalyptic", "Futuristic", "Retro", "Minimalist"]
};

const MAGIC_MODIFIERS = [
    "highly detailed", "8k resolution", "cinematic lighting", "photorealistic",
    "masterpiece", "sharp focus", "intricate details", "unreal engine 5 render",
    "volumetric lighting", "global illumination"
];

const PROMPT_TEMPLATES = [
    { label: "Cyberpunk Character", text: "A cyberpunk street samurai, neon lights, rainy street, high tech armor, detailed face, futuristic city background" },
    { label: "Fantasy Landscape", text: "Epic fantasy landscape, floating islands, waterfalls, magical aura, detailed clouds, 8k resolution, matte painting" },
    { label: "Isometric Room", text: "Isometric view of a cozy gamer room, neon lighting, detailed computer setup, posters, low poly style, 3d render" },
    { label: "Product Shot", text: "Professional product photography of a [ITEM], studio lighting, neutral background, sharp focus, 4k" },
    { label: "Logo Design", text: "Minimalist vector logo of a [SUBJECT], flat design, simple shapes, white background, professional branding" }
];

// Helper to simulate stats
const getRandomStat = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1) + min);

const VisualPromptRenderer: React.FC<VisualPromptRendererProps> = ({ content }) => {
    const [prompt, setPrompt] = useState(content);
    const [negativePrompt, setNegativePrompt] = useState("");
    const [copied, setCopied] = useState(false);

    // State for generation
    const [isGenerating, setIsGenerating] = useState(false);
    const [generationLogs, setGenerationLogs] = useState<string[]>([]);

    // Single View State
    const [generatedImage, setGeneratedImage] = useState<string | null>(null);

    // Grid View State
    const [viewMode, setViewMode] = useState<'single' | 'grid'>('single');
    const [gridImages, setGridImages] = useState<{ url: string, model: string }[]>([]);

    const [imageLoading, setImageLoading] = useState(false);
    const [imageError, setImageError] = useState(false);

    // Advanced Settings
    const [showSettings, setShowSettings] = useState(false);
    const [showStyleMatrix, setShowStyleMatrix] = useState(false);
    const [showTemplates, setShowTemplates] = useState(false);
    const [model, setModel] = useState('flux');
    const [aspectRatio, setAspectRatio] = useState('16:9');
    const [seed, setSeed] = useState<number>(Math.floor(Math.random() * 10000));
    const [randomSeed, setRandomSeed] = useState(true);

    const [history, setHistory] = useState<ImageHistoryItem[]>([]);

    // Presets
    const [presets, setPresets] = useState<Preset[]>([]);
    const [presetName, setPresetName] = useState("");
    const [showPresets, setShowPresets] = useState(false);

    // Voice
    const [isListening, setIsListening] = useState(false);

    // Neural HUD Stats
    const [hudStats, setHudStats] = useState({ vram: 0, ops: 0, entropy: 0 });

    useEffect(() => {
        setPrompt(content);
    }, [content]);

    // HUD Update Loop
    useEffect(() => {
        let interval: any;
        if (isGenerating || imageLoading) {
            interval = setInterval(() => {
                setHudStats({
                    vram: getRandomStat(40, 95),
                    ops: getRandomStat(120, 300),
                    entropy: getRandomStat(10, 99)
                });
            }, 800);
        }
        return () => clearInterval(interval);
    }, [isGenerating, imageLoading]);

    const handleCopy = () => {
        navigator.clipboard.writeText(prompt);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const handleMagicEnhance = () => {
        const currentLower = prompt.toLowerCase();
        const availableModifiers = MAGIC_MODIFIERS.filter(m => !currentLower.includes(m.toLowerCase()));

        if (availableModifiers.length === 0) return;

        const toAdd = availableModifiers.sort(() => 0.5 - Math.random()).slice(0, 3);
        setPrompt(prev => {
            const separator = prev.trim().endsWith(',') || prev.trim().endsWith('.') ? ' ' : ', ';
            return `${prev.trim()}${separator}${toAdd.join(', ')}`;
        });
    };

    const addStyleTag = (tag: string) => {
        setPrompt(prev => {
            if (prev.includes(tag)) return prev;
            const separator = prev.trim().endsWith(',') || prev.trim().endsWith('.') ? ' ' : ', ';
            return `${prev.trim()}${separator}${tag}`;
        });
    };

    const sanitizePromptForImage = (text: string): string => {
        // AI-generated visual prompts are often long paragraphs.
        // Image APIs need concise, comma-separated tags.
        // Strategy: extract key phrases and limit length.
        let cleaned = text
            .replace(/\n+/g, ', ')           // newlines → commas
            .replace(/["""'']/g, '')          // remove quotes
            .replace(/\([^)]*\)/g, '')        // remove parentheticals
            .replace(/\s{2,}/g, ' ')          // collapse whitespace
            .replace(/,\s*,/g, ',')           // remove double commas
            .trim();

        // If prompt is very long (AI-generated paragraph), take just the first 2 sentences
        // and append style keywords
        if (cleaned.length > 400) {
            const sentences = cleaned.split(/[.!?]+/).filter(s => s.trim().length > 5);
            cleaned = sentences.slice(0, 2).join('. ').trim();
            // Append generic quality tags
            cleaned += ', highly detailed, 8k resolution, cinematic lighting';
        }

        return cleaned.slice(0, 500);
    };

    const buildPromptText = (pText: string, pNegative: string): string => {
        const sanitized = sanitizePromptForImage(pText);
        return pNegative ? `${sanitized} excluding ${pNegative}` : sanitized;
    }

    const parsePrompt = () => {
        let finalPrompt = prompt;
        let finalSeed = randomSeed ? Math.floor(Math.random() * 10000) : seed;
        let finalNegative = negativePrompt;
        let width = 0;
        let height = 0;

        // Parse --seed
        const seedMatch = finalPrompt.match(/--seed\s+(\d+)/);
        if (seedMatch) {
            finalSeed = parseInt(seedMatch[1]);
            finalPrompt = finalPrompt.replace(seedMatch[0], '');
            setSeed(finalSeed);
            setRandomSeed(false);
        } else if (randomSeed) {
            setSeed(finalSeed); // Sync UI
        }

        // Parse --no
        const noMatch = finalPrompt.match(/--no\s+([\w\s,]+)/);
        if (noMatch) {
            finalNegative = `${finalNegative} ${noMatch[1]}`.trim();
            finalPrompt = finalPrompt.replace(noMatch[0], '');
            setNegativePrompt(finalNegative);
        }

        // Parse --ar
        const arMatch = finalPrompt.match(/--ar\s+(\d+:\d+)/);
        if (arMatch) {
            const foundAr = ASPECT_RATIOS.find(ar => ar.id === arMatch[1]);
            if (foundAr) {
                setAspectRatio(foundAr.id);
                width = foundAr.width;
                height = foundAr.height;
            }
            finalPrompt = finalPrompt.replace(arMatch[0], '');
        }

        if (width === 0) {
            const selectedRatio = ASPECT_RATIOS.find(r => r.id === aspectRatio) || ASPECT_RATIOS[0];
            width = selectedRatio.width;
            height = selectedRatio.height;
        }

        return { finalPrompt: finalPrompt.trim(), finalSeed, finalNegative, width, height };
    }

    const generateViaBackend = async (promptText: string): Promise<string | null> => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/generate-image`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: promptText })
            });
            const data = await response.json();
            if (data.success && data.image_url) {
                return data.image_url;
            }
            console.error('Image gen failed:', data.error);
            return null;
        } catch (e) {
            console.error('Image gen request failed:', e);
            return null;
        }
    };

    const handleGenerate = async (_isUpscale: boolean = false) => {
        if (isGenerating) return;
        setIsGenerating(true);
        setGeneratedImage(null);
        setGridImages([]);
        setImageError(false);
        setGenerationLogs(["Initializing Nano Banana (Gemini) Neural Network..."]);

        const { finalPrompt, finalSeed, finalNegative } = parsePrompt();
        const promptText = buildPromptText(finalPrompt, finalNegative);

        // Progress logs 
        const sequence = [
            { text: `Parsing semantics...`, delay: 800 },
            { text: `Sending to Gemini Image Generator (Seed: ${finalSeed})...`, delay: 1500 },
            { text: "Generating image via Nano Banana...", delay: 3000 },
        ];
        sequence.forEach(({ text, delay }) => {
            setTimeout(() => setGenerationLogs(prev => [...prev, text]), delay);
        });

        try {
            const imageUrl = await generateViaBackend(promptText);
            if (imageUrl) {
                setGeneratedImage(imageUrl);
                setImageLoading(false);
                addToHistory(imageUrl, finalPrompt, finalSeed, 'gemini');
                setGenerationLogs(prev => [...prev, '✅ Image generated successfully!']);
            } else {
                setImageError(true);
                setGenerationLogs(prev => [...prev, '❌ Generation failed. Try again.']);
            }
        } catch (e) {
            setImageError(true);
            setGenerationLogs(prev => [...prev, '❌ Error connecting to image service.']);
        } finally {
            setIsGenerating(false);
        }
    };

    const addToHistory = (url: string, promptText: string, seedVal: number, modelVal: string) => {
        const newItem: ImageHistoryItem = {
            url,
            prompt: promptText,
            seed: seedVal,
            model: modelVal,
            timestamp: Date.now()
        };
        setHistory(prev => [newItem, ...prev].slice(0, 10));
    };

    const handleRemix = () => {
        setRandomSeed(true);
        setTimeout(() => handleGenerate(false), 0);
    };

    const handleChaos = () => {
        setRandomSeed(true);
        // Pick random model
        const randomModel = MODELS[Math.floor(Math.random() * MODELS.length)].id;
        setModel(randomModel);

        // Pick random Aspect Ratio
        const randomAr = ASPECT_RATIOS[Math.floor(Math.random() * ASPECT_RATIOS.length)].id;
        setAspectRatio(randomAr);

        // Add 3 random style tags
        const allTags = Object.values(STYLE_MATRIX).flat();
        const randomTags = Array.from({ length: 3 }, () => allTags[Math.floor(Math.random() * allTags.length)]);

        setPrompt(prev => {
            let p = prev;
            randomTags.forEach(tag => {
                if (!p.includes(tag)) p += `, ${tag}`;
            });
            return p;
        });

        setTimeout(() => handleGenerate(false), 100);
    };

    const handleVoiceInput = () => {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert("Voice input not supported in this browser.");
            return;
        }

        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        const recognition = new SpeechRecognition();

        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => setIsListening(true);
        recognition.onend = () => setIsListening(false);

        recognition.onresult = (event: any) => {
            const transcript = event.results[0][0].transcript;
            setPrompt(prev => prev + " " + transcript);
        };

        recognition.start();
    };

    const downloadImage = async (imageUrl: string) => {
        try {
            const response = await fetch(imageUrl);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `brain-vault-render-${Date.now()}.png`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (e) {
            console.error("Download failed:", e);
            window.open(imageUrl, '_blank');
        }
    };

    const restoreFromHistory = (item: ImageHistoryItem) => {
        setPrompt(item.prompt);
        setSeed(item.seed);
        setRandomSeed(false);
        setModel(item.model === 'grid-mix' ? 'flux' : item.model);
        setViewMode('single');
        setGeneratedImage(item.url);
        setImageLoading(true);
    };

    const savePreset = () => {
        if (!presetName) return;
        const newPreset: Preset = {
            name: presetName,
            model,
            aspectRatio,
            negativePrompt,
            tags: []
        };
        setPresets(prev => [...prev, newPreset]);
        setPresetName("");
        setShowPresets(false);
    };

    const loadPreset = (preset: Preset) => {
        setModel(preset.model);
        setAspectRatio(preset.aspectRatio);
        setNegativePrompt(preset.negativePrompt);
        setShowPresets(false);
    };

    const extractTags = (text: string) => {
        const parts = text.split(',').map(s => s.trim());
        const tags = parts.filter(p => p.length < 25 && (p.includes('style') || p.includes('lighting') || p.includes('render') || p.startsWith('--')));
        return tags;
    };

    const tags = extractTags(prompt);

    return (
        <div className="visual-prompt-container glass-card">
            <div className="vp-header">
                <span className="vp-icon">🎨</span>
                <span className="vp-title">Generative Art Terminal</span>
                <div className="vp-status">{isGenerating || imageLoading ? 'PROCESSING' : 'READY'}</div>
            </div>

            <div className="vp-toolbar">
                <div className="vp-toolbar-group">
                    <button
                        className={`settings-toggle-btn ${viewMode === 'single' ? 'active' : ''}`}
                        onClick={() => setViewMode('single')}
                        title="Single View"
                    >
                        <FaSquare /> Single
                    </button>
                    <button
                        className={`settings-toggle-btn ${viewMode === 'grid' ? 'active' : ''}`}
                        onClick={() => setViewMode('grid')}
                        title="Compare Models (Grid)"
                    >
                        <FaThLarge /> Compare
                    </button>
                </div>

                <div className="vp-toolbar-group">
                    <button
                        className={`settings-toggle-btn ${showTemplates ? 'active' : ''}`}
                        onClick={() => setShowTemplates(!showTemplates)}
                    >
                        <FaFileAlt /> Templates
                    </button>
                    <button
                        className={`settings-toggle-btn ${showPresets ? 'active' : ''}`}
                        onClick={() => setShowPresets(!showPresets)}
                    >
                        <FaSave /> Presets
                    </button>
                    <button
                        className={`settings-toggle-btn ${showStyleMatrix ? 'active' : ''}`}
                        onClick={() => setShowStyleMatrix(!showStyleMatrix)}
                    >
                        <FaPalette /> Styles
                    </button>
                    <button
                        className={`settings-toggle-btn ${showSettings ? 'active' : ''}`}
                        onClick={() => setShowSettings(!showSettings)}
                    >
                        <FaCog /> Config {showSettings ? <FaChevronUp /> : <FaChevronDown />}
                    </button>
                </div>
            </div>

            {/* Templates Panel */}
            {showTemplates && (
                <div className="vp-presets-panel">
                    <h4 className="style-cat-title">Quick Start Templates</h4>
                    <div className="preset-list">
                        {PROMPT_TEMPLATES.map(t => (
                            <div key={t.label} className="preset-item" onClick={() => { setPrompt(t.text); setShowTemplates(false); }}>
                                <span className="preset-name">{t.label}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Presets Modal/Panel */}
            {showPresets && (
                <div className="vp-presets-panel">
                    <div className="preset-save-row">
                        <input
                            type="text"
                            className="vp-input"
                            placeholder="New Preset Name..."
                            value={presetName}
                            onChange={(e) => setPresetName(e.target.value)}
                        />
                        <button className="vp-btn-mini" onClick={savePreset}>Save</button>
                    </div>
                    <div className="preset-list">
                        {presets.length === 0 && <div className="no-presets">No saved presets.</div>}
                        {presets.map(p => (
                            <div key={p.name} className="preset-item" onClick={() => loadPreset(p)}>
                                <span className="preset-name">{p.name}</span>
                                <span className="preset-details">{p.model} • {p.aspectRatio}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {showStyleMatrix && (
                <div className="vp-style-matrix">
                    {Object.entries(STYLE_MATRIX).map(([category, styles]) => (
                        <div key={category} className="style-category">
                            <h4 className="style-cat-title">{category}</h4>
                            <div className="style-tags">
                                {styles.map(style => (
                                    <button
                                        key={style}
                                        className="style-tag-btn"
                                        onClick={() => addStyleTag(style)}
                                    >
                                        {style}
                                    </button>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {showSettings && (
                <div className="vp-settings-panel">
                    <div className="vp-control-group">
                        <label className="vp-label">Model Architecture</label>
                        <select
                            className="vp-select"
                            value={model}
                            onChange={(e) => setModel(e.target.value)}
                            disabled={viewMode === 'grid'}
                        >
                            {MODELS.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
                        </select>
                        {viewMode === 'grid' && <span className="vp-helper-text">Grid mode uses 4 fixed models.</span>}
                    </div>

                    <div className="vp-control-group">
                        <label className="vp-label">Aspect Ratio</label>
                        <select
                            className="vp-select"
                            value={aspectRatio}
                            onChange={(e) => setAspectRatio(e.target.value)}
                        >
                            {ASPECT_RATIOS.map(r => <option key={r.id} value={r.id}>{r.label}</option>)}
                        </select>
                    </div>

                    <div className="vp-control-group">
                        <label className="vp-label">Seed (Empty = Random)</label>
                        <div style={{ display: 'flex', gap: '5px' }}>
                            <input
                                type="number"
                                className="vp-input"
                                value={randomSeed ? '' : seed}
                                placeholder="Random"
                                onChange={(e) => {
                                    setSeed(parseInt(e.target.value) || 0);
                                    setRandomSeed(false);
                                }}
                                style={{ width: '100px' }}
                            />
                            <button
                                className="vp-btn-mini"
                                onClick={() => {
                                    setRandomSeed(true);
                                    setSeed(Math.floor(Math.random() * 10000));
                                }}
                                title="Randomize"
                                style={{ background: 'transparent', color: '#fff', border: '1px solid #333', cursor: 'pointer' }}
                            >
                                <FaRandom />
                            </button>
                        </div>
                    </div>

                    <div className="vp-control-group full-width">
                        <label className="vp-label">Negative Prompt (Exclude)</label>
                        <input
                            type="text"
                            className="vp-input"
                            value={negativePrompt}
                            placeholder="blur, low quality, distorted, watermark..."
                            onChange={(e) => setNegativePrompt(e.target.value)}
                        />
                    </div>
                </div>
            )}

            <div className="vp-terminal">
                <div className="vp-command-line">
                    <span className="cmd-prompt">/imagine prompt:</span>
                    <textarea
                        className="vp-textarea"
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        spellCheck="false"
                        placeholder="Describe your vision... (Tip: use --ar 16:9 or --no blur)"
                    />
                    <button
                        className={`mic-btn ${isListening ? 'listening' : ''}`}
                        onClick={handleVoiceInput}
                        title="Voice Input"
                    >
                        <FaMicrophone />
                    </button>
                </div>
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '5px', gap: '10px' }}>
                    <button className="magic-btn chaos" onClick={handleChaos} title="Randomize Settings & Style">
                        <FaBolt /> Chaos Mode
                    </button>
                    <button className="magic-btn secondary" onClick={handleRemix} title="Remix with random seed">
                        <FaRandom /> Remix
                    </button>
                    <button className="magic-btn" onClick={handleMagicEnhance} title="Add magic modifiers">
                        <FaMagic /> Magic Enhance
                    </button>
                </div>

                {generationLogs.length > 0 && (
                    <div className="vp-logs">
                        {generationLogs.map((log, i) => (
                            <div key={i} className="log-line">
                                <span className="log-prefix">{'>'}</span> {log}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Image Section */}
            {(generatedImage || gridImages.length > 0 || imageLoading) && (
                <div className={`vp-result ${viewMode === 'grid' ? 'grid-mode' : ''}`}>

                    {/* Neural HUD Overlay */}
                    {(imageLoading || isGenerating) && (
                        <div className="neural-hud">
                            <div className="hud-row">
                                <span className="hud-label">VRAM ALLOC</span>
                                <span className="hud-value">{hudStats.vram}%</span>
                            </div>
                            <div className="hud-row">
                                <span className="hud-label">TENSOR OPS</span>
                                <span className="hud-value">{hudStats.ops} TFLOPS</span>
                            </div>
                            <div className="hud-row">
                                <span className="hud-label">ENTROPY</span>
                                <span className="hud-value">{hudStats.entropy}</span>
                            </div>
                        </div>
                    )}

                    {/* Matrix Scanline Overlay */}
                    {(imageLoading || isGenerating) && <div className="scanline-overlay"></div>}

                    {imageLoading && !imageError && (
                        <div className="image-loader">
                            <div className="spinner"></div>
                            <span>Rendering neural pathways...</span>
                        </div>
                    )}

                    {/* Single View */}
                    {viewMode === 'single' && generatedImage && !imageError && (
                        <>
                            <img
                                src={generatedImage}
                                alt="Generated Visualization"
                                className="generated-img"
                                onError={() => {
                                    setImageLoading(false);
                                    setImageError(true);
                                }}
                            />
                            {!imageLoading && (
                                <div className="vp-overlay">
                                    <button className="download-img-btn" onClick={() => handleGenerate(true)}>
                                        <FaExpand /> Upscale 2x
                                    </button>
                                    <button className="download-img-btn" onClick={() => downloadImage(generatedImage)}>
                                        <FaDownload /> Save
                                    </button>
                                </div>
                            )}
                        </>
                    )}

                    {/* Grid View */}
                    {viewMode === 'grid' && gridImages.length > 0 && !imageError && (
                        <div className="vp-grid-layout" style={{ display: imageLoading ? 'none' : 'grid' }}>
                            {gridImages.map((img, idx) => (
                                <div key={idx} className="vp-grid-item">
                                    <img
                                        src={img.url}
                                        alt={`Model ${img.model}`}
                                        onLoad={() => {
                                            // Simple logic: if last image loads, stop loading
                                            if (idx === gridImages.length - 1) setImageLoading(false);
                                        }}
                                    />
                                    <span className="grid-label">{img.model}</span>
                                    <button className="grid-save-btn" onClick={() => downloadImage(img.url)}><FaDownload /></button>
                                </div>
                            ))}
                        </div>
                    )}

                    {imageError && (
                        <div className="error-message" style={{ color: '#f85149', padding: '20px', textAlign: 'center' }}>
                            <p>⚠️ Image generation service (Pollinations.ai) is currently unavailable.</p>
                            <p style={{ color: '#8b949e', fontSize: '0.85rem', marginTop: '5px' }}>The external API is experiencing an outage. You can copy the prompt and use it in other generators.</p>
                            <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', marginTop: '15px' }}>
                                <button
                                    className="vp-action-btn primary"
                                    onClick={() => {
                                        setImageError(false);
                                        handleGenerate(false);
                                    }}
                                >
                                    <FaRocket /> Retry
                                </button>
                                <button
                                    className="vp-action-btn"
                                    onClick={() => {
                                        navigator.clipboard.writeText(prompt);
                                        alert('Prompt copied! Paste it in Midjourney, DALL-E, or any image generator.');
                                    }}
                                >
                                    <FaCopy /> Copy Prompt
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {tags.length > 0 && !generatedImage && !imageLoading && (
                <div className="vp-tags">
                    {tags.map((tag, i) => (
                        <span key={i} className="vp-tag">{tag}</span>
                    ))}
                </div>
            )}

            <div className="vp-actions">
                <button
                    className={`vp-action-btn ${copied ? 'success' : ''}`}
                    onClick={handleCopy}
                >
                    <FaCopy /> {copied ? 'Copied!' : 'Copy Prompt'}
                </button>
                <button
                    className={`vp-action-btn primary ${(isGenerating || imageLoading) ? 'disabled' : ''}`}
                    onClick={() => handleGenerate(false)}
                    disabled={isGenerating || imageLoading}
                >
                    {(isGenerating || imageLoading) ? <><div className="spinner" style={{ width: 12, height: 12, borderWidth: 2 }}></div> Processing...</> : <><FaRocket /> Generate Image</>}
                </button>
            </div>

            {history.length > 0 && (
                <div className="vp-history">
                    {history.map((item, idx) => (
                        <div
                            key={item.timestamp}
                            className={`vp-history-item ${generatedImage === item.url ? 'active' : ''}`}
                            onClick={() => restoreFromHistory(item)}
                            title={`Seed: ${item.seed} | Model: ${item.model}\nPrompt: ${item.prompt}`}
                        >
                            <img src={item.url} alt={`History ${idx}`} />
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default VisualPromptRenderer;
