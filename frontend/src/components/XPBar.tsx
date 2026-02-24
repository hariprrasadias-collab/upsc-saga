// /frontend/src/components/XPBar.tsx
import React from 'react';
import './XPBar.css';

// Define props: current XP amount and the target XP needed for the next level
interface XPBarProps {
  currentXP: number;
  maxXP: number;
}

const XPBar: React.FC<XPBarProps> = ({ currentXP, maxXP }) => {
  // Calculate percentage. Ensure it doesn't exceed 100% or go below 0%.
  const percentage = Math.min(Math.max((currentXP / maxXP) * 100, 0), 100);

  return (
    <div className="xp-container">
      <div className="xp-header">
        <span>Experience</span>
        {/* Display the numerical values */}
        <span>{currentXP} / {maxXP} XP</span>
      </div>
      {/* The container for the bar images */}
      <div
        className="xp-bar-frame"
        role="progressbar"
        aria-valuenow={currentXP}
        aria-valuemin={0}
        aria-valuemax={maxXP}
        aria-label="Experience Progress"
        title={`${currentXP} / ${maxXP} XP`}
      >
        {/* The dynamic fill layer. Its width depends on the calculated percentage. */}
        <div
          className="xp-bar-fill"
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
};

export default XPBar;