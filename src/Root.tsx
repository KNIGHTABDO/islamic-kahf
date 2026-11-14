import React from 'react';
import {Composition, Still} from 'remotion';
import {Episode, FPS} from './Episode';
import {Short, Thumb} from './Extras';
import {CHAPTERS} from './chapters';
import shorts from './shorts.json';
import type {Chapter, ShortClip} from './types';

// One composition per chapter (id = chapter id, e.g. "ch01"), plus thumb-<id> stills and short-<id> 9:16 clips.
// Frame count rule (same in tools/frames.mjs): Math.ceil(total * 30).
export const RemotionRoot: React.FC = () => {
  const byId = new Map<string, Chapter>(CHAPTERS.map((c) => [c.id, c]));
  return (<>
    {CHAPTERS.map((c) => <Composition key={c.id} id={c.id} component={Episode} defaultProps={{c}}
      durationInFrames={Math.ceil(c.total * FPS)} fps={FPS} width={1920} height={1080} />)}
    {CHAPTERS.map((c) => <Still key={'t' + c.id} id={'thumb-' + c.id} component={Thumb} defaultProps={{c}} width={1280} height={720} />)}
    {(shorts as ShortClip[]).filter((s) => byId.has(s.chapter)).map((s) => <Composition key={s.id} id={'short-' + s.id} component={Short}
      defaultProps={{c: byId.get(s.chapter)!, s}} durationInFrames={Math.ceil((s.to - s.from) * FPS)} fps={FPS} width={1080} height={1920} />)}
  </>);
};
