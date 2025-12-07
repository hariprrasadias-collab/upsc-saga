import React, { useState } from 'react';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';

interface Props {
    content: string;
}

const CheatSheetRenderer: React.FC<Props> = ({ content }) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const handlePrint = () => {
        const printWindow = window.open('', '_blank');
        if (printWindow) {
            printWindow.document.write(`
                <html>
                <head>
                    <title>Cheat Sheet - Print View</title>
                    <style>
                        body { font-family: sans-serif; padding: 20px; line-height: 1.5; color: #000; }
                        h1, h2, h3 { color: #333; border-bottom: 2px solid #ccc; padding-bottom: 5px; }
                        code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-family: monospace; }
                        pre { background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
                        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
                        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                        th { background: #eee; }
                    </style>
                </head>
                <body>
                    <h1>Quick Reference Cheat Sheet</h1>
                    <div id="content">Loading content...</div>
                </body>
                </html>
            `);

            // We need to render the markdown to HTML for printing.
            // For simplicity, we'll write the raw text for now or inject a basic converter if we had one.
            // Since MarkdownRenderer is a React component, we can't easily stringify its output here without hydration.
            // A simple fallback is to print raw markdown or use a library.
            // Let's print styled Pre-wrap for now to be safe.
            printWindow.document.getElementById('content')!.innerHTML = `<pre style="white-space: pre-wrap; font-family: sans-serif;">${content}</pre>`;

            printWindow.document.close();
            printWindow.print();
        }
    };

    return (
        <div className="cheat-sheet-container" style={{ border: '1px solid #4ade80', padding: '15px', borderRadius: '8px', background: 'rgba(74, 222, 128, 0.05)', position: 'relative' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(74, 222, 128, 0.3)', paddingBottom: '10px', marginBottom: '15px' }}>
                <h3 style={{ color: '#4ade80', margin: 0 }}>📝 Quick Reference</h3>
                <div style={{ display: 'flex', gap: '10px' }}>
                    <button
                        onClick={handleCopy}
                        style={{ background: 'transparent', border: '1px solid #4ade80', color: '#4ade80', borderRadius: '4px', cursor: 'pointer', padding: '5px 10px' }}
                    >
                        {copied ? '✓ Copied' : '📋 Copy All'}
                    </button>
                    <button
                        onClick={handlePrint}
                        style={{ background: '#4ade80', border: 'none', color: '#000', borderRadius: '4px', cursor: 'pointer', padding: '5px 10px', fontWeight: 'bold' }}
                    >
                        🖨️ Print
                    </button>
                </div>
            </div>
            <MarkdownRenderer content={content} />
        </div>
    );
};

export default CheatSheetRenderer;
