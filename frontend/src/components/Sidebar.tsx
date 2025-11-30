// Sidebar with Expandable Groups
// Sidebar with Expandable Groups
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Sidebar.css';
import { useGlobal } from '../contexts/GlobalContext';

const Sidebar: React.FC = () => {
  const { currentTab, setCurrentTab, isSidebarOpen, toggleSidebar } = useGlobal();
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
        { id: 'syllabus', label: 'Syllabus', icon: '🧭' },
        { id: 'quests', label: 'Quests', icon: '📜' },
        { id: 'revision-cards', label: 'Revision Cards', icon: '⚡' },
        { id: 'mnemonics', label: 'Mnemonics', icon: '🧠' },
        { id: 'mindmap', label: 'Mind Map', icon: '🕸️' }
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
        { id: 'compilation', label: 'Monthly Compilation', icon: '📚' },
        { id: 'pyq', label: 'The Archives', icon: '🏛️' },
        { id: 'heatmap', label: 'PYQ Heatmap', icon: '📊' },
        { id: 'model-answers', label: 'Model Answers', icon: '📝' },
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
    <div className={`sidebar ${isSidebarOpen ? 'open' : 'closed'}`}>
      <div className="sidebar-header">
        <h2>UPSC SAGA</h2>
        {/* Mobile Close Button */}
        <button className="mobile-close-btn" onClick={toggleSidebar}>×</button>
      </div>

      {/* Dashboard - Always Top */}
      <div
        className={`menu-item ${currentTab === 'dashboard' ? 'active' : ''}`}
        onClick={() => handleTabChange('dashboard')}
      >
        <span className="icon">🏠</span>
        <span className="label">Dashboard</span>
      </div>

      {/* Analytics - Standalone */}
      <div
        className={`menu-item ${currentTab === 'analytics' ? 'active' : ''}`}
        onClick={() => handleTabChange('analytics')}
      >
        <span className="icon">📊</span>
        <span className="label">Analytics</span>
      </div>

      {/* Weak Areas - Standalone */}
      <div
        className={`menu-item ${currentTab === 'weak-areas' ? 'active' : ''}`}
        onClick={() => handleTabChange('weak-areas')}
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
                  onClick={() => handleTabChange(item.id)}
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