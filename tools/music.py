"""Fit one or more Lyria takes to a chapter's length -> public/chXX/music.wav.   (UNTESTED on a long chapter: listen.)
Usage: python3 tools/music.py ch01 work/music/a.wav [work/music/b.wav ...]
Takes are chained with 4 s crossfades (cycling through the list) until they cover the chapter, then trimmed with a
3 s fade-out. Needs src/chapters/ch01.json (run build.py once, then again after this so Remotion sees the file).
Never time-stretch more than a few percent; long chapters need several takes, not one stretched take."""
import os, json, subprocess, sys
ch, takes = sys.argv[1], sys.argv[2:]
cj = f'src/chapters/{ch}.json'
if not os.path.exists(cj): sys.exit(f'{cj} missing: run python3 tools/build.py {ch} first (music needs the chapter length)')
total = json.load(open(cj, encoding='utf8'))['total'] + 0.5
dur = lambda f: float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)
seq, have, i = [], 0.0, 0
while have < total:
    f = takes[i % len(takes)]; seq.append(f); have += dur(f) - (4 if seq[1:] else 0); i += 1
    if i > 200: sys.exit('takes too short')
args = sum((['-i', f] for f in seq), [])
if len(seq) == 1: fc = '[0]aformat=sample_rates=48000:channel_layouts=stereo[m]'
else:
    fc, prev = '', '[0]'
    for k in range(1, len(seq)):
        fc += f'{prev}[{k}]acrossfade=d=4:c1=tri:c2=tri[x{k}];'; prev = f'[x{k}]'
    fc += f'{prev}aformat=sample_rates=48000:channel_layouts=stereo[m]'
fc += f';[m]atrim=0:{total},afade=t=out:st={total - 3}:d=3[o]'
subprocess.run(['ffmpeg', '-v', 'error', '-y', *args, '-filter_complex', fc, '-map', '[o]', '-c:a', 'pcm_s16le', f'public/{ch}/music.wav'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'public/{ch}/music.wav', '-c:a', 'libmp3lame', '-b:a', '320k', f'public/{ch}/music.mp3'], check=True)  # plan uses music.mp3 (wav too big for GitHub)
print(f'public/{ch}/music.wav (+ music.mp3) {total:.1f}s from {len(seq)} pieces')
