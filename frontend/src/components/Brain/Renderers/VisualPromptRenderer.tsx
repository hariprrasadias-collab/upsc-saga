import React, { useState } from 'react';
import './Renderers.css';

interface VisualPromptRendererProps {
    content: string; // The raw prompt text
}

const VisualPromptRenderer: React.FC<VisualPromptRendererProps> = ({ content }) => {
    const [copied, setCopied] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [generationLogs, setGenerationLogs] = useState<string[]>([]);
    const [generatedImage, setGeneratedImage] = useState<string | null>(null);
    const [imageLoading, setImageLoading] = useState(false);
    const [imageError, setImageError] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const handleGenerate = () => {
        if (isGenerating) return;
        setIsGenerating(true);
        setGeneratedImage(null);
        setImageError(false);
        setGenerationLogs(["Initializing Neural Network..."]);

        // Simulated Generation Sequence
        const sequence = [
            { text: "Loading LoRA adapters...", delay: 800 },
            { text: "Tokenizing prompt...", delay: 1500 },
            { text: "Denoising step 1/20...", delay: 2200 },
            { text: "Denoising step 10/20...", delay: 3500 },
            { text: "Denoising step 18/20...", delay: 4500 },
            { text: "Upscaling result...", delay: 5200 },
            { text: "Success. Downloading stream...", delay: 6000 }
        ];

        sequence.forEach(({ text, delay }) => {
            setTimeout(() => {
                setGenerationLogs(prev => [...prev, text]);
            }, delay);
        });

        setTimeout(() => {
            // Use Pollinations.ai for REAL AI generation
            // Safely limit prompt length and encode
            const encodedPrompt = encodeURIComponent(content.slice(0, 600));
            const seed = Math.floor(Math.random() * 10000);
            // 'flux' is a good general model on pollinations, 'midjourney' also an option sometimes
            const url = `https://image.pollinations.ai/prompt/${encodedPrompt}?nologo=true&seed=${seed}&width=800&height=450&model=flux`;

            setGeneratedImage(url);
            setImageLoading(true);
            setIsGenerating(false);
        }, 6000);
    };

    // Extract tags roughly
    const extractTags = (text: string) => {
        const parts = text.split(',').map(s => s.trim());
        const tags = parts.filter(p => p.length < 20 && (p.includes('style') || p.includes('lighting') || p.includes('render') || p.startsWith('--')));
        return tags;
    };

    const tags = extractTags(content);
    const mainPrompt = content;

    return (
        <div className="visual-prompt-container glass-card">
            <div className="vp-header">
                <span className="vp-icon">🎨</span>
                <span className="vp-title">Generative Art Terminal</span>
                <div className="vp-status">{isGenerating || imageLoading ? 'PROCESSING' : 'READY'}</div>
            </div>

            <div className="vp-terminal">
                <div className="vp-command-line">
                    <span className="cmd-prompt">/imagine prompt:</span>
                    <span className="cmd-text">{mainPrompt}</span>
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
                <div className="vp-result fade-in">

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
                        <div className="error-message">
                            ⚠️ Image generation failed. The prompt might be too complex for the external grid.
                        </div>
                    )}

                    {!imageLoading && !imageError && generatedImage && (
                        <div className="vp-overlay">
                            <button className="download-img-btn" onClick={() => window.open(generatedImage, '_blank')}>
                                ⬇ Save High Res
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
                    {copied ? '✅ Copied!' : '📋 Copy Prompt'}
                </button>
                <button
                    className={`vp-action-btn primary ${(isGenerating || imageLoading) ? 'disabled' : ''}`}
                    onClick={handleGenerate}
                    disabled={isGenerating || imageLoading}
                >
                    {(isGenerating || imageLoading) ? '⏳ Dreamify-ing...' : '🚀 Generate Image'}
                </button>
            </div>
        </div>
    );
};

export default VisualPromptRenderer;
