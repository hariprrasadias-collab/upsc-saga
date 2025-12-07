import React, { useState, useEffect } from 'react';
import './Renderers.css';
import { FaDownload, FaCopy, FaRocket, FaMagic, FaCog, FaChevronDown, FaChevronUp } from 'react-icons/fa';

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

const MAGIC_MODIFIERS = [
    "highly detailed", "8k resolution", "cinematic lighting", "photorealistic",
    "masterpiece", "sharp focus", "intricate details", "unreal engine 5 render",
    "volumetric lighting", "global illumination"
];

const VisualPromptRenderer: React.FC<VisualPromptRendererProps> = ({ content }) => {
    const [prompt, setPrompt] = useState(content);
    const [copied, setCopied] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [generationLogs, setGenerationLogs] = useState<string[]>([]);
    const [generatedImage, setGeneratedImage] = useState<string | null>(null);
    const [imageLoading, setImageLoading] = useState(false);
    const [imageError, setImageError] = useState(false);

    // Advanced Settings
    const [showSettings, setShowSettings] = useState(false);
    const [model, setModel] = useState('flux');
    const [aspectRatio, setAspectRatio] = useState('16:9');
    const [seed, setSeed] = useState<number>(Math.floor(Math.random() * 10000));
    const [randomSeed, setRandomSeed] = useState(true);

    const [history, setHistory] = useState<ImageHistoryItem[]>([]);

    useEffect(() => {
        setPrompt(content);
    }, [content]);

    const handleCopy = () => {
        navigator.clipboard.writeText(prompt);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const handleMagicEnhance = () => {
        // Add 3 random modifiers that aren't already there
        const currentLower = prompt.toLowerCase();
        const availableModifiers = MAGIC_MODIFIERS.filter(m => !currentLower.includes(m.toLowerCase()));

        if (availableModifiers.length === 0) return;

        // Shuffle and take up to 3
        const toAdd = availableModifiers.sort(() => 0.5 - Math.random()).slice(0, 3);
        setPrompt(prev => {
            const separator = prev.trim().endsWith(',') || prev.trim().endsWith('.') ? ' ' : ', ';
            return `${prev.trim()}${separator}${toAdd.join(', ')}`;
        });
    };

    const handleGenerate = () => {
        if (isGenerating) return;
        setIsGenerating(true);
        setGeneratedImage(null);
        setImageError(false);
        setGenerationLogs(["Initializing Neural Network..."]);

        const currentSeed = randomSeed ? Math.floor(Math.random() * 10000) : seed;
        if (randomSeed) setSeed(currentSeed); // Update UI to show used seed

        const selectedRatio = ASPECT_RATIOS.find(r => r.id === aspectRatio) || ASPECT_RATIOS[0];

        // Simulated Generation Sequence
        const sequence = [
            { text: `Loading model checkpoint: ${model}...`, delay: 800 },
            { text: "Tokenizing prompt vectors...", delay: 1500 },
            { text: `Allocating tensor (Seed: ${currentSeed})...`, delay: 2000 },
            { text: "Denoising step 5/25...", delay: 3000 },
            { text: "Denoising step 15/25...", delay: 4200 },
            { text: "Applying aesthetics filter...", delay: 5000 },
            { text: "Success. Decoding latents...", delay: 5800 }
        ];

        sequence.forEach(({ text, delay }) => {
            setTimeout(() => {
                setGenerationLogs(prev => [...prev, text]);
            }, delay);
        });

        setTimeout(() => {
            const encodedPrompt = encodeURIComponent(prompt.slice(0, 1000));
            const url = `https://image.pollinations.ai/prompt/${encodedPrompt}?nologo=true&seed=${currentSeed}&width=${selectedRatio.width}&height=${selectedRatio.height}&model=${model}`;

            setGeneratedImage(url);
            setImageLoading(true);
            setIsGenerating(false);

            // Add to history
            const newItem: ImageHistoryItem = {
                url,
                prompt,
                seed: currentSeed,
                model,
                timestamp: Date.now()
            };
            setHistory(prev => [newItem, ...prev].slice(0, 10)); // Keep last 10

        }, 6000);
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
        setModel(item.model);
        setGeneratedImage(item.url);
        setImageLoading(true); // Will trigger onLoad event
    };

    // Extract tags roughly
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
                <button
                    className={`settings-toggle-btn ${showSettings ? 'active' : ''}`}
                    onClick={() => setShowSettings(!showSettings)}
                >
                    <FaCog /> Advanced Config {showSettings ? <FaChevronUp /> : <FaChevronDown />}
                </button>
            </div>

            {showSettings && (
                <div className="vp-settings-panel">
                    <div className="vp-control-group">
                        <label className="vp-label">Model Architecture</label>
                        <select
                            className="vp-select"
                            value={model}
                            onChange={(e) => setModel(e.target.value)}
                        >
                            {MODELS.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
                        </select>
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
                                🎲
                            </button>
                        </div>
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
                    />
                </div>
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '5px' }}>
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
            {(generatedImage || imageLoading) && (
                <div className="vp-result">

                    {imageLoading && !imageError && (
                        <div className="image-loader">
                            <div className="spinner"></div>
                            <span>Rendering pixel data...</span>
                        </div>
                    )}

                    {generatedImage && !imageError && (
                        <img
                            src={generatedImage}
                            alt="Generated Visualization"
                            className="generated-img"
                            style={{ display: imageLoading ? 'none' : 'block' }}
                            onLoad={() => setImageLoading(false)}
                            onError={() => {
                                setImageLoading(false);
                                setImageError(true);
                            }}
                        />
                    )}

                    {imageError && (
                        <div className="error-message" style={{color: '#f85149', padding: '20px'}}>
                            ⚠️ Image generation failed. The prompt might be too complex for the external grid.
                        </div>
                    )}

                    {!imageLoading && !imageError && generatedImage && (
                        <div className="vp-overlay">
                            <button className="download-img-btn" onClick={() => downloadImage(generatedImage)}>
                                <FaDownload /> Save High Res
                            </button>
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
                    onClick={handleGenerate}
                    disabled={isGenerating || imageLoading}
                >
                    {(isGenerating || imageLoading) ? <><div className="spinner" style={{width: 12, height: 12, borderWidth: 2}}></div> Processing...</> : <><FaRocket /> Generate Image</>}
                </button>
            </div>

            {history.length > 0 && (
                <div className="vp-history">
                    {history.map((item, idx) => (
                        <div
                            key={item.timestamp}
                            className={`vp-history-item ${generatedImage === item.url ? 'active' : ''}`}
                            onClick={() => restoreFromHistory(item)}
                            title={`Seed: ${item.seed} | Model: ${item.model}`}
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
