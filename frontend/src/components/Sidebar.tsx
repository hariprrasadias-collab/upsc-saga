// Sidebar with Expandable Groups
import React, { useState, memo } from 'react';
import { useNavigate } from 'react-router-dom';
import './Sidebar.css';
import { useGlobal } from '../contexts/GlobalContext';

const Sidebar: React.FC = memo(() => {
  const { currentTab, setCurrentTab, isSidebarOpen, toggleSidebar, toggleMimir } = useGlobal();
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    planning: true,
    training: false,
    knowledge: false,
    enhancement: false,
    admin: false
  });

  const navigate = useNavigate();

  const toggleGroup = (group: string) => {
    setExpandedGroups(prev => ({
      ...prev,
      [group]: !prev[group]
    }));
  };

  const handleTabChange = (tabId: string) => {
    if (tabId === 'mimir') {
      toggleMimir(true);
      // On mobile, close sidebar after selection
      if (window.innerWidth <= 768) {
        toggleSidebar();
      }
      return;
    }

    setCurrentTab(tabId);
    navigate('/');
    // On mobile, close sidebar after selection
    if (window.innerWidth <= 768) {
      toggleSidebar();
    }
  };

  const menuGroups = {
    planning: {
      title: '🗺️ Planning',
      items: [
        { id: 'study-plan', label: 'Study Plan', icon: '📅' },
        { id: 'war-map', label: 'War Map', icon: '🗓️' },
        { id: 'triangulation-history', label: 'War Room Archives', icon: '⚔️' },
        { id: 'syllabus', label: 'Syllabus', icon: '🧭' },
        { id: 'quests', label: 'Quests', icon: '📜' },
        { id: 'revision-cards', label: 'Revision Cards', icon: '⚡' },
        { id: 'mnemonics', label: 'Mnemonics', icon: '🧠' },
        { id: 'mindmap', label: 'Mind Map', icon: '🕸️' },
        { id: 'mind-palace', label: 'Mind Palace', icon: '🏰' },
        { id: 'revision-center', label: 'Revision Center', icon: '🔄' },
        { id: 'timebox', label: 'Time Boxing', icon: '⏳' },
        { id: 'golden-path', label: 'The Golden Path', icon: '🌟' }
      ]
    },
    training: {
      title: '💪 Training',
      items: [
        { id: 'dojo', label: 'Anki Dojo', icon: '🥋' },
        { id: 'answer-writing', label: 'Answer Writing', icon: '✍️' },
        { id: 'scribe', label: 'The Scribe (AI)', icon: '📜' },
        { id: 'socratic-history', label: 'Socratic Archives', icon: '🏛️' },
        { id: 'mock-tests', label: 'Mock Tests', icon: '📋' },
        { id: 'arena', label: 'Boss Arena', icon: '⚔️' },
        { id: 'essay', label: 'Essay Workshop', icon: '✍️' },
        { id: 'csat', label: 'CSAT Prep', icon: '🧮' },
        { id: 'foresight', label: 'Project Foresight', icon: '🔮' }
      ]
    },
    knowledge: {
      title: '📚 Knowledge',
      items: [
        { id: 'mimir', label: 'Mimir (AI)', icon: '🧙‍♂️' },
        { id: 'brain-vault', label: 'Brain Vault', icon: '🧠' },
        { id: 'flashcards', label: 'Flashcards', icon: '🎴' },
        { id: 'seer', label: 'The Seer', icon: '🔮' },
        { id: 'ravens', label: 'The Ravens', icon: '🐦' },
        { id: 'compilation', label: 'Monthly Compilation', icon: '📚' },
        { id: 'pyq', label: 'The Archives', icon: '🏛️' },
        { id: 'heatmap', label: 'PYQ Heatmap', icon: '📊' },
        { id: 'model-answers', label: 'Model Answers', icon: '📝' },
        { id: 'codex', label: 'Yggdrasil', icon: '🌳' },
        { id: 'lore-tablets', label: 'Lore Tablets', icon: '📖' },
        { id: 'watchman', label: 'Night Watchman', icon: '🌃' }
      ]
    },
    enhancement: {
      title: '⚡ Enhancement',
      items: [
        { id: 'armory', label: 'Armory', icon: '🛡️' },
        { id: 'panopticon', label: 'The Panopticon', icon: '👁️' },
        { id: 'neural-hash', label: 'The Neural Hash', icon: '🧬' }
      ]
    },
    admin: {
      title: '🛡️ Admin',
      items: [
        { id: 'admin', label: 'Control Panel', icon: '⚙️' }
      ]
    }
  };

  return (
    <div className={`sidebar ${isSidebarOpen ? 'open' : 'closed'}`}>
      <div className="sidebar-header">
        <h2>UPSC SAGA</h2>
        {/* Mobile Close Button */}
        <button
          className="mobile-close-btn"
          onClick={toggleSidebar}
          aria-label="Close sidebar"
          type="button"
        >
          ×
        </button>
      </div>

      {/* Dashboard - Always Top */}
      <button
        type="button"
        className={`menu-item ${currentTab === 'dashboard' ? 'active' : ''}`}
        onClick={() => handleTabChange('dashboard')}
        aria-current={currentTab === 'dashboard' ? 'page' : undefined}
      >
        <span className="icon" aria-hidden="true">🏠</span>
        <span className="label">Dashboard</span>
      </button>

      {/* Analytics - Standalone */}
      <button
        type="button"
        className={`menu-item ${currentTab === 'analytics' ? 'active' : ''}`}
        onClick={() => handleTabChange('analytics')}
        aria-current={currentTab === 'analytics' ? 'page' : undefined}
      >
        <span className="icon" aria-hidden="true">📊</span>
        <span className="label">Analytics</span>
      </button>

      {/* Weak Areas - Standalone */}
      <button
        type="button"
        className={`menu-item ${currentTab === 'weak-areas' ? 'active' : ''}`}
        onClick={() => handleTabChange('weak-areas')}
        aria-current={currentTab === 'weak-areas' ? 'page' : undefined}
      >
        <span className="icon" aria-hidden="true">🎯</span>
        <span className="label">Weak Areas</span>
      </button>

      {/* Expandable Groups */}
      {Object.entries(menuGroups).map(([groupKey, group]) => (
        <div key={groupKey} className="menu-group">
          <button
            type="button"
            className="group-header"
            onClick={() => toggleGroup(groupKey)}
            aria-expanded={expandedGroups[groupKey]}
            aria-controls={`group-${groupKey}-content`}
          >
            <span className="group-title">{group.title}</span>
            <span className="expand-icon" aria-hidden="true">{expandedGroups[groupKey] ? '▼' : '▶'}</span>
          </button>

          {expandedGroups[groupKey] && (
            <div className="group-items" id={`group-${groupKey}-content`}>
              {group.items.map(item => (
                <button
                  type="button"
                  key={item.id}
                  className={`menu-item sub-item ${currentTab === item.id ? 'active' : ''}`}
                  onClick={() => handleTabChange(item.id)}
                  aria-current={currentTab === item.id ? 'page' : undefined}
                >
                  <span className="icon" aria-hidden="true">{item.icon}</span>
                  <span className="label">{item.label}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
});

export default Sidebar;
