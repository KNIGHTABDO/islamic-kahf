"""Parse script/chXX.txt into ordered parts. Shared by tts.py, fetch_ayah.py and assemble.py.

Script format (UTF-8):
  # comment line (never spoken)
  @ayah 18:10-12      real recitation of Qur'an 18:10..12 goes here (never TTS the Qur'an)
  @title              title card: a silent gap of titleDur seconds in the narration
  @pause 1.5          silence, seconds (music swells)
  anything else       fully diacritized Fusha narration; a blank line ends a paragraph
Narration between markers becomes one TTS take, split at paragraph boundaries only when it is longer than
voice.json maxWords (one take per chunk, same voice, same settings).
"""
import hashlib, json, re, sys

def load_voice(path='voice.json'):
    return json.load(open(path, encoding='utf8'))

def take_hash(text, v):
    key = '\n'.join([v['model'], v['voice'], str(v['temperature']), v['direction'], text])
    return hashlib.sha1(key.encode('utf8')).hexdigest()[:8]

def parse(path, v):
    parts, paras, cur = [], [], []
    def flush_para():
        if cur: paras.append(' '.join(cur)); cur.clear()
    def flush_narr():
        flush_para()
        if not paras: return
        chunk = []
        for p in paras:
            if chunk and len(' '.join(chunk + [p]).split()) > v['maxWords']:
                parts.append(chunk); chunk = []
            chunk.append(p)
        if chunk: parts.append(chunk)
        paras.clear()
    for raw in open(path, encoding='utf8'):
        ln = raw.strip()
        if ln.startswith('#'): continue
        if not ln: flush_para(); continue
        if ln.startswith('@'):
            flush_narr()
            m = re.match(r'@ayah\s+(\d+):(\d+)(?:-(\d+))?\s*$', ln)
            if m:
                s, a = int(m.group(1)), int(m.group(2)); b = int(m.group(3) or a)
                parts.append({'type': 'ayah', 'sura': s, 'ayat': list(range(a, b + 1))}); continue
            if ln == '@title': parts.append({'type': 'title'}); continue
            m = re.match(r'@pause\s+([\d.]+)\s*$', ln)
            if m: parts.append({'type': 'pause', 'sec': float(m.group(1))}); continue
            sys.exit(f'unknown marker: {ln}')
        cur.append(ln)
    flush_narr()
    out = []
    for p in parts:
        if isinstance(p, list):
            text = '\n'.join(p)
            n = len(text.split())
            if n > v['maxWords']: print(f'warning: one paragraph has {n} words > maxWords {v["maxWords"]}', file=sys.stderr)
            out.append({'type': 'narr', 'text': text, 'words': n, 'hash': take_hash(text, v)})
        else:
            out.append(p)
    return out

if __name__ == '__main__':
    v = load_voice()
    for i, p in enumerate(parse(sys.argv[1], v)):
        print(i, p['type'], p.get('hash', ''), p.get('words', ''), p.get('sura', ''), p.get('ayat', ''), p.get('sec', ''))
