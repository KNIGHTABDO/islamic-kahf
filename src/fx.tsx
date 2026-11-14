import React from 'react';
import {AbsoluteFill, interpolate, random, useCurrentFrame} from 'remotion';
import type {FX} from './types';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const screen = {mixBlendMode: 'screen' as const, pointerEvents: 'none' as const};

export const Embers: React.FC<{n?: number}> = ({n = 38}) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={screen}>{Array.from({length: n}).map((_, i) => {
    const p = (f * (0.004 + random(`es${i}`) * 0.006) + random(`ep${i}`)) % 1;
    const sz = 3 + random(`ez${i}`) * 6;
    return <div key={i} style={{position: 'absolute', left: `${random(`ex${i}`) * 100 + Math.sin(f / 22 + i) * 2.5}%`,
      top: `${108 - p * 120}%`, width: sz, height: sz, borderRadius: '50%', background: '#ffb347',
      opacity: Math.sin(p * Math.PI) * (0.5 + 0.5 * Math.sin(f / 4 + i * 3)),
      boxShadow: `0 0 ${sz * 3}px ${sz}px rgba(255,120,30,0.55)`}} />;
  })}</AbsoluteFill>;
};

export const Dust: React.FC<{n?: number}> = ({n = 45}) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={screen}>{Array.from({length: n}).map((_, i) => {
    const sz = 1.5 + random(`dz${i}`) * 3.5;
    return <div key={i} style={{position: 'absolute',
      left: `${(random(`dx${i}`) * 110 + f * (0.02 + random(`dv${i}`) * 0.05)) % 110 - 5}%`,
      top: `${random(`dy${i}`) * 100 + Math.sin(f / 40 + i) * 1.5}%`, width: sz, height: sz, borderRadius: '50%',
      background: '#fff6dc', opacity: 0.25 + 0.35 * Math.sin(f / 25 + i * 1.7) ** 2, filter: 'blur(0.6px)'}} />;
  })}</AbsoluteFill>;
};

export const Fog: React.FC<{tint?: string}> = ({tint = '190,200,230'}) => {
  const f = useCurrentFrame();
  const blob = (i: number, top: number, w: number, sp: number, o: number) => <div key={i} style={{
    position: 'absolute', top: `${top}%`, left: `${-40 + ((f * sp + i * 37) % 140)}%`, width: `${w}%`, height: '45%',
    background: `radial-gradient(ellipse at center, rgba(${tint},0.55) 0%, rgba(${tint},0) 70%)`, opacity: o, filter: 'blur(30px)'}} />;
  return <AbsoluteFill style={screen}>{blob(1, 62, 80, 0.08, 0.35)}{blob(2, 70, 90, 0.05, 0.3)}{blob(3, 55, 70, 0.11, 0.2)}</AbsoluteFill>;
};

const Smoke: React.FC = () => <Fog tint="120,110,100" />;

const FireFlicker: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{...screen, background: 'radial-gradient(ellipse at 15% 20%, rgba(255,140,40,1), rgba(255,90,20,0) 60%)',
    opacity: 0.1 + 0.08 * Math.sin(f * 0.9) + 0.06 * Math.sin(f * 2.3 + 1) + 0.05 * (random(`ff${f}`) - 0.5)}} />;
};

const LampGlow: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{...screen, background: 'radial-gradient(circle at 38% 85%, rgba(255,170,60,1), rgba(255,120,30,0) 45%)',
    opacity: 0.22 + 0.07 * Math.sin(f * 0.7) + 0.05 * Math.sin(f * 1.9 + 2)}} />;
};

const GodRays: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{...screen, overflow: 'hidden'}}>{[0, 1, 2, 3].map((i) => <div key={i} style={{
    position: 'absolute', right: `${2 + i * 7}%`, top: '-20%', width: `${7 + i * 2}%`, height: '150%', transformOrigin: 'top center',
    transform: `rotate(${32 + i * 4}deg)`, background: 'linear-gradient(to bottom, rgba(200,220,255,0.55), rgba(200,220,255,0))',
    opacity: 0.25 + 0.15 * Math.sin(f / (30 + i * 7) + i), filter: 'blur(18px)'}} />)}</AbsoluteFill>;
};

const Rain: React.FC<{snow?: boolean}> = ({snow}) => {
  const f = useCurrentFrame();
  const n = snow ? 90 : 140;
  return <AbsoluteFill style={{pointerEvents: 'none', opacity: snow ? 0.8 : 0.35}}>{Array.from({length: n}).map((_, i) => {
    const sp = snow ? 0.002 + random(`rs${i}`) * 0.002 : 0.03 + random(`rs${i}`) * 0.02;
    const p = (f * sp + random(`rp${i}`)) % 1;
    const x = random(`rx${i}`) * 100 + (snow ? Math.sin(f / 30 + i) * 1.5 : p * 6);
    return <div key={i} style={{position: 'absolute', left: `${x}%`, top: `${p * 110 - 5}%`,
      width: snow ? 4 : 1.5, height: snow ? 4 : 38, borderRadius: snow ? '50%' : 1,
      background: snow ? '#fff' : 'linear-gradient(to bottom, rgba(220,230,255,0), rgba(220,230,255,0.9))',
      transform: snow ? undefined : 'rotate(8deg)'}} />;
  })}</AbsoluteFill>;
};

const Flash: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{background: '#fff3e0', opacity: interpolate(f, [0, 2, 9], [0, 0.85, 0], clamp)}} />;
};

export const Grain: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{opacity: 0.08, mixBlendMode: 'overlay', pointerEvents: 'none'}}>
    <svg width="100%" height="100%"><filter id="g"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed={f % 9} /></filter>
      <rect width="100%" height="100%" filter="url(#g)" /></svg></AbsoluteFill>;
};

export const Vignette: React.FC = () => <AbsoluteFill style={{pointerEvents: 'none',
  background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,0.6) 100%)'}} />;

// Order = draw order (light first, particles on top, flash last).
const ORDER: [FX, React.FC][] = [['fire', FireFlicker], ['lamp', LampGlow], ['rays', GodRays], ['fog', Fog], ['smoke', Smoke],
  ['rain', () => <Rain />], ['snow', () => <Rain snow />], ['embers', Embers], ['dust', Dust], ['flash', Flash]];
export const Overlays: React.FC<{fx?: FX[]}> = ({fx}) => <>{ORDER.filter(([k]) => fx?.includes(k)).map(([k, C]) => <C key={k} />)}</>;
