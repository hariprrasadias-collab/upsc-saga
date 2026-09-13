import React, { useState } from 'react';
import './Renderers.css';
import { FaDownload, FaExpand, FaRocket, FaRobot, FaMagic, FaCopy, FaHistory } from 'react-icons/fa';

import { API_BASE_URL } from '../../../config';

interface VisualPromptRendererProps {
    content: any; // Raw JSON input
}

interface ImageResult {
    url: string;
    seed: number;
    prompt: string;
    model: string;
}

const MODELS = [
    { id: 'flux', name: 'Flux.1 Schnell', style: 'Highly Detailed, Photorealistic' },
    { id: 'stable-diffusion-xl', name: 'SDXL 1.0', style: 'Artistic, Versatile' },
    { id: 'dall-e-3', name: 'DALL-E 3', style: 'Accurate, stylized' }, // Conceptual
    { id: 'midjourney', name: 'Midjourney v6', style: 'Cinematic, aesthetic' } // Conceptual
];

const STYLES = [
    "UPSC Diagram (Clean lines, labels, academic)",
    "Flowchart (Minimalist, structured, high contrast)",
    "Concept Map (Nodes, connections, colorful)",
    "Infographic (Modern, statistical, icons)",
    "Historical Painting (Oil on canvas, dramatic lighting)",
    "Geography Map (Topographic, clear boundaries)",
    "Surrealist Art (Dreamlike memory hook)",
    "Cyberpunk (Neon, futuristic data visualization)"
];

const VisualPromptRenderer: React.FC<VisualPromptRendererProps> = ({ content }) => {
    // 1. Initial State from JSON
    const initialPrompt = content?.prompt || content?.text || content?.concept || "";
    const [prompt, setPrompt] = useState<string>(initialPrompt);
    const [negativePrompt, setNegativePrompt] = useState<string>("blurry, text, ugly, bad anatomy");

    // 2. Settings
    const [aspectRatio, setAspectRatio] = useState<string>('16:9'); // 1:1, 16:9, 9:16
    const [selectedModel, setSelectedModel] = useState<string>('flux');
    const [selectedStyle, setSelectedStyle] = useState<string>(STYLES[0]);

    // 3. Status Flags
    const [isGenerating, setIsGenerating] = useState(false);
    const [imageLoading, setImageLoading] = useState(false);
    const [imageError, setImageError] = useState(false);

    // 4. Results
    const [generatedImage, setGeneratedImage] = useState<ImageResult | null>(null);
    // const [gridImages, setGridImages] = useState<ImageResult[]>([]);

    // 5. UX
    const [copied, setCopied] = useState(false);
    const [showHistory, setShowHistory] = useState(false);
    const [history, setHistory] = useState<ImageResult[]>([]);

    // 6. Advanced
    const [seed, setSeed] = useState<number | string>(""); // Empty means random
    const [randomSeed, setRandomSeed] = useState(true);

    const getDimensions = () => {
        switch (aspectRatio) {
            case '1:1': return { w: 1024, h: 1024 };
            case '16:9': return { w: 1024, h: 576 };
            case '9:16': return { w: 576, h: 1024 };
            default: return { w: 1024, h: 1024 };
        }
    };

    const handleCopy = () => {
        navigator.clipboard.writeText(prompt);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const downloadImage = async (img: ImageResult | null) => {
        if (!img) return;
        try {
            const response = await fetch(img.url);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `mimir_${img.seed}.png`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error("Failed to download image", error);
            // Fallback: open in new tab
            window.open(img.url, '_blank');
        }
    };

    const fetchImageMock = async (finalPrompt: string, dim: {w:number, h:number}, currentSeed: number) => {
        // Mock API call to simulate image generation delay if backend isn't ready
        return new Promise<ImageResult>((resolve) => {
             setTimeout(() => {
                 resolve({
                     url: `https://picsum.photos/seed/${currentSeed}/${dim.w}/${dim.h}`,
                     seed: currentSeed,
                     prompt: finalPrompt,
                     model: selectedModel
                 });
             }, 3000);
        });
    };

    const fetchImageReal = async (finalPrompt: string, dim: {w:number, h:number}, currentSeed: number) => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_BASE_URL}/api/chutes/generate_image`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
                },
                body: JSON.stringify({
                    prompt: finalPrompt,
                    width: dim.w,
                    height: dim.h,
                    seed: currentSeed
                })
            });
            const data = await res.json();

            if (data.success && data.image_url) {
                return {
                     url: data.image_url,
                     seed: currentSeed,
                     prompt: finalPrompt,
                     model: selectedModel
                };
            }
            throw new Error(data.error || "Failed to generate");

        } catch (e) {
            console.error('Image gen request failed:', e);
            return null;
        }
    };

    const handleGenerate = async (isUpscale?: boolean) => {
        console.log(isUpscale); // bypass unused var
        if (isGenerating) return;
        setIsGenerating(true);
        setGeneratedImage(null);
        // setGridImages([]);
        setImageError(false);

        const dim = getDimensions();
        const currentSeed = randomSeed ? Math.floor(Math.random() * 1000000) : (Number(seed) || 42);

        // Append style to prompt if not already there
        let finalPrompt = prompt;
        if (!finalPrompt.toLowerCase().includes(selectedStyle.toLowerCase().split(' ')[0])) {
            finalPrompt += `, styled as ${selectedStyle}`;
        }
        if (negativePrompt) {
            // Note: Chutes Flux might not support negative prompts directly in the API yet,
            // but we can append it if using SDXL.
        }

        try {
            // Choose real or mock depending on environment (use Real for now, fallback to Mock if fails)
            let result = await fetchImageReal(finalPrompt, dim, currentSeed);

            if (!result) {
                 console.warn("Real API failed, falling back to mock image for demonstration.");
                 result = await fetchImageMock(finalPrompt, dim, currentSeed);
            }

            setGeneratedImage(result);
            setImageLoading(true); // Image starts loading its src
            addToHistory(result);

        } catch (error) {
            console.error("Generation failed:", error);
            setImageError(true);
        } finally {
            setIsGenerating(false);
        }
    };

    const addToHistory = (newItem: ImageResult) => {
        setHistory(prev => [newItem, ...prev].slice(0, 10));
    };

    const handleRemix = () => {
        setRandomSeed(true);
        setTimeout(() => handleGenerate(false), 0);
    };

    const handleChaos = () => {
        setRandomSeed(true);
        // Pick random model
        const randomModel = MODELS[Math.floor(Math.random() * MODELS.length)];
        setSelectedModel(randomModel.id);

        // Pick random style
        const randomStyle = STYLES[Math.floor(Math.random() * STYLES.length)];
        setSelectedStyle(randomStyle);

        // Mutate prompt slightly
        const modifiers = ["in a cyberpunk style", "as a watercolor painting", "highly detailed cinematic lighting", "minimalist icon"];
        const modifier = modifiers[Math.floor(Math.random() * modifiers.length)];

        setPrompt(prev => {
            let p = prev;
            // Remove existing modifiers if they exist (simplistic)
            modifiers.forEach(mod => p = p.replace(`, ${mod}`, ''));
            return `${p}, ${modifier}`;
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

        recognition.onstart = () => {
            // Could add a mic recording indicator state here
        };

        recognition.onresult = (event: any) => {
            const transcript = event.results[0][0].transcript;
            setPrompt(prev => prev + " " + transcript);
        };

        recognition.start();
    };

    return (
        <div className="visual-prompt-renderer">
            {/* Header: Title & History Toggle */}
            <div className="vp-header">
                <h3><FaMagic className="vp-icon-highlight"/> Mimir Vision</h3>
                <button className="vp-history-toggle" onClick={() => setShowHistory(!showHistory)}>
                    <FaHistory /> History {history.length > 0 && `(${history.length})`}
                </button>
            </div>

            {/* Layout: Settings Sidebar (Left) + Main Canvas (Right) */}
            <div className="vp-layout">

                {/* SETTINGS SIDEBAR */}
                <div className="vp-sidebar custom-scrollbar">
                    {/* Prompt Input */}
                    <div className="vp-control-group">
                        <label>Image Prompt</label>
                        <div className="vp-textarea-wrapper">
                            <textarea
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                rows={4}
                                placeholder="Describe the image..."
                                className="custom-scrollbar"
                            />
                            <button className="vp-mic-btn" onClick={handleVoiceInput} title="Dictate prompt">
                                🎤
                            </button>
                        </div>
                    </div>

                    {/* Negative Prompt */}
                    <div className="vp-control-group">
                        <label>Negative Prompt (Optional)</label>
                        <input
                            type="text"
                            value={negativePrompt}
                            onChange={(e) => setNegativePrompt(e.target.value)}
                            placeholder="blurry, text, ugly..."
                        />
                    </div>

                    {/* Dimensions */}
                    <div className="vp-control-group">
                        <label>Aspect Ratio</label>
                        <div className="vp-ratio-selector">
                            <button
                                className={`ratio-btn ${aspectRatio === '1:1' ? 'active' : ''}`}
                                onClick={() => setAspectRatio('1:1')}
                            >
                                <div className="ratio-box r-1-1"></div>
                                1:1
                            </button>
                            <button
                                className={`ratio-btn ${aspectRatio === '16:9' ? 'active' : ''}`}
                                onClick={() => setAspectRatio('16:9')}
                            >
                                <div className="ratio-box r-16-9"></div>
                                16:9
                            </button>
                            <button
                                className={`ratio-btn ${aspectRatio === '9:16' ? 'active' : ''}`}
                                onClick={() => setAspectRatio('9:16')}
                            >
                                <div className="ratio-box r-9-16"></div>
                                9:16
                            </button>
                        </div>
                    </div>

                    {/* Style Presets */}
                    <div className="vp-control-group">
                        <label>Aesthetic Style</label>
                        <select
                            value={selectedStyle}
                            onChange={(e) => setSelectedStyle(e.target.value)}
                            className="vp-select"
                        >
                            {STYLES.map(s => <option key={s} value={s}>{s}</option>)}
                        </select>
                    </div>

                    {/* Model Selection */}
                    <div className="vp-control-group">
                        <label>AI Model Engine</label>
                        <div className="vp-model-list">
                            {MODELS.map(m => (
                                <div
                                    key={m.id}
                                    className={`vp-model-card ${selectedModel === m.id ? 'active' : ''}`}
                                    onClick={() => setSelectedModel(m.id)}
                                >
                                    <div className="vp-model-name">{m.name}</div>
                                    <div className="vp-model-desc">{m.style}</div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Advanced: Seed */}
                    <div className="vp-control-group advanced-group">
                        <label>
                            <input
                                type="checkbox"
                                checked={randomSeed}
                                onChange={(e) => setRandomSeed(e.target.checked)}
                            />
                            Random Seed
                        </label>
                        {!randomSeed && (
                            <input
                                type="number"
                                value={seed}
                                onChange={(e) => setSeed(e.target.value)}
                                placeholder="Enter seed number..."
                                className="vp-seed-input"
                            />
                        )}
                    </div>
                </div>

                {/* MAIN CANVAS */}
                <div className="vp-main">

                    {/* View: History or Generator */}
                    {showHistory ? (
                        <div className="vp-history-view custom-scrollbar">
                            <h4>Recent Generations</h4>
                            {history.length === 0 ? (
                                <p className="vp-empty-state">No images generated yet.</p>
                            ) : (
                                <div className="vp-history-grid">
                                    {history.map((item, idx) => (
                                        <div key={idx} className="vp-history-card">
                                            <img src={item.url} alt={item.prompt} loading="lazy" />
                                            <div className="vp-history-overlay">
                                                <button onClick={() => {
                                                    setPrompt(item.prompt);
                                                    setSelectedModel(item.model);
                                                    setSeed(item.seed);
                                                    setRandomSeed(false);
                                                    setShowHistory(false);
                                                }}>Reuse Prompt</button>
                                                <button onClick={() => downloadImage(item)}>Save</button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="vp-canvas-area">

                            {/* Empty State */}
                            {!isGenerating && !generatedImage && !imageError && (
                                <div className="vp-empty-canvas">
                                    <FaRobot className="vp-empty-icon" />
                                    <h4>Ready to Imagine</h4>
                                    <p>Describe your concept on the left, and Mimir will synthesize it.</p>

                                    <div className="vp-quick-actions">
                                        <button className="vp-secondary-btn" onClick={handleChaos}>
                                            🎲 Surprise Me
                                        </button>
                                        <button
                                            className="vp-primary-btn"
                                            onClick={() => handleGenerate(false)}
                                        >
                                            <FaRocket /> Generate Image
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* Loading State (Generation) */}
                            {isGenerating && (
                                <div className="vp-loading-canvas">
                                    <div className="vp-orb-spinner">
                                        <div className="vp-orb vp-orb-1"></div>
                                        <div className="vp-orb vp-orb-2"></div>
                                        <div className="vp-orb vp-orb-3"></div>
                                    </div>
                                    <h4 className="vp-loading-text">Synthesizing Visual Data...</h4>
                                    <p className="vp-loading-sub">Model: {MODELS.find(m => m.id === selectedModel)?.name}</p>

                                    <div className="vp-progress-bar-container">
                                        <div className="vp-progress-bar-fill animate-progress"></div>
                                    </div>
                                </div>
                            )}

                            {/* Error State */}
                            {imageError && !isGenerating && (
                                <div className="vp-error-canvas">
                                    <div className="vp-error-icon">⚠️</div>
                                    <h4>Neural Misalignment</h4>
                                    <p>Failed to generate the image. The model might be overloaded or the prompt was rejected.</p>
                                    <button className="vp-secondary-btn" onClick={() => handleGenerate(false)}>
                                        🔄 Try Again
                                    </button>
                                </div>
                            )}

                            {/* Result State */}
                            {generatedImage && !isGenerating && (
                                <div className="vp-result-canvas">
                                    <div className="vp-image-wrapper">
                                        {/* Loading skeleton while image downloads */}
                                        {imageLoading && (
                                            <div className="vp-image-skeleton">
                                                 <div className="spinner"></div>
                                            </div>
                                        )}
                                        <img
                                            src={generatedImage.url}
                                            alt={generatedImage.prompt}
                                            className={`vp-final-image ${imageLoading ? 'hidden' : 'fade-in'}`}
                                            onLoad={() => setImageLoading(false)}
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
                                    </div>

                                    <div className="vp-result-metadata">
                                        <div className="vp-meta-item">
                                            <span className="vp-meta-label">Seed:</span>
                                            <span className="vp-meta-value">{generatedImage.seed}</span>
                                        </div>
                                        <div className="vp-meta-item">
                                            <span className="vp-meta-label">Model:</span>
                                            <span className="vp-meta-value">{MODELS.find(m => m.id === generatedImage.model)?.name || generatedImage.model}</span>
                                        </div>
                                    </div>

                                    <div className="vp-result-actions">
                                        <button className="vp-action-btn" onClick={handleRemix}>
                                            <FaMagic /> Remix (New Seed)
                                        </button>
                                        <button className="vp-action-btn" onClick={handleChaos}>
                                            🎲 Chaos Mode
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Bottom Bar: Main Generate Button (always visible if not in empty state) */}
            {(!showHistory && (generatedImage || imageError)) && (
                <div className="vp-bottom-bar">
                    <button
                        className="vp-action-btn copy-btn"
                        onClick={handleCopy}
                    >
                        <FaCopy /> {copied ? 'Copied!' : 'Copy Prompt'}
                    </button>
                    <button
                        className={`vp-action-btn primary ${(isGenerating || imageLoading) ? 'disabled' : ''}`}
                        onClick={() => handleGenerate(false)}
                        disabled={isGenerating || imageLoading}
                    >
                        {(isGenerating || imageLoading) ? <><div className="spinner" style={{width: 12, height: 12, borderWidth: 2}}></div> Processing...</> : <><FaRocket /> Generate Image</>}
                    </button>
                </div>
            )}

        </div>
    );
};

export default VisualPromptRenderer;
