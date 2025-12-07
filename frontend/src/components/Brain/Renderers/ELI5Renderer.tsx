import React from 'react';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';

interface Props {
    content: string;
}

const ELI5Renderer: React.FC<Props> = ({ content }) => {
    return (
        <div className="eli5-container" style={{ fontFamily: '"Comic Sans MS", "Chalkboard SE", sans-serif', padding: '20px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '15px' }}>
            <h3 style={{ color: '#facc15', marginTop: 0 }}>👶 Explain Like I'm 5</h3>
            <div style={{ fontSize: '1.1em', lineHeight: '1.6' }}>
                <MarkdownRenderer content={content} />
            </div>
        </div>
    );
};

export default ELI5Renderer;
