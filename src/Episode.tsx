import React from 'react';
import {AbsoluteFill, Audio, Easing, Img, Loop, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {loadFont as loadRuqaa} from '@remotion/google-fonts/ArefRuqaa';
import {loadFont as loadAmiri} from '@remotion/google-fonts/Amiri';
import {loadFont as loadQuran} from '@remotion/google-fonts/AmiriQuran';
import {ParallaxStill} from './Parallax';
import {Dust, Grain, Overlays, Vignette} from './fx';
import type {Chapter, Credits as Cr, Location as Loc, Shot, Verse} from './types';

export const {fontFamily: RUQAA} = loadRuqaa();
export const {fontFamily: AMIRI} = loadAmiri();
export const {fontFamily: QURAN} = loadQuran();
export const FPS = 30;
const XF = 0.3; // crossfade seconds between shots
export const GOLD = 'linear-gradient(180deg, #fff1c9 0%, #e8b65a 55%, #9c6a22 100%)';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const ease = Easing.bezier(0.45, 0, 0.55, 1);
const lerp = (r: [number, number], p: number) => r[0] + (r[1] - r[0]) * p;
const dirOf = (p: string) => (p.includes('/') ? p.slice(0, p.lastIndexOf('/') + 1) : '');
export const depthOf = (p: string) => dirOf(p) + 'd_' + p.slice(p.lastIndexOf('/') + 1).replace(/\.\w+$/, '.png');

export const ShotView: React.FC<{s: Shot; first?: boolean}> = ({s, first}) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [0, (s.t1 - s.t0 + XF) * FPS], [0, 1], {...clamp, easing: ease});
  const kb = s.kb ?? {s: [1.0, 1.06], x: [0, 0], y: [0, 0]};
  const media = {width: '100%', height: '100%', objectFit: 'cover' as const};
  const vid = <OffthreadVideo src={staticFile(s.src)} muted playbackRate={s.loop ? 1 : s.rate ?? 1} style={media} />;
  return (
    <AbsoluteFill style={{opacity: first ? 1 : interpolate(f, [0, XF * FPS], [0, 1], clamp)}}>
      <AbsoluteFill style={{transform: `translate(${lerp(kb.x, p)}%, ${lerp(kb.y, p)}%) scale(${lerp(kb.s, p)})`, filter: s.grade}}>
        {s.video ? (s.loop && s.clipDur ? <Loop durationInFrames={Math.max(1, Math.floor(s.clipDur * FPS))}>{vid}</Loop> : vid)
          : s.par ? <ParallaxStill src={s.src} depth={depthOf(s.src)} dx={lerp(s.par.x, p)} dy={lerp(s.par.y, p)} />
          : <Img src={staticFile(s.src)} style={media} />}
      </AbsoluteFill>
      <Overlays fx={s.fx} />
    </AbsoluteFill>
  );
};

// Ruq'ah location card: right-to-left ink wipe + growing gold rule.
const LocationCard: React.FC<{l: Loc}> = ({l}) => {
  const f = useCurrentFrame();
  const d = (l.dur ?? 3.3) * FPS;
  const out = interpolate(f, [d - 16, d], [1, 0], clamp);
  return (<>
    <div style={{position: 'absolute', top: 0, right: 0, width: 900, height: 330, opacity: out * 0.85,
      background: 'radial-gradient(ellipse at 85% 30%, rgba(0,0,0,0.75), rgba(0,0,0,0) 65%)'}} />
    <div style={{position: 'absolute', top: 70, right: 90, direction: 'rtl', textAlign: 'right', opacity: out}}>
      <div style={{fontFamily: RUQAA, fontSize: 78, color: '#f4e6c4', lineHeight: 1.25, textShadow: '0 3px 14px rgba(0,0,0,0.85)',
        clipPath: `inset(0 0 0 ${interpolate(f, [0, 28], [100, 0], {...clamp, easing: Easing.out(Easing.cubic)})}%)`}}>{l.title}</div>
      <div style={{height: 3, marginLeft: 'auto', background: 'linear-gradient(to left, #d9a94a, rgba(217,169,74,0))',
        width: `${interpolate(f, [10, 40], [0, 100], {...clamp, easing: Easing.out(Easing.cubic)})}%`}} />
      {l.sub && <div style={{fontFamily: AMIRI, fontSize: 34, color: '#d9c7a0', marginTop: 8, textShadow: '0 2px 10px rgba(0,0,0,0.9)',
        opacity: interpolate(f, [24, 40], [0, 1], clamp)}}>{l.sub}</div>}
    </div></>);
};

export const Subtitles: React.FC<{c: Chapter; size?: number; bottom?: number}> = ({c, size = 52, bottom = 78}) => {
  const t = useCurrentFrame() / FPS - c.narrAt;
  const cur = c.lines.find(([a, b]) => t >= a - 0.1 && t <= b + 0.35);
  if (!cur) return null;
  const [a, b, txt] = cur;
  const o = Math.min(interpolate(t, [a - 0.1, a + 0.12], [0, 1], clamp), interpolate(t, [b + 0.15, b + 0.35], [1, 0], clamp));
  return <div style={{position: 'absolute', bottom, width: '100%', padding: '0 40px', boxSizing: 'border-box', textAlign: 'center', direction: 'rtl', opacity: o}}>
    <span style={{fontFamily: AMIRI, fontSize: size, color: '#fbf3e2', fontWeight: 700, textShadow: '0 0 4px #000, 0 3px 12px rgba(0,0,0,0.95)'}}>{txt}</span>
  </div>;
};

// Qur'an verse card: exact Uthmani text + reference while the real recitation plays. Never TTS, never subtitled.
// Tanzil/alquran.cloud text puts waqf signs (U+06D6-U+06DC) after a space; a mark with no base letter renders as a box.
// Attach each one to the word before it, for display only (the stored text stays exact).
const quranDisplay = (t: string) => t.replace(/ ([\u06D6-\u06DC])/g, '$1');

const VerseCard: React.FC<{v: Verse}> = ({v}) => {
  const f = useCurrentFrame();
  const d = (v.b - v.a) * FPS;
  const o = Math.min(interpolate(f, [0, 12], [0, 1], clamp), interpolate(f, [d - 8, d + 6], [1, 0], clamp));
  const words = v.text.split(/\s+/).length;
  const size = words > 40 ? 46 : words > 24 ? 56 : words > 12 ? 66 : 78;
  return (
    <AbsoluteFill style={{opacity: o}}>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(5,8,20,0.82) 0%, rgba(5,8,20,0.9) 100%)'}} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', padding: '0 170px'}}>
        <div style={{fontFamily: QURAN, fontSize: size, lineHeight: 1.9, color: '#f6e7c1', direction: 'rtl', textAlign: 'center',
          textShadow: '0 0 18px rgba(232,182,90,0.35)'}}>{quranDisplay(v.text)}</div>
        <div style={{height: 2, width: 260, margin: '26px 0 14px', background: 'linear-gradient(to right, rgba(217,169,74,0), #d9a94a, rgba(217,169,74,0))'}} />
        <div style={{fontFamily: AMIRI, fontSize: 34, color: '#cdb98e', direction: 'rtl'}}>{v.ref}</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const TitleCard: React.FC<{c: Chapter}> = ({c}) => {
  const f = useCurrentFrame();
  const d = c.titleDur * FPS;
  const o = interpolate(f, [0, 24], [0, 1], clamp);
  return (
    <AbsoluteFill style={{background: '#050403', opacity: interpolate(f, [d - 29, d], [1, 0], clamp)}}>
      <AbsoluteFill style={{opacity: 0.28 * o}}>
        <Img src={staticFile(c.titleBg)} style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'blur(8px) brightness(0.6)'}} />
      </AbsoluteFill>
      <Dust n={60} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: o, direction: 'rtl',
        transform: `scale(${interpolate(f, [0, 150], [1.12, 1.0], {...clamp, easing: Easing.out(Easing.cubic)})})`}}>
        {c.label && <div style={{fontFamily: AMIRI, fontSize: 44, color: '#d9c7a0', opacity: interpolate(f, [10, 30], [0, 1], clamp)}}>{c.label}</div>}
        <div style={{fontFamily: RUQAA, fontSize: c.title.length > 14 ? 170 : 230, lineHeight: 1.3, background: GOLD, WebkitBackgroundClip: 'text',
          backgroundClip: 'text', color: 'transparent', filter: `drop-shadow(0 0 ${18 + 10 * Math.sin(f / 12)}px rgba(232,182,90,0.55))`}}>{c.title}</div>
        <div style={{fontFamily: AMIRI, fontSize: 40, color: '#cdb98e', marginTop: 10, opacity: interpolate(f, [30, 54], [0, 1], clamp)}}>{c.subtitle}</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Outro: React.FC<{text: string; sub?: string; series: string}> = ({text, sub, series}) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 20], [0, 1], clamp);
  return <AbsoluteFill style={{background: 'rgba(5,4,3,0.88)', opacity: o, alignItems: 'center', justifyContent: 'center', direction: 'rtl'}}>
    <Dust n={50} />
    <div style={{fontFamily: RUQAA, fontSize: 120, background: GOLD, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent'}}>{text}</div>
    {sub && <div style={{fontFamily: AMIRI, fontSize: 42, color: '#d9c7a0', marginTop: 12}}>{sub}</div>}
    <div style={{fontFamily: AMIRI, fontSize: 34, color: '#9f8d68', marginTop: 40}}>{series}</div>
  </AbsoluteFill>;
};

// Movie-style end roll. Every block has a fixed height, so the roll's total height is known and it scrolls at one
// constant speed; the end card fades in after the last block leaves and holds to the end.
const CH = {head: 620, h: 190, row: 74, line: 66, gap: 120, endHold: 8};
const Ornament: React.FC<{w?: number}> = ({w = 260}) => <div style={{display: 'flex', alignItems: 'center', gap: 18, justifyContent: 'center'}}>
  <div style={{width: w, height: 2, background: 'linear-gradient(90deg, transparent, #c9a45c)'}} />
  <div style={{width: 12, height: 12, transform: 'rotate(45deg)', border: '2px solid #e2c27a'}} />
  <div style={{width: w, height: 2, background: 'linear-gradient(270deg, transparent, #c9a45c)'}} />
</div>;
const Credits: React.FC<{k: Cr; series: string}> = ({k, series}) => {
  const f = useCurrentFrame();
  const {height: VH} = useVideoConfig();
  const D = k.dur * FPS, hold = CH.endHold * FPS;
  const H = (k.head ? CH.head : 0) + k.sections.reduce((a, s) => a + CH.h + (s.rows?.length ?? 0) * CH.row + (s.text?.length ?? 0) * CH.line + CH.gap, 0);
  const rollEnd = D - hold;
  const y = interpolate(f, [0, rollEnd], [VH, -H], clamp);
  const endO = interpolate(f, [rollEnd - 20, rollEnd + 25], [0, 1], clamp) * interpolate(f, [D - 40, D - 2], [1, 0], clamp);
  const bgO = interpolate(f, [0, 30], [0, 1], clamp);
  const rowStyle: React.CSSProperties = {height: CH.row, display: 'flex', alignItems: 'center', direction: 'rtl', width: 1500};
  return (
    <AbsoluteFill style={{background: '#050403', opacity: bgO}}>
      {k.bg && <AbsoluteFill style={{opacity: 0.22}}>
        <Img src={staticFile(k.bg)} style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'blur(14px) brightness(0.5) sepia(0.35)',
          transform: `scale(${interpolate(f, [0, D], [1.08, 1.22])})`}} />
      </AbsoluteFill>}
      <Dust n={55} />
      <AbsoluteFill style={{alignItems: 'center', opacity: interpolate(f, [rollEnd - 30, rollEnd], [1, 0], clamp)}}>
        <div style={{position: 'absolute', top: 0, transform: `translateY(${y}px)`, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
          {k.head && <div style={{height: CH.head, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', direction: 'rtl'}}>
            {k.head.label && <div style={{fontFamily: AMIRI, fontSize: 40, color: '#cdb98e', letterSpacing: 2}}>{k.head.label}</div>}
            <div style={{fontFamily: RUQAA, fontSize: 190, lineHeight: 1.35, background: GOLD, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent',
              filter: 'drop-shadow(0 0 22px rgba(232,182,90,0.45))'}}>{k.head.title}</div>
            {k.head.sub && <div style={{fontFamily: AMIRI, fontSize: 44, color: '#e9dcbc', marginTop: 4}}>{k.head.sub}</div>}
          </div>}
          {k.sections.map((s, i) => <div key={i} style={{display: 'flex', flexDirection: 'column', alignItems: 'center', paddingBottom: CH.gap}}>
            <div style={{height: CH.h, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 14}}>
              <div style={{fontFamily: RUQAA, fontSize: 76, lineHeight: 1.2, background: GOLD, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent'}}>{s.h}</div>
              <Ornament />
            </div>
            {s.rows?.map(([role, name], j) => <div key={j} style={rowStyle}>
              <div style={{flex: 1, textAlign: 'left', paddingLeft: 40, fontFamily: AMIRI, fontSize: 34, color: '#cdb98e', direction: 'rtl', order: 0}}>{role}</div>
              <div style={{width: 2, height: 30, background: 'rgba(201,164,92,0.45)', order: 1}} />
              <div style={{flex: 1, textAlign: 'right', paddingRight: 40, fontFamily: AMIRI, fontSize: 40, color: '#fbf3e2', fontWeight: 700, direction: 'rtl', order: 2}}>{name}</div>
            </div>)}
            {s.text?.map((t, j) => <div key={j} style={{height: CH.line, display: 'flex', alignItems: 'center', fontFamily: AMIRI, fontSize: 38,
              color: '#e9dcbc', direction: 'rtl', textAlign: 'center'}}>{t}</div>)}
          </div>)}
        </div>
      </AbsoluteFill>
      {k.end && <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', direction: 'rtl', opacity: endO,
        transform: `scale(${interpolate(f, [rollEnd - 20, D], [1.06, 1.0], clamp)})`}}>
        <div style={{fontFamily: RUQAA, fontSize: 150, lineHeight: 1.3, background: GOLD, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent',
          filter: `drop-shadow(0 0 ${18 + 8 * Math.sin(f / 14)}px rgba(232,182,90,0.5))`}}>{k.end.text}</div>
        <div style={{marginTop: 18}}><Ornament w={200} /></div>
        <div style={{fontFamily: AMIRI, fontSize: 44, color: '#e9dcbc', marginTop: 22}}>{k.end.sub ?? series}</div>
        {k.end.small && <div style={{fontFamily: AMIRI, fontSize: 30, color: '#9f8d68', marginTop: 30}}>{k.end.small}</div>}
      </AbsoluteFill>}
      <Vignette />
      <Grain />
    </AbsoluteFill>
  );
};

// Music level over the chapter: intro level before narration, low under narration, silent under every verse
// (no music under Qur'an), up during swells and after the narration, fade out at the end.
const musicVolume = (c: Chapter, frame: number, dur: number) => {
  const L = c.musicLevels ?? {intro: 0.55, under: 0.28, swell: 0.6};
  const t = frame / FPS, n = t - c.narrAt;
  let v = t < c.narrAt ? interpolate(t, [0, 0.66, c.narrAt], [0, L.intro, L.under], clamp)
    : interpolate(n, [c.narrDur, c.narrDur + 0.66], [L.under, L.swell], clamp);
  for (const [a, b] of c.swells ?? []) v = Math.max(v, Math.min(interpolate(n, [a, a + 0.6], [L.under, L.swell], clamp), interpolate(n, [b - 0.6, b], [L.swell, L.under], clamp)));
  for (const vs of c.verses) v *= 1 - Math.min(interpolate(n, [vs.a - 0.8, vs.a - 0.1], [0, 1], clamp), interpolate(n, [vs.b + 0.1, vs.b + 0.8], [1, 0], clamp));
  return v * interpolate(frame, [dur - (c.credits ? 120 : 30), dur], [1, 0], clamp);
};

export const Episode: React.FC<{c: Chapter; noAudio?: boolean; noSubs?: boolean}> = ({c, noAudio, noSubs}) => {
  const {durationInFrames} = useVideoConfig();
  const fr = (s: number) => Math.round(s * FPS);
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {c.shots.map((s, i) => {
        const from = fr(i === 0 ? s.t0 : s.t0 - XF);
        return <Sequence key={i} from={from} durationInFrames={fr(s.t1) - from + 1}><ShotView s={s} first={i === 0} /></Sequence>;
      })}
      {c.locations.map((l, i) => <Sequence key={'l' + i} from={fr(l.t)} durationInFrames={fr(l.dur ?? 3.3)}><LocationCard l={l} /></Sequence>)}
      <Vignette />
      <Grain />
      {c.verses.map((v, i) => <Sequence key={'v' + i} from={fr(c.narrAt + v.a - 0.2)} durationInFrames={fr(v.b - v.a + 0.4)}><VerseCard v={v} /></Sequence>)}
      {!noSubs && <Subtitles c={c} />}
      <Sequence from={fr(c.titleAt)} durationInFrames={fr(c.titleDur)}><TitleCard c={c} /></Sequence>
      {c.outro && <Sequence from={fr(c.outro.at)}><Outro text={c.outro.text} sub={c.outro.sub} series={c.series} /></Sequence>}
      {c.credits && <Sequence from={fr(c.credits.at)}><Credits k={c.credits} series={c.series} /></Sequence>}
      {!noAudio && <Sequence from={fr(c.narrAt)}><Audio src={staticFile(c.narration)} /></Sequence>}
      {!noAudio && c.sfx && <Audio src={staticFile(c.sfx)} />}
      {!noAudio && c.music && <Audio src={staticFile(c.music)} volume={(f) => musicVolume(c, f, durationInFrames)} />}
    </AbsoluteFill>
  );
};
