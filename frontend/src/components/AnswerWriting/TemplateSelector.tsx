import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';
import './TemplateSelector.css';

interface Template {
    id: string;
    name: string;
    description: string;
    structure: string[];
    wordCount: number;
    tips: string[];
    example: string;
}

interface TemplateSelectorProps {
    onSelectTemplate: (template: Template) => void;
}

const TemplateSelector: React.FC<TemplateSelectorProps> = ({ onSelectTemplate }) => {
    const [templates, setTemplates] = useState<Template[]>([]);
    const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
    const [isOpen, setIsOpen] = useState(false);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchTemplates();
    }, []);

    const fetchTemplates = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/templates/list`);
            const data = await response.json();
            if (data.success) {
                setTemplates(data.templates);
            }
        } catch (error) {
            console.error('Error fetching templates:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSelectTemplate = (template: Template) => {
        setSelectedTemplate(template);
    };

    const handleUseTemplate = () => {
        if (selectedTemplate) {
            onSelectTemplate(selectedTemplate);
            setIsOpen(false);
        }
    };

    return (
        <div className="template-selector">
            <button
                className="template-trigger-btn"
                onClick={() => setIsOpen(!isOpen)}
            >
                📝 Use Answer Template
            </button>

            {isOpen && (
                <div className="template-modal-overlay" onClick={() => setIsOpen(false)}>
                    <div className="template-modal" onClick={(e) => e.stopPropagation()}>
                        <div className="template-modal-header">
                            <h2>Answer Templates</h2>
                            <button className="close-btn" onClick={() => setIsOpen(false)} aria-label="Close">✕</button>
                        </div>

                        <div className="template-modal-body">
                            {loading ? (
                                <div className="loading">Loading templates...</div>
                            ) : (
                                <div className="template-content">
                                    {/* Template List */}
                                    <div className="template-list">
                                        <h3>Question Types</h3>
                                        {templates.map((template) => (
                                            <div
                                                key={template.id}
                                                className={`template-item ${selectedTemplate?.id === template.id ? 'active' : ''}`}
                                                onClick={() => handleSelectTemplate(template)}
                                            >
                                                <div className="template-name">{template.name}</div>
                                                <div className="template-desc">{template.description}</div>
                                            </div>
                                        ))}
                                    </div>

                                    {/* Template Preview */}
                                    {selectedTemplate && (
                                        <div className="template-preview">
                                            <h3>{selectedTemplate.name}</h3>
                                            <p className="preview-desc">{selectedTemplate.description}</p>

                                            <div className="preview-meta">
                                                <span className="word-count">📊 Target: {selectedTemplate.wordCount} words</span>
                                            </div>

                                            <div className="preview-section">
                                                <h4>Structure</h4>
                                                <ul className="structure-list">
                                                    {selectedTemplate.structure.map((item, idx) => (
                                                        <li key={idx}>{item}</li>
                                                    ))}
                                                </ul>
                                            </div>

                                            <div className="preview-section">
                                                <h4>Tips</h4>
                                                <ul className="tips-list">
                                                    {selectedTemplate.tips.map((tip, idx) => (
                                                        <li key={idx}>💡 {tip}</li>
                                                    ))}
                                                </ul>
                                            </div>

                                            <div className="preview-section">
                                                <h4>Example Structure</h4>
                                                <pre className="example-text">{selectedTemplate.example}</pre>
                                            </div>

                                            <button className="use-template-btn" onClick={handleUseTemplate}>
                                                Use This Template
                                            </button>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TemplateSelector;
