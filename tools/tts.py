"""Generate narration takes for one chapter with kapi (AI Studio Flash TTS through the user's Brave), then the studio chain.
Usage (project root):  python3 tools/tts.py ch01 [--takes 2] [--only HASH]
Writes audio/ch01/raw_<hash>_t<k>.wav, audio/ch01/st_<hash>_t<k>.wav (studio), audio/ch01/review/NN_<hash>_t<k>.mp3.
Rerunning skips takes that exist; editing a paragraph changes its hash so only that chunk is regenerated.
Pick takes in audio/ch01/picks.json {"<hash>": k} (default take 1)."""
import argparse, glob, json, os, shutil, subprocess, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from parts import load_voice, parse

RUN = time.strftime('%m%d%H%M%S')  # fresh request-ids each run: a reused id returns the old job (failed or with files elsewhere)
KAPI = os.path.expanduser('~/Desktop/projects/knight-api/target/debug/kapi')
ap = argparse.ArgumentParser(); ap.add_argument('ch'); ap.add_argument('--takes', type=int, default=1); ap.add_argument('--only')
a = ap.parse_args()
v = load_voice(); proj = os.path.basename(os.getcwd())
D = f'audio/{a.ch}'; os.makedirs(f'{D}/review', exist_ok=True)
parts = [p for p in parse(f'script/{a.ch}.txt', v) if p['type'] == 'narr']
dur = lambda f: float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout or 0)

def run_take(p, k):
    raw = f'{D}/raw_{p["hash"]}_t{k}.wav'
    if os.path.exists(raw): return raw
    prompt = v['direction'] + '\n\n' + p['text']
    for attempt in range(1, 4):
        out = f'{os.path.abspath("work")}/tts/{a.ch}_{p["hash"]}_t{k}_{attempt}'
        cmd = [KAPI, 'gen', '--model', v['model'], '--param', f'voice={v["voice"]}', '--param', f'Temperature={v["temperature"]}',
               '--request-id', f'{proj}-{a.ch}-{p["hash"]}-t{k}-a{attempt}-{RUN}', '--out', out, '--wait-s', '400', prompt]
        r = subprocess.run(cmd, capture_output=True, text=True)
        try: j = json.loads(r.stdout.splitlines()[0])
        except Exception: j = {'status': 'error', 'error': r.stdout[:200] + r.stderr[:200]}
        if j.get('status') == 'running':
            r2 = subprocess.run([KAPI, 'job', j['id'], '--wait-s', '400'], capture_output=True, text=True)
            try: j = json.loads(r2.stdout.splitlines()[0])
            except Exception: pass
        # a reused request-id returns the earlier job, whose files sit in that job's own out dir
        w = sorted(glob.glob(f'{out}/**/*.wav', recursive=True)) or [f['path'] for f in (j.get('files') or []) if str(f.get('path', '')).endswith('.wav') and os.path.exists(f['path'])]
        if w:
            shutil.copy(w[0], raw); return raw
        print(f'  take {k} attempt {attempt} failed: {str(j.get("error"))[:160]}', flush=True); time.sleep(5)
    return None

for i, p in enumerate(parts, 1):
    if a.only and p['hash'] != a.only: continue
    for k in range(1, a.takes + 1):
        raw = run_take(p, k)
        if not raw: print(f'FAILED chunk {i} {p["hash"]} take {k}'); continue
        st = f'{D}/st_{p["hash"]}_t{k}.wav'
        if not os.path.exists(st): subprocess.run(['bash', 'tools/studio.sh', raw, st], check=True, capture_output=True)
        mp3 = f'{D}/review/{i:02d}_{p["hash"]}_t{k}.mp3'
        if not os.path.exists(mp3): subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', st, '-b:a', '160k', mp3], check=True)
        d = dur(raw); wps = p['words'] / d if d else 0
        print(f'chunk {i:02d} {p["hash"]} t{k}: {d:6.1f}s {p["words"]} words {wps:.2f} w/s  -> {mp3}', flush=True)
print('done. Send the review mp3s to the user to rate; record choices in', f'{D}/picks.json')
