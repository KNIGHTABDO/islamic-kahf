"""Download what every @ayah marker in script/chXX.txt needs: the real recitation (everyayah.com) and the
Uthmani text (alquran.cloud). Optional --tafsir saves Ibn Kathir (Arabic, quran.com tafsir id 14) for fact-checking.
Usage: python3 tools/fetch_ayah.py ch01 [--tafsir]     Reciter: voice.json "reciter": an everyayah.com folder name, or "local:<name>" for licensed files in sources/quran/licensed/<name>/SSSAAA.mp3.
Files: sources/quran/audio/<reciter>/SSSAAA.mp3 (gitignored), sources/quran/text/S_A.json, sources/quran/tafsir/S_A.json"""
import argparse, json, os, shutil, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
from parts import load_voice, parse

UA = {'User-Agent': 'Mozilla/5.0 (episode-builder)'}
def get(url, tries=4):
    for i in range(tries):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except Exception as e:
            if i == tries - 1: raise
            time.sleep(2 + 3 * i)
BASMALA = 'بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ'

ap = argparse.ArgumentParser(); ap.add_argument('ch'); ap.add_argument('--tafsir', action='store_true'); a = ap.parse_args()
v = load_voice(); rec = v['reciter']
for d in [f'sources/quran/audio/{rec}', 'sources/quran/text', 'sources/quran/tafsir']: os.makedirs(d, exist_ok=True)
for p in parse(f'script/{a.ch}.txt', v):
    if p['type'] != 'ayah': continue
    s = p['sura']
    for n in p['ayat']:
        mp3 = f'sources/quran/audio/{rec}/{s:03d}{n:03d}.mp3'
        if os.path.exists(mp3): pass
        elif rec.startswith('local:'):   # licensed recordings you own or have written permission for (see reference/recitation-rights.md)
            src = f"sources/quran/licensed/{rec[6:]}/{s:03d}{n:03d}.mp3"
            if not os.path.exists(src): sys.exit(f'missing licensed recitation {src}')
            shutil.copy(src, mp3)
        else: open(mp3, 'wb').write(get(f'https://everyayah.com/data/{rec}/{s:03d}{n:03d}.mp3'))
        tj = f'sources/quran/text/{s}_{n}.json'
        if not os.path.exists(tj):
            d = json.loads(get(f'https://api.alquran.cloud/v1/ayah/{s}:{n}/quran-uthmani'))['data']
            text = d['text']
            if n == 1 and s not in (1, 9) and text.startswith(BASMALA): text = text[len(BASMALA):].strip()
            json.dump({'ref': f'{s}:{n}', 'sura': d['surah']['name'], 'suraEn': d['surah']['englishName'], 'text': text},
                      open(tj, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
        if a.tafsir:
            fj = f'sources/quran/tafsir/{s}_{n}.json'
            if not os.path.exists(fj):
                d = json.loads(get(f'https://api.quran.com/api/v4/tafsirs/14/by_ayah/{s}:{n}'))
                json.dump(d, open(fj, 'w', encoding='utf8'), ensure_ascii=False)
        print(f'{s}:{n} ok', json.load(open(tj, encoding='utf8'))['text'][:60])
