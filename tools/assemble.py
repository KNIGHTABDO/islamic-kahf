"""Assemble one chapter's narration track and subtitle timing.
Usage: python3 tools/assemble.py ch01 [--narr-at 1.0]
Inputs : script/ch01.txt, audio/ch01/st_<hash>_t<k>.wav (picked via audio/ch01/picks.json, default take 1),
         sources/quran/audio/<reciter>/*.mp3 + sources/quran/text/*.json (run fetch_ayah.py first)
Outputs: public/ch01/narration.wav (48k stereo), public/ch01/lines.json:
         {narrDur, titleGap (narration-relative start of the @title gap or null), swells [[a,b]...] (from @pause),
          lines [[a,b,text]...], verses [{a,b,ref,text}...]}   (all times narration-relative; build.py adds narrAt)
Subtitles come from aligning each chunk's script text to its own audio (silencedetect + DP on character weight),
then splitting display lines to <= 7 words. Check the printed table: a phrase whose duration is far from its
expected length means the take skipped or repeated words; listen to that chunk."""
import argparse, json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from parts import load_voice, parse

SR = 48000
ap = argparse.ArgumentParser(); ap.add_argument('ch'); a = ap.parse_args()
v = load_voice(); P = v['pauses']; D = f'audio/{a.ch}'; OUT = f'public/{a.ch}'; os.makedirs(OUT, exist_ok=True)
os.makedirs('work/asm', exist_ok=True)
picks = json.load(open(f'{D}/picks.json')) if os.path.exists(f'{D}/picks.json') else {}
run = lambda *c: subprocess.run(c, check=True, capture_output=True, text=True)
def dur(f): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)

HARAKAT = re.compile('[\u064C-\u0650\u0652-\u0655\u0670]')  # keep shadda U+0651 and tanween fath U+064B
def display(t): return re.sub(r'\s+', ' ', HARAKAT.sub('', t)).strip()

def speech_chunks(f):
    err = subprocess.run(['ffmpeg', '-i', f, '-af', 'silencedetect=noise=-38dB:d=0.12', '-f', 'null', '-'], capture_output=True, text=True).stderr
    ss = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', err)]; se = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', err)]
    total = dur(f); ch, cur = [], 0.0
    for s0, e0 in zip(ss, se):
        if s0 - cur > 0.08: ch.append((cur, s0))
        cur = e0
    if total - cur > 0.08: ch.append((cur, total))
    return ch

PUNCT = r'[\.،,!\?؟:…؛]'
def weight(p): return len(re.sub(r'[\s\.،,!\?؟:…؛"«»]', '', p)) + 2

def align(f, text):
    """DP: contiguous script phrases -> contiguous speech chunks (each group <= 3 chunks, <= 6 phrases)."""
    phrases = [p.strip() for p in re.split(r'(?<=[\.،,!\?؟:…؛])\s+|\n+', text) if p.strip()]
    chunks = speech_chunks(f); W = [weight(p) for p in phrases]; Pn, N = len(phrases), len(chunks)
    rate = sum(W) / max(1e-6, sum(b - a for a, b in chunks)); INF = float('inf')
    best = [[INF] * (N + 1) for _ in range(Pn + 1)]; back = [[None] * (N + 1) for _ in range(Pn + 1)]; best[0][0] = 0
    for j in range(1, N + 1):
        for i in range(1, Pn + 1):
            for m in range(max(0, j - 3), j):
                speech = sum(c[1] - c[0] for c in chunks[m:j])
                for k in range(max(0, i - 6), i):
                    if best[k][m] == INF: continue
                    c = best[k][m] + (sum(W[k:i]) / rate - speech) ** 2 / max(speech, 0.3) + 0.9 * (j - m - 1)
                    if c < best[i][j]: best[i][j] = c; back[i][j] = (k, m)
    if best[Pn][N] == INF:
        print(f'  ! alignment failed for {f} ({Pn} phrases, {N} speech chunks): falling back to proportional timing')
        tot = sum(W); s0 = chunks[0][0] if chunks else 0.0; e0 = chunks[-1][1] if chunks else dur(f); out = []; t0 = s0
        for p, w in zip(phrases, W): d = (e0 - s0) * w / tot; out.append((t0, t0 + d, p)); t0 += d
        return out
    res, i, j = [], Pn, N
    while j > 0:
        k, m = back[i][j]; res.append((chunks[m][0], chunks[j - 1][1], ' '.join(phrases[k:i]), sum(W[k:i]) / rate)); i, j = k, m
    res.reverse()
    for s0, e0, t, exp in res:
        flag = '  <-- check' if abs((e0 - s0) - exp) > max(1.2, 0.45 * exp) else ''
        print(f'  {s0:7.2f}-{e0:7.2f} ({e0 - s0:4.1f}s exp {exp:4.1f}) {display(t)[:70]}{flag}')
    return [(s0, e0, t) for s0, e0, t, _ in res]

def split_display(a0, b0, text, maxw=7):
    words = display(text).split()
    if len(words) <= maxw: return [(a0, b0, ' '.join(words))]
    n = -(-len(words) // maxw); size = -(-len(words) // n)
    groups = [words[i:i + size] for i in range(0, len(words), size)]
    ws = [sum(len(w) + 1 for w in g) for g in groups]; tot = sum(ws); out, t = [], a0
    for g, w in zip(groups, ws):
        d = (b0 - a0) * w / tot; out.append((t, t + d, ' '.join(g))); t += d
    return out

segs, t = [], 0.0          # segs: (wav path, seconds) in order; t = running narration time
lines, verses, swells, title_gap = [], [], [], None
def silence(sec):
    global t
    f = f'work/asm/sil_{int(sec * 1000)}.wav'
    if not os.path.exists(f): run('ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'anullsrc=r={SR}:cl=stereo', '-t', f'{sec:.3f}', '-c:a', 'pcm_s16le', f)
    segs.append(f); t += sec

def norm(src, dst, lufs):
    L = re.findall(r'^\s+I:\s+(-?[\d.]+)', subprocess.run(['ffmpeg', '-nostats', '-i', src, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr, re.M)[-1]
    g = round(lufs - float(L), 2)
    run('ffmpeg', '-v', 'error', '-y', '-i', src, '-af', f'aresample={SR}:resampler=soxr,volume={g}dB,alimiter=limit=0.89:level=false', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_s16le', dst)

parts = parse(f'script/{a.ch}.txt', v); prev = None
for idx, p in enumerate(parts):
    if p['type'] == 'narr':
        k = picks.get(p['hash'], 1); src = f'{D}/st_{p["hash"]}_t{k}.wav'
        if not os.path.exists(src): sys.exit(f'missing {src}: run tools/tts.py {a.ch} first (or fix picks.json)')
        if prev == 'narr': silence(P['paragraph'])
        f = f'work/asm/n_{p["hash"]}_t{k}.wav'
        run('ffmpeg', '-v', 'error', '-y', '-i', src, '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_s16le', f)
        print(f'narr {p["hash"]} t{k} at {t:.2f}s')
        for s0, e0, txt in align(f, p['text']):
            lines += [[round(t + x, 2), round(t + y, 2), z] for x, y, z in split_display(s0, e0, txt)]
        segs.append(f); t += dur(f)
    elif p['type'] == 'ayah':
        silence(P['verseBefore'])
        for n_i, n in enumerate(p['ayat']):
            if n_i: silence(P['betweenAyat'])
            mp3 = f'sources/quran/audio/{v["reciter"]}/{p["sura"]:03d}{n:03d}.mp3'
            if not os.path.exists(mp3): sys.exit(f'missing {mp3}: run tools/fetch_ayah.py {a.ch}')
            f = f'work/asm/q_{p["sura"]}_{n}.wav'; norm(mp3, f, -17.0)
            txt = json.load(open(f'sources/quran/text/{p["sura"]}_{n}.json', encoding='utf8'))
            d = dur(f); verses.append({'a': round(t, 2), 'b': round(t + d, 2), 'key': f'{p["sura"]}:{n}', 'ref': f'{txt["sura"]} · {n}', 'text': txt['text']})
            print(f'ayah {p["sura"]}:{n} at {t:.2f}s ({d:.1f}s)'); segs.append(f); t += d
        silence(P['verseAfter'])
    elif p['type'] == 'title':
        title_gap = round(t + 0.3, 2); silence(v['titleDur'] + 0.6)
    elif p['type'] == 'pause':
        swells.append([round(t, 2), round(t + p['sec'], 2)]); silence(p['sec'])
    prev = p['type']

lst = 'work/asm/list.txt'
open(lst, 'w').write(''.join(f"file '{os.path.abspath(s)}'\n" for s in segs))
run('ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c:a', 'pcm_s16le', '-ar', str(SR), '-ac', '2', f'{OUT}/narration.wav')
run('ffmpeg', '-v', 'error', '-y', '-i', f'{OUT}/narration.wav', '-c:a', 'libmp3lame', '-b:a', '320k', f'{OUT}/narration.mp3')  # the render uses this (wav is too big for GitHub)
nd = round(dur(f'{OUT}/narration.wav'), 2)
json.dump({'narrDur': nd, 'titleGap': title_gap, 'swells': swells, 'lines': lines, 'verses': verses},
          open(f'{OUT}/lines.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(f'{OUT}/narration.wav {nd}s ({nd / 60:.1f} min), {len(lines)} subtitle lines, {len(verses)} verses, title gap {title_gap}')
