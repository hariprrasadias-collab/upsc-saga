import React from 'react';
import D3Tree from '../../MindMap/D3Tree';

interface Props {
    content: string;
}

const MindMapRenderer: React.FC<Props> = ({ content }) => {
    let data;
    try {
        data = JSON.parse(content);
    } catch {
        return <div className="error-text">Failed to parse Mind Map data.</div>;
    }

    return (
        <div className="mindmap-renderer-container" style={{ height: '500px', width: '100%', border: '1px solid rgba(0,255,242,0.2)', borderRadius: '8px' }}>
            <D3Tree data={data} />
        </div>
    );
};

export default MindMapRenderer;
