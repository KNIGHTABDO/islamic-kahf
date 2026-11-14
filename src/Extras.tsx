import React from 'react';
import {AbsoluteFill, Img, Sequence, staticFile} from 'remotion';
import {AMIRI, Episode, FPS, GOLD, RUQAA, Subtitles} from './Episode';
import type {Chapter, ShortClip} from './types';

// YouTube thumbnail (render with `npx remotion still`). Big gold Ruqaa title over a keyframe.
export const Thumb: React.FC<{c: Chapter}> = ({c}) => {
  const t = c.thumb ?? {bg: c.titleBg, text: c.title};
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <Img src={staticFile(t.bg)} style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'contrast(1.1) saturate(1.15)'}} />
      <AbsoluteFill style={{background: 'linear-gradient(to left, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.35) 55%, rgba(0,0,0,0) 80%)'}} />
      <AbsoluteFill style={{alignItems: 'flex-end', justifyContent: 'center', padding: '0 60px', direction: 'rtl'}}>
        <div style={{fontFamily: RUQAA, fontSize: t.text.length > 12 ? 120 : 150, lineHeight: 1.25, background: GOLD, WebkitBackgroundClip: 'text',
          backgroundClip: 'text', color: 'transparent', filter: 'drop-shadow(0 4px 10px rgba(0,0,0,0.9))', maxWidth: 760, textAlign: 'right'}}>{t.text}</div>
        {t.sub && <div style={{fontFamily: AMIRI, fontWeight: 700, fontSize: 48, color: '#fbf3e2', textShadow: '0 3px 10px #000', marginTop: 6}}>{t.sub}</div>}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// 9:16 Short cut from a chapter: blurred fill behind, the 16:9 frame in the middle, big subtitles under it, hook on top.
export const Short: React.FC<{c: Chapter; s: ShortClip}> = ({c, s}) => {
  const off = -Math.round(s.from * FPS);
  const frame = (noAudio: boolean) => <Sequence from={off}><Episode c={c} noSubs noAudio={noAudio} /></Sequence>;
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <AbsoluteFill style={{transform: 'scale(3.2)', filter: 'blur(28px) brightness(0.55)'}}>
        <div style={{position: 'absolute', left: (1080 - 1920) / 2, top: (1920 - 1080) / 2, width: 1920, height: 1080}}>{frame(true)}</div>
      </AbsoluteFill>
      <div style={{position: 'absolute', left: 0, top: 656, width: 1920, height: 1080, transform: 'scale(0.5625)', transformOrigin: 'top left'}}>{frame(false)}</div>
      {s.hook && <div style={{position: 'absolute', top: 300, width: '100%', textAlign: 'center', direction: 'rtl', padding: '0 60px', boxSizing: 'border-box',
        fontFamily: RUQAA, fontSize: 88, lineHeight: 1.3, background: GOLD, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent',
        filter: 'drop-shadow(0 4px 10px rgba(0,0,0,0.9))'}}>{s.hook}</div>}
      <Sequence from={off}><Subtitles c={c} size={64} bottom={520} /></Sequence>
    </AbsoluteFill>
  );
};
