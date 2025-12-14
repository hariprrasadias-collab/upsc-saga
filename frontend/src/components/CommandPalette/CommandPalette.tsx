import React, { useState, useEffect, useRef } from 'react';
import './CommandPalette.css';

import { usePomodoro } from '../../contexts/PomodoroContext';
import { useGlobal } from '../../contexts/GlobalContext';

interface CommandOption {
    id: string;
    label: string;
    action: () => void;
    category: 'Navigation' | 'Action' | 'Tool';
    shortcut?: string;
}

const CommandPalette: React.FC = () => {
    const { setCurrentTab, toggleRageMode } = useGlobal();
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState('');
    const [selectedIndex, setSelectedIndex] = useState(0);
    const inputRef = useRef<HTMLInputElement>(null);

    const { toggleTimer, isRunning } = usePomodoro();

    // Define available commands
    const commands: CommandOption[] = [
        // Navigation
        { id: 'nav-dashboard', label: 'Go to Dashboard', category: 'Navigation', action: () => setCurrentTab('dashboard') },
        { id: 'nav-warmap', label: 'Go to War Map', category: 'Navigation', action: () => setCurrentTab('war-map') },
        { id: 'nav-syllabus', label: 'Go to Syllabus Tracker', category: 'Navigation', action: () => setCurrentTab('syllabus') },
        { id: 'nav-quests', label: 'Go to Quests', category: 'Navigation', action: () => setCurrentTab('quests') },
        { id: 'nav-codex', label: 'Go to Codex (Yggdrasil)', category: 'Navigation', action: () => setCurrentTab('codex') },
        { id: 'nav-lore', label: 'Go to Lore Tablets', category: 'Navigation', action: () => setCurrentTab('lore-tablets') },
        { id: 'nav-pyq', label: 'Go to PYQ Database', category: 'Navigation', action: () => setCurrentTab('pyq') },
        { id: 'nav-armory', label: 'Go to Armory', category: 'Navigation', action: () => setCurrentTab('armory') },
        { id: 'nav-dojo', label: 'Go to Anki Dojo', category: 'Navigation', action: () => setCurrentTab('dojo') },
        { id: 'nav-seer', label: 'Go to Seer (News)', category: 'Navigation', action: () => setCurrentTab('seer') },
        { id: 'nav-ravens', label: 'Go to Ravens (AI News)', category: 'Navigation', action: () => setCurrentTab('ravens') },
        { id: 'nav-answer', label: 'Go to Answer Writing', category: 'Navigation', action: () => setCurrentTab('answer-writing') },
        { id: 'nav-mock', label: 'Go to Mock Tests', category: 'Navigation', action: () => setCurrentTab('mock-tests') },
        { id: 'nav-essay', label: 'Go to Essay Workshop', category: 'Navigation', action: () => setCurrentTab('essay') },
        { id: 'nav-csat', label: 'Go to CSAT Module', category: 'Navigation', action: () => setCurrentTab('csat') },
        { id: 'nav-mimir', label: 'Go to Mimir Chat', category: 'Navigation', action: () => setCurrentTab('mimir') },
        { id: 'nav-flashcards', label: 'Go to Flashcards', category: 'Navigation', action: () => setCurrentTab('flashcards') },
        { id: 'nav-analytics', label: 'Go to Analytics', category: 'Navigation', action: () => setCurrentTab('analytics') },
        { id: 'nav-weak', label: 'Go to Weak Areas', category: 'Navigation', action: () => setCurrentTab('weak-areas') },
        { id: 'nav-admin', label: 'Go to Admin Dashboard', category: 'Navigation', action: () => setCurrentTab('admin') },
        { id: 'nav-scribe', label: 'Go to Scribe (Workbench)', category: 'Navigation', action: () => setCurrentTab('scribe') },
        { id: 'nav-arena', label: 'Go to Boss Arena', category: 'Navigation', action: () => setCurrentTab('arena') },

        // Tools
        {
            id: 'tool-pomodoro',
            label: isRunning ? 'Pause Pomodoro Timer' : 'Start Pomodoro Timer',
            category: 'Tool',
            action: () => toggleTimer()
        },
        {
            id: 'tool-rage',
            label: 'Toggle Spartan Rage',
            category: 'Tool',
            action: () => toggleRageMode()
        },
    ];

    const filteredCommands = commands.filter(cmd =>
        cmd.label.toLowerCase().includes(query.toLowerCase())
    );

    // Handle Keyboard Shortcuts
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                setIsOpen(prev => !prev);
            }

            if (isOpen) {
                if (e.key === 'Escape') {
                    setIsOpen(false);
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    setSelectedIndex(prev => (prev + 1) % filteredCommands.length);
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    setSelectedIndex(prev => (prev - 1 + filteredCommands.length) % filteredCommands.length);
                } else if (e.key === 'Enter') {
                    e.preventDefault();
                    if (filteredCommands[selectedIndex]) {
                        filteredCommands[selectedIndex].action();
                        setIsOpen(false);
                    }
                }
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, filteredCommands, selectedIndex]);

    // Focus input when opened
    useEffect(() => {
        if (isOpen && inputRef.current) {
            setTimeout(() => inputRef.current?.focus(), 50);
            setQuery('');
            setSelectedIndex(0);
        }
    }, [isOpen]);

    if (!isOpen) return null;

    const activeDescendantId = filteredCommands[selectedIndex]?.id;

    return (
        <div
            className="command-palette-overlay"
            onClick={() => setIsOpen(false)}
        >
            <div
                className="command-palette-modal"
                onClick={e => e.stopPropagation()}
                role="dialog"
                aria-modal="true"
                aria-label="Command Palette"
            >
                <div className="command-palette-search">
                    <span className="search-icon" aria-hidden="true">🔍</span>
                    <input
                        ref={inputRef}
                        type="text"
                        placeholder="Type a command or search..."
                        value={query}
                        onChange={e => {
                            setQuery(e.target.value);
                            setSelectedIndex(0);
                        }}
                        aria-label="Search commands"
                        role="combobox"
                        aria-expanded="true"
                        aria-controls="command-results-list"
                        aria-activedescendant={activeDescendantId}
                        aria-autocomplete="list"
                    />
                    <span className="esc-hint" aria-hidden="true">ESC</span>
                </div>

                <div
                    className="command-palette-results"
                    id="command-results-list"
                    role="listbox"
                >
                    {filteredCommands.length > 0 ? (
                        filteredCommands.map((cmd, index) => (
                            <div
                                key={cmd.id}
                                id={cmd.id}
                                className={`command-item ${index === selectedIndex ? 'selected' : ''}`}
                                onClick={() => {
                                    cmd.action();
                                    setIsOpen(false);
                                }}
                                onMouseEnter={() => setSelectedIndex(index)}
                                role="option"
                                aria-selected={index === selectedIndex}
                            >
                                <div className="command-content">
                                    <span className="command-label">{cmd.label}</span>
                                    <span className="command-category">{cmd.category}</span>
                                </div>
                                {cmd.shortcut && <span className="command-shortcut">{cmd.shortcut}</span>}
                            </div>
                        ))
                    ) : (
                        <div className="no-results" role="alert">No commands found</div>
                    )}
                </div>

                <div className="command-palette-footer" aria-hidden="true">
                    <span>Use <b>↑↓</b> to navigate</span>
                    <span><b>↵</b> to select</span>
                </div>
            </div>
        </div>
    );
};

export default CommandPalette;
