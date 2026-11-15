"""Rough phrase start times from Gemini (through kapi), used by assemble.py as alignment anchors.

  python3 tools/anchors.py chXX      (after one assemble.py run, which writes work/asm/n_<hash>_t<k>.wav)

For each narration chunk: numbered phrase list (same split as assemble.align) + the chunk audio -> gemini-3.8-flash
-> audio/chXX/anchors/<hash>_t<k>.json {"starts": [sec or null, ...]}. The DP then prefers pause boundaries near
these, which fixes slow dramatic passages where pure length matching shifts subtitles by a whole phrase.
Cached: delete a file to redo it."""
import json, os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from parts import load_voice, parse
ch = sys.argv[1]; v = load_voice(); D = f'audio/{ch}'; os.makedirs(f'{D}/anchors', exist_ok=True)
picks = json.load(open(f'{D}/picks.json')) if os.path.exists(f'{D}/picks.json') else {}
KAPI = os.path.expanduser('~/Desktop/projects/knight-api/target/debug/kapi')
def phrases(text): return [p.strip() for p in re.split(r'(?<=[\.،,!\?؟:…؛])\s+|\n+', text) if p.strip()]
for p in parse(f'script/{ch}.txt', v):
    if p['type'] != 'narr': continue
    k = picks.get(p['hash'], 1); wav = f'work/asm/n_{p["hash"]}_t{k}.wav'; out = f'{D}/anchors/{p["hash"]}_t{k}.json'
    if os.path.exists(out): continue
    if not os.path.exists(wav): sys.exit(f'missing {wav}: run tools/assemble.py {ch} once first')
    ph = phrases(p['text']); tmp = tempfile.mkdtemp()
    mp3 = f'{tmp}/chunk.mp3'; lst = f'{tmp}/phrases.txt'
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', wav, '-ac', '1', '-b:a', '96k', mp3], check=True)
    open(lst, 'w', encoding='utf8').write('\n'.join(f'{i + 1}. {x}' for i, x in enumerate(ph)))
    prompt = ('The audio is one Arabic narration take. phrases.txt is its script split into numbered phrases, in order. '
              'Listen carefully and give the time in seconds (0.1 s precision) at which the narrator STARTS saying each phrase. '
              'Answer ONLY with JSON: {"starts": [s1, s2, ...]} with exactly ' + str(len(ph)) + ' numbers (null if a phrase is not spoken).')
    r = subprocess.run([KAPI, 'gen', '--model', 'gemini-3.8-flash', '--file', mp3, '--file', lst, '--wait-s', '300',
                        '--request-id', f'anchors-{p["hash"]}-t{k}' + os.environ.get('RETRY', ''), prompt], capture_output=True, text=True)
    try:
        txt = json.loads(r.stdout.strip().splitlines()[-1])['text']
        starts = json.loads(re.search(r'\{.*\}', txt, re.S).group(0))['starts']
        assert len(starts) == len(ph)
    except Exception as e:
        print(f'{p["hash"]}: no usable answer ({e.__class__.__name__}); skipped'); continue
    json.dump({'starts': starts}, open(out, 'w')); print(f'{p["hash"]}: {len(ph)} anchors')
