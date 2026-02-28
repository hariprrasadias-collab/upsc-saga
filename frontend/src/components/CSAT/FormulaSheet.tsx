import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';

interface FormulaSection {
    title: string;
    content: string[];
}

const FormulaSheet: React.FC = () => {
    const [formulas, setFormulas] = useState<Record<string, FormulaSection[]>>({});
    const [expandedSection, setExpandedSection] = useState<string | null>(null);

    useEffect(() => {
        fetchFormulas();
    }, []);

    const fetchFormulas = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/csat/formulas`);
            const data = await response.json();
            setFormulas(data);
        } catch (error) {
            console.error('Error fetching formulas:', error);
        }
    };

    const toggleSection = (title: string) => {
        setExpandedSection(expandedSection === title ? null : title);
    };

    return (
        <div className="formula-sheet">
            {Object.entries(formulas).map(([category, sections]) => (
                <div key={category} className="formula-category">
                    <h2>{category}</h2>
                    <div className="formula-grid">
                        {sections.map((section) => (
                            <div key={section.title} className="formula-card">
                                <div
                                    className="formula-header"
                                    onClick={() => toggleSection(section.title)}
                                >
                                    <h3>{section.title}</h3>
                                    <span className="toggle-icon">
                                        {expandedSection === section.title ? '−' : '+'}
                                    </span>
                                </div>

                                {expandedSection === section.title && (
                                    <div className="formula-content">
                                        <ul>
                                            {section.content.map((item, idx) => (
                                                <li key={idx}>{item}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default FormulaSheet;
