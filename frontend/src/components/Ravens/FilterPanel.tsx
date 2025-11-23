// frontend/src/components/Ravens/FilterPanel.tsx
import React from 'react';

interface FilterPanelProps {
    filters: {
        paper: string;
        subject: string;
        importance: number;
        bookmarked: boolean;
        search: string;
    };
    onFilterChange: (key: string, value: any) => void;
}

const FilterPanel: React.FC<FilterPanelProps> = ({ filters, onFilterChange }) => {
    const papers = ['All', 'GS1', 'GS2', 'GS3', 'GS4', 'Essay', 'Optional'];
    const subjects = [
        'All',
        'Polity & Governance',
        'Economics',
        'International Relations',
        'Environment & Ecology',
        'Science & Technology',
        'Internal Security',
        'Disaster Management',
        'Social Issues',
        'History & Culture',
        'Geography',
        'Ethics'
    ];

    return (
        <div className="filter-panel">
            <div className="filter-section">
                <label>🔍 Search</label>
                <input
                    type="text"
                    placeholder="Search articles..."
                    value={filters.search}
                    onChange={(e) => onFilterChange('search', e.target.value)}
                    className="search-input"
                />
            </div>

            <div className="filter-section">
                <label>📄 Mains Paper</label>
                <select
                    value={filters.paper}
                    onChange={(e) => onFilterChange('paper', e.target.value)}
                    className="filter-select"
                >
                    {papers.map(paper => (
                        <option key={paper} value={paper === 'All' ? '' : paper}>
                            {paper}
                        </option>
                    ))}
                </select>
            </div>

            <div className="filter-section">
                <label>📚 Subject</label>
                <select
                    value={filters.subject}
                    onChange={(e) => onFilterChange('subject', e.target.value)}
                    className="filter-select"
                >
                    {subjects.map(subject => (
                        <option key={subject} value={subject === 'All' ? '' : subject}>
                            {subject}
                        </option>
                    ))}
                </select>
            </div>

            <div className="filter-section">
                <label>⭐ Importance</label>
                <select
                    value={filters.importance}
                    onChange={(e) => onFilterChange('importance', Number(e.target.value))}
                    className="filter-select"
                >
                    <option value={0}>All</option>
                    <option value={1}>⭐ Low</option>
                    <option value={2}>⭐⭐ Medium</option>
                    <option value={3}>⭐⭐⭐ High</option>
                </select>
            </div>

            <div className="filter-section">
                <label className="checkbox-label">
                    <input
                        type="checkbox"
                        checked={filters.bookmarked}
                        onChange={(e) => onFilterChange('bookmarked', e.target.checked)}
                    />
                    📌 Bookmarked Only
                </label>
            </div>
        </div>
    );
};

export default FilterPanel;
