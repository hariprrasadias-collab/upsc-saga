/* LoadingRune.tsx — Cinematic Loading Component */
import React from 'react';
import './LoadingRune.css';

interface LoadingRuneProps {
  variant?: 'full' | 'inline';
  message?: string;
}

const LoadingRune: React.FC<LoadingRuneProps> = ({
  variant = 'full',
  message = 'Summoning the Realm'
}) => {
  return (
    <div className={`loading-rune loading-rune--${variant}`} role="status" aria-label={message}>
      <div className="loading-rune__circle">
        {/* Outer rotating ring */}
        <svg className="loading-rune__svg" viewBox="0 0 100 100" aria-hidden="true">
          <circle
            cx="50" cy="50" r="44"
            className="loading-rune__track"
          />
          <circle
            cx="50" cy="50" r="44"
            className="loading-rune__arc"
          />
        </svg>

        {/* Inner runic cross */}
        <svg className="loading-rune__inner" viewBox="0 0 40 40" aria-hidden="true">
          <line x1="20" y1="4" x2="20" y2="36" stroke="currentColor" strokeWidth="2.5" strokeLinecap="square" />
          <line x1="4" y1="20" x2="36" y2="20" stroke="currentColor" strokeWidth="2.5" strokeLinecap="square" />
          <line x1="20" y1="4" x2="20" y2="10" stroke="var(--color-crimson)" strokeWidth="2.5" />
          <rect x="17" y="17" width="6" height="6" fill="var(--color-amber)" className="loading-rune__core" />
        </svg>
      </div>

      {variant === 'full' && (
        <div className="loading-rune__text">
          <span className="loading-rune__label">{message}</span>
          <span className="loading-rune__dots" aria-hidden="true">
            <span />
            <span />
            <span />
          </span>
        </div>
      )}
    </div>
  );
};

export default LoadingRune;
