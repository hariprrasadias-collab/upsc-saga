// /frontend/src/components/AshParticles.tsx
import { useEffect, useState, memo } from 'react';

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

// ⚡ Bolt: Wrapped in React.memo to prevent unnecessary re-renders of all 50 particle nodes
// when the parent App component updates, as it only depends on a primitive boolean prop.
const AshParticles = memo(({ isRageMode }: AshParticlesProps) => {
  const [particles, setParticles] = useState<Particle[]>([]);

  useEffect(() => {
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
     
    setParticles(newParticles);
  }, []);

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
});

export default AshParticles;