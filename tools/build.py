"""Resolve plan/chXX.plan.json + public/chXX/lines.json into src/chapters/chXX.json, regenerate src/chapters/index.ts,
then synthesize public/chXX/sfx.wav (make_sfx.py).   Usage: python3 tools/build.py ch01 [--no-sfx]

Times in the plan are "at" values (resolved to absolute seconds), with an optional "off" (seconds, may be negative):
  12.5               absolute seconds in the chapter video
  "line:<words>"     start of the first subtitle line containing <words> (harakat ignored); "line:<words>#2" = 2nd match
  "lineEnd:<words>"  end of that line
  "verse:18:10" / "verseEnd:18:10"   start / end of the recitation of that ayah
  "swell:0"          start of the n-th @pause      "title"  title card start      "end"  end of narration
Plan keys: see reference/plan-format.md. Shots run until the next shot's start (the last one to the end)."""
import argparse, glob, json, os, re, subprocess, sys

ap = argparse.ArgumentParser(); ap.add_argument('ch'); ap.add_argument('--no-sfx', action='store_true'); a = ap.parse_args()
ch = a.ch; plan = json.load(open(f'plan/{ch}.plan.json', encoding='utf8')); L = json.load(open(f'public/{ch}/lines.json', encoding='utf8'))
NA = plan.get('narrAt', 1.0); TD = plan.get('titleDur', 5.3); ND = L['narrDur']
HAR = re.compile('[ً-ٰٕـ]'); norm = lambda s: re.sub(r'\s+', ' ', HAR.sub('', s)).strip()
if L['titleGap'] is not None: TITLE = round(NA + L['titleGap'], 2)
else: TITLE = round(NA + ND + plan.get('titleAfter', 0.6), 2)

def at(x, off=0.0):
    if isinstance(x, (int, float)): return round(x + off, 2)
    if x == 'title': return round(TITLE + off, 2)
    if x == 'end': return round(NA + ND + off, 2)
    kind, _, arg = x.partition(':')
    if kind in ('line', 'lineEnd'):
        arg, _, nth = arg.partition('#'); nth = int(nth or 1); want = norm(arg)
        hits = [l for l in L['lines'] if want in norm(l[2])]
        if len(hits) < nth: sys.exit(f'{ch}: no subtitle line contains "{arg}" (match {nth}). Check script/subtitles.')
        l = hits[nth - 1]; return round(NA + (l[0] if kind == 'line' else l[1]) + off, 2)
    if kind in ('verse', 'verseEnd'):
        vs = [v for v in L['verses'] if v.get('key') == arg]
        if not vs: sys.exit(f'{ch}: no verse {arg} in lines.json')
        return round(NA + (vs[0]['a'] if kind == 'verse' else vs[0]['b']) + off, 2)
    if kind == 'swell': return round(NA + L['swells'][int(arg)][0] + off, 2)
    sys.exit(f'{ch}: bad at value {x!r}')
A = lambda o: at(o['at'], o.get('off', 0.0))

outro = None
if plan.get('outro'):
    o = plan['outro']; oat = A(o) if 'at' in o else round(NA + ND + 0.6 if L['titleGap'] is not None else TITLE + TD, 2)
    outro = {'at': oat, 'text': o['text'], **({'sub': o['sub']} if o.get('sub') else {})}
if outro: TOTAL = round(outro['at'] + plan['outro'].get('dur', 4.5), 2)
credits = None
if plan.get('credits'):   # movie-style end roll after the outro card (overlaps its last second)
    credits = {k: v for k, v in plan['credits'].items() if k != 'stats'}; credits['at'] = round(TOTAL - 1.0, 2)
    credits['dur'] = plan['credits'].get('dur', 45); TOTAL = round(credits['at'] + credits['dur'], 2)
elif L['titleGap'] is not None: TOTAL = round(NA + ND + plan.get('tail', 2.0), 2)
else: TOTAL = round(TITLE + TD, 2)

def probe(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout or 0)
shots = []
ps = sorted(plan['shots'], key=A)
for i, s in enumerate(ps):
    t0 = 0.0 if i == 0 else A(s); t1 = A(ps[i + 1]) if i + 1 < len(ps) else TOTAL
    if t1 - t0 < 0.4: print(f'warning: shot {s["src"]} lasts only {t1 - t0:.2f}s')
    o = {k: v for k, v in s.items() if k not in ('at', 'off', 'note')}; o.update(t0=t0, t1=t1)
    if not os.path.exists(f'public/{s["src"]}'): print(f'warning: missing public/{s["src"]}')
    elif s.get('video'):
        cl = probe(f'public/{s["src"]}')
        if s.get('loop'): o['clipDur'] = round(cl, 3)
        else:
            r = min(1.0, round(cl / (t1 - t0 + 0.3), 3))
            if r < 1: o['rate'] = r
            if r < 0.5: print(f'warning: {s["src"]} slowed to {r}x to cover {t1 - t0:.1f}s; use loop:true or split the shot')
    if s.get('par'):
        d, n = os.path.split(s['src']); dp = f'public/{d}/d_{os.path.splitext(n)[0]}.png'
        if not os.path.exists(dp): print(f'warning: par needs {dp} (tools/depth.sh)')
    shots.append(o)

locs = [{'t': A(l), 'title': l['title'], **({k: l[k] for k in ('sub', 'dur') if k in l})} for l in plan.get('locations', [])]
cues = [{'kind': q['kind'], 't': A(q), 'db': q.get('db', -14), 'dur': round(at(q['to'], q.get('toOff', 0)) - A(q), 2) if 'to' in q else q.get('dur', 0)} for q in plan.get('cues', [])]
if plan.get('titleSfx', True):
    cues += [{'kind': 'riser', 't': round(TITLE - 2.95, 2), 'db': -13, 'dur': 0}, {'kind': 'boom', 't': TITLE, 'db': -4, 'dur': 0},
             {'kind': 'chime', 't': round(TITLE + 0.05, 2), 'db': -12, 'dur': 0}]
cues = [q for q in cues if 0 <= q['t'] < TOTAL]; cues.sort(key=lambda q: q['t'])
swells = list(L['swells']) + ([[L['titleGap'], round(L['titleGap'] + TD, 2)]] if L['titleGap'] is not None else [])

if credits and plan['credits'].get('stats'):   # "details of the work", counted from the build itself
    ar = lambda n: str(n).translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩'))
    stills = {sh['src'] for sh in shots if not sh.get('video')}
    credits['sections'] = credits.get('sections', []) + [{'h': 'أرقام العمل', 'rows': [
        ['مدة الفصل', f'{ar(round(ND / 60))} دقيقة'], ['الآيات المتلوّة', ar(len(L['verses']))],
        ['اللوحات المرسومة', ar(len(stills))], ['اللقطات', ar(len(shots))],
        ['المقاطع المتحركة', ar(sum(1 for sh in shots if sh.get('video')))],
        ['سطور الترجمة', ar(len(L['lines']))], ['التصيير', f"{ar(plan['credits'].get('workers', 40))} خادمًا متوازيًا"]]}]
C = {'id': ch, 'series': plan.get('series', 'صندوق الحكايات'), 'title': plan['title'], 'subtitle': plan['subtitle'],
     **({'label': plan['label']} if plan.get('label') else {}), 'titleBg': plan['titleBg'],
     'titleAt': TITLE, 'titleDur': TD, 'total': TOTAL, 'narrAt': NA, 'narrDur': ND, 'narration': f'{ch}/narration.mp3',
     **({'sfx': f'{ch}/sfx.mp3'} if not a.no_sfx else {}),
     **({'music': plan['music'], 'musicLevels': plan.get('musicLevels', {'intro': 0.55, 'under': 0.28, 'swell': 0.6})} if plan.get('music') else {}),
     'swells': swells, **({'outro': outro} if outro else {}), **({'credits': credits} if credits else {}), **({'thumb': plan['thumb']} if plan.get('thumb') else {}),
     'shots': shots, 'lines': L['lines'], 'verses': L['verses'], 'locations': locs, 'cues': cues}
json.dump(C, open(f'src/chapters/{ch}.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)

ids = sorted(os.path.splitext(os.path.basename(p))[0] for p in glob.glob('src/chapters/ch*.json'))
open('src/chapters/index.ts', 'w').write("// generated by tools/build.py\nimport type {Chapter} from '../types';\n"
    + ''.join(f"import {i} from './{i}.json';\n" for i in ids)
    + f"export const CHAPTERS: Chapter[] = [{', '.join(f'{i} as unknown as Chapter' for i in ids)}];\n")
print(f'{ch}: total {TOTAL}s ({TOTAL / 60:.1f} min, {int(-(-TOTAL * 30 // 1))} frames) title at {TITLE}s, {len(shots)} shots, {len(cues)} cues, {len(locs)} locations')
if not a.no_sfx:
    subprocess.run([sys.executable, 'tools/make_sfx.py', ch], check=True)
    # the render uses MP3 (a 10+ min WAV is over GitHub's 100 MB file limit)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', f'public/{ch}/sfx.wav', '-c:a', 'libmp3lame', '-b:a', '256k', f'public/{ch}/sfx.mp3'], check=True)
