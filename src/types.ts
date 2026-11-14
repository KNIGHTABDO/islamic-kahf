// Resolved chapter data, written by tools/build.py into src/chapters/chXX.json. Never edit those JSONs by hand:
// edit plan/chXX.plan.json (and script/chXX.txt) and rerun build.py.
export type FX = 'embers' | 'fire' | 'fog' | 'dust' | 'rays' | 'lamp' | 'flash' | 'rain' | 'snow' | 'smoke';
export type Range = [number, number];
export type Shot = {
  t0: number; t1: number;            // absolute seconds in the chapter video
  src: string;                       // path under public/, e.g. "ch01/k3.png" or "ch01/king.mp4"
  video?: boolean; rate?: number;    // Flow / GIF clip; rate < 1 slows it to cover the shot
  loop?: boolean; clipDur?: number;  // short GIF-style loop: repeat (build.py fills clipDur) instead of slowing
  kb?: {s: Range; x: Range; y: Range};   // Ken Burns: scale, translate % (from -> to)
  par?: {x: Range; y: Range};        // depth parallax travel in px; needs public/<dir>/d_<name>.png
  fx?: FX[]; grade?: string;         // overlays; CSS filter string
};
export type Line = [number, number, string];        // narration-relative seconds, subtitle text
export type Verse = {a: number; b: number; ref: string; text: string}; // narration-relative, one per ayah
export type Location = {t: number; title: string; sub?: string; dur?: number}; // absolute
export type Cue = {kind: string; t: number; db: number; dur: number};          // SFX, absolute
export type Chapter = {
  id: string;
  series: string;         // channel name shown on the title card
  title: string;          // episode title (big Ruqaa)
  label?: string;         // e.g. "الفصل الأول"
  subtitle: string;       // e.g. "قصةٌ من القرآن الكريم · سورة الكهف"
  titleBg: string;        // still used blurred behind the title card
  titleAt: number; titleDur: number; total: number;   // absolute seconds
  narrAt: number; narrDur: number;                    // narration starts at narrAt (absolute)
  narration: string; sfx?: string; music?: string;    // paths under public/
  musicLevels?: {intro: number; under: number; swell: number};
  swells?: Range[];       // narration-relative ranges where music rises (pauses, title gap)
  outro?: {at: number; text: string; sub?: string};   // absolute; end card
  thumb?: {bg: string; text: string; sub?: string};   // YouTube thumbnail still (1280x720)
  shots: Shot[]; lines: Line[]; verses: Verse[]; locations: Location[]; cues: Cue[];
};
export type ShortClip = {id: string; chapter: string; from: number; to: number; hook?: string};
