// Sidebar with Expandable Groups
import React, { useState } from 'react';
import './Sidebar.css';

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ currentTab, setCurrentTab }) => {
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    planning: true,
    training: false,
    knowledge: false,
    enhancement: false,
    admin: false
  });

  const toggleGroup = (group: string) => {
    setExpandedGroups(prev => ({
      ...prev,
      [group]: !prev[group]
    }));
  };

  const menuGroups = {
    planning: {
      title: '🗺️ Planning',
      items: [
        { id: 'war-map', label: 'War Map', icon: '🗓️' },
        { id: 'syllabus', label: 'Syllabus', icon: '🧭' },
        { id: 'quests', label: 'Quests', icon: '📜' }
      ]
    },
    training: {
      title: '💪 Training',
      items: [
        { id: 'dojo', label: 'Anki Dojo', icon: '🥋' },
        { id: 'answer-writing', label: 'Answer Writing', icon: '✍️' },
        { id: 'scribe', label: 'The Scribe (AI)', icon: '📜' },
        { id: 'mock-tests', label: 'Mock Tests', icon: '📋' },
        { id: 'arena', label: 'Boss Arena', icon: '⚔️' },
        { id: 'essay', label: 'Essay Workshop', icon: '✍️' },
        { id: 'csat', label: 'CSAT Prep', icon: '🧮' }
      ]
    },
    knowledge: {
      title: '📚 Knowledge',
      items: [
        { id: 'mimir', label: 'Mimir (AI)', icon: '🧙‍♂️' },
        { id: 'flashcards', label: 'Flashcards', icon: '🎴' },
        { id: 'seer', label: 'The Seer', icon: '🔮' },
        { id: 'ravens', label: 'The Ravens', icon: '🐦' },
        { id: 'pyq', label: 'The Archives', icon: '🏛️' },
        { id: 'codex', label: 'Yggdrasil', icon: '🌳' },
        { id: 'lore-tablets', label: 'Lore Tablets', icon: '📖' }
      ]
    },
    enhancement: {
      title: '⚡ Enhancement',
      items: [
        { id: 'armory', label: 'Armory', icon: '🛡️' }
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
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>UPSC SAGA</h2>
      </div>

      {/* Dashboard - Always visible */}
      <div
        className={`menu-item ${currentTab === 'dashboard' ? 'active' : ''}`}
        onClick={() => setCurrentTab('dashboard')}
      >
        <span className="icon">🏠</span>
        <span className="label">Dashboard</span>
      </div>

      {/* Analytics - Standalone */}
      <div
        className={`menu-item ${currentTab === 'analytics' ? 'active' : ''}`}
        onClick={() => setCurrentTab('analytics')}
      >
        <span className="icon">📊</span>
        <span className="label">Analytics</span>
      </div>

      {/* Weak Areas - Standalone */}
      <div
        className={`menu-item ${currentTab === 'weak-areas' ? 'active' : ''}`}
        onClick={() => setCurrentTab('weak-areas')}
      >
        <span className="icon">🎯</span>
        <span className="label">Weak Areas</span>
      </div>

      {/* Expandable Groups */}
      {Object.entries(menuGroups).map(([groupKey, group]) => (
        <div key={groupKey} className="menu-group">
          <div className="group-header" onClick={() => toggleGroup(groupKey)}>
            <span className="group-title">{group.title}</span>
            <span className="expand-icon">{expandedGroups[groupKey] ? '▼' : '▶'}</span>
          </div>

          {expandedGroups[groupKey] && (
            <div className="group-items">
              {group.items.map(item => (
                <div
                  key={item.id}
                  className={`menu-item sub-item ${currentTab === item.id ? 'active' : ''}`}
                  onClick={() => setCurrentTab(item.id)}
                >
                  <span className="icon">{item.icon}</span>
                  <span className="label">{item.label}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default Sidebar;