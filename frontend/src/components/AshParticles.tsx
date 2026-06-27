// /frontend/src/components/AshParticles.tsx
import React, { useEffect, useState } from 'react';

interface Particle {
  id: number;
  left: string;
  animationDuration: string;
  animationDelay: string;
  size: string;
}

interface AshParticlesProps {
  isRageMode: boolean;
}

// ⚡ Bolt: Wrapped in React.memo to prevent 50 animated DOM nodes from re-rendering
// when App state (like currentTab) changes. Also used lazy initialization to avoid
// a second render cycle on mount.
const AshParticles: React.FC<AshParticlesProps> = React.memo(({ isRageMode }) => {
  const [particles] = useState<Particle[]>(() => {
    const count = 50; // Number of particles
    const newParticles: Particle[] = [];
    for (let i = 0; i < count; i++) {
      newParticles.push({
        id: i,
        left: `${Math.random() * 100}%`,
        animationDuration: `${Math.random() * 5 + 5}s`, // 5-10s duration
        animationDelay: `${Math.random() * 5}s`,
        size: `${Math.random() * 3 + 2}px`,
      });
    }
    return newParticles;
  });

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      pointerEvents: 'none',
      zIndex: 50,
      overflow: 'hidden'
    }}>
      {particles.map((p) => (
        <div
          key={p.id}
          style={{
            position: 'absolute',
            left: p.left,
            width: p.size,
            height: p.size,
            borderRadius: '50%',
            backgroundColor: isRageMode ? '#ff4500' : 'rgba(255, 255, 255, 0.6)',
            boxShadow: isRageMode ? '0 0 10px #ff4500' : 'none',
            animationName: isRageMode ? 'ember-rise' : 'fall',
            animationDuration: p.animationDuration,
            animationDelay: p.animationDelay,
            animationTimingFunction: 'linear',
            animationIterationCount: 'infinite',
            top: isRageMode ? undefined : '-10px',
            bottom: isRageMode ? '-10px' : undefined,
          }}
        />
      ))}
    </div>
  );
};

export default AshParticles;