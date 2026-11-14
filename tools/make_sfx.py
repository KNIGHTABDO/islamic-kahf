"""Synthesize the chapter SFX track from the cues in src/chapters/chXX.json (written by build.py). No downloads.
Usage: python3 tools/make_sfx.py ch01   ->  public/ch01/sfx.wav
Cue = {kind, t (absolute s), db, dur}. dur>0 = bed trimmed to dur with a fade-out; dur 0 = one-shot hit.
Kinds (procedural, ffmpeg lavfi):
  beds : city crowd fire lamp wind steps cave heart rain sea
  hits : whoosh swish boom riser chime
  file:<path>  any real sound file in the project (e.g. file:sfx/door.wav), used as-is.
riser is 2.8 s long: start it 2.8 s before what it leads into (build.py does this for at:"title")."""
import json, os, subprocess, sys
ch = sys.argv[1]; R = 48000; D = 'work/sfx'; os.makedirs(D, exist_ok=True)
c = json.load(open(f'src/chapters/{ch}.json', encoding='utf8'))
def g(*a): subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', *a], check=True)
def L(src): return ['-f', 'lavfi', '-i', src]
def fades(d, fin=0.8, fout=1.2): return f'afade=t=in:d={fin},afade=t=out:st={max(0.1, d - fout):.2f}:d={fout}'

def bed(kind, d, out):
    if kind in ('city', 'crowd'):
        mur = 0.5 if kind == 'city' else 1.0
        g(*L(f'anoisesrc=d={d}:c=brown:a=0.5:s={R}'), *L(f'anoisesrc=d={d}:c=pink:a=0.35:s={R}'), '-filter_complex',
          f'[0]lowpass=f=500,tremolo=f=0.2:d=0.5[w];[1]bandpass=f=550:w=1.2,tremolo=f=5.3:d=0.35,tremolo=f=3.1:d=0.3,volume={mur}[m];[w][m]amix=inputs=2:normalize=0,{fades(d)}', out)
    elif kind in ('fire', 'lamp'):
        g(*L(f"aevalsrc='if(lt(random(0),0.0016),(random(1)-0.5)*1.6,0)':d={d}:s={R}"), *L(f'anoisesrc=d={d}:c=brown:a=0.45:s={R}'), '-filter_complex',
          f'[0]highpass=f=900,aecho=0.6:0.3:12:0.4[c];[1]lowpass=f=260,tremolo=f=1.7:d=0.5,tremolo=f=4.3:d=0.3[r];[c][r]amix=inputs=2:normalize=0,{fades(d, 0.4, 0.8)}', out)
    elif kind == 'wind':
        g(*L(f'anoisesrc=d={d}:c=brown:a=0.6:s={R}'), *L(f'anoisesrc=d={d}:c=pink:a=0.25:s={R}'), '-filter_complex',
          f'[0]lowpass=f=700,tremolo=f=0.17:d=0.7[a];[1]bandpass=f=1300:w=0.4,tremolo=f=0.11:d=0.9,vibrato=f=0.3:d=0.5[b];[a][b]amix=inputs=2:normalize=0,{fades(d, 1.2, 1.5)}', out)
    elif kind == 'steps':
        ev = lambda f0, off, per, amp, n: f"aevalsrc='{amp}*sin(2*PI*{f0}*t)*exp(-38*mod(t+{off},{per}))+{n}*(random(0)*2-1)*exp(-70*mod(t+{off},{per}))':d={d}:s={R}"
        g(*L(ev(85, 0, 0.31, 0.9, 0.5)), *L(ev(95, 0.11, 0.29, 0.8, 0.45)), *L(ev(78, 0.2, 0.33, 0.7, 0.4)), '-filter_complex',
          f'[0][1][2]amix=inputs=3:normalize=0,lowpass=f=2500,aecho=0.7:0.4:45:0.3,{fades(d, 0.5, 1.4)}', out)
    elif kind == 'cave':
        g(*L(f"aevalsrc='0.35*sin(2*PI*55*t)+0.22*sin(2*PI*82.4*t)*(0.6+0.4*sin(2*PI*0.13*t))':d={d}:s={R}"),
          *L(f"aevalsrc='0.6*sin(2*PI*(1300+900*exp(-35*mod(t,1.9)))*mod(t,1.9))*exp(-28*mod(t,1.9))':d={d}:s={R}"), '-filter_complex',
          f'[1]aecho=0.8:0.75:170|390|720:0.45|0.35|0.25,volume=0.5[d];[0][d]amix=inputs=2:normalize=0,{fades(d, 1, 1.2)}', out)
    elif kind == 'heart':
        g(*L(f"aevalsrc='(sin(2*PI*48*t)*exp(-18*mod(t,0.9))+0.7*sin(2*PI*44*(t-0.22))*exp(-18*mod(t-0.22,0.9))*gte(mod(t,0.9),0.22))*0.9':d={d}:s={R}"),
          '-af', f'lowpass=f=180,volume=1.5,{fades(d, 0.6, 0.9)}', out)
    elif kind == 'rain':
        g(*L(f'anoisesrc=d={d}:c=pink:a=0.5:s={R}'), *L(f"aevalsrc='if(lt(random(0),0.004),(random(1)-0.5),0)':d={d}:s={R}"), '-filter_complex',
          f'[0]highpass=f=400,lowpass=f=7000[h];[1]highpass=f=2000[k];[h][k]amix=inputs=2:normalize=0,{fades(d, 1.5, 1.5)}', out)
    elif kind == 'sea':
        g(*L(f'anoisesrc=d={d}:c=brown:a=0.7:s={R}'), *L(f'anoisesrc=d={d}:c=pink:a=0.3:s={R}'), '-filter_complex',
          f'[0]lowpass=f=600,tremolo=f=0.09:d=0.85[a];[1]highpass=f=1500,tremolo=f=0.09:d=0.9[b];[a][b]amix=inputs=2:normalize=0,{fades(d, 2, 2)}', out)
    else: sys.exit(f'unknown bed kind {kind}')

def hit(kind, out):
    if kind == 'whoosh': g(*L(f'anoisesrc=d=0.7:c=pink:a=0.8:s={R}'), '-af', 'bandpass=f=900:w=1.6,afade=t=in:d=0.3:curve=exp,afade=t=out:st=0.35:d=0.35', out)
    elif kind == 'swish': g(*L(f'anoisesrc=d=0.9:c=pink:a=0.7:s={R}'), '-af', 'bandpass=f=2200:w=1.2,afade=t=in:d=0.5:curve=exp,afade=t=out:st=0.5:d=0.4', out)
    elif kind == 'boom':
        g(*L(f"aevalsrc='0.95*sin(2*PI*(52-22*t)*t)*exp(-2.6*t)':d=2.4:s={R}"), *L(f'anoisesrc=d=0.25:c=brown:a=0.7:s={R}'), '-filter_complex',
          '[1]afade=t=out:d=0.25[n];[0][n]amix=inputs=2:normalize=0,aecho=0.8:0.6:90|200:0.35|0.2,alimiter=limit=0.95', out)
    elif kind == 'riser':
        g(*L(f'anoisesrc=d=2.8:c=white:a=0.6:s={R}'), *L(f"aevalsrc='0.3*sin(2*PI*(80+300*t*t/7.84)*t)':d=2.8:s={R}"), '-filter_complex',
          '[0]highpass=f=1800,lowpass=f=9000[n];[n][1]amix=inputs=2:normalize=0,afade=t=in:d=2.75:curve=exp,afade=t=out:st=2.72:d=0.08', out)
    elif kind == 'chime':
        g(*L(f"aevalsrc='0.3*sin(2*PI*1318*t)*exp(-1.6*t)+0.22*sin(2*PI*1975*t)*exp(-2*t)+0.16*sin(2*PI*2637*t)*exp(-2.6*t)':d=4:s={R}"), '-af', 'aecho=0.8:0.6:140|310:0.35|0.25', out)
    else: sys.exit(f'unknown hit kind {kind}')

HITS = {'whoosh', 'swish', 'boom', 'riser', 'chime'}
files = []
for q in c['cues']:
    k, d = q['kind'], float(q.get('dur') or 0)
    if k.startswith('file:'): src = k[5:]
    elif k in HITS: src = f'{D}/{k}.wav'; os.path.exists(src) or hit(k, src)
    else:
        d = max(d, 2.0); src = f'{D}/{k}_{d:.2f}.wav'; os.path.exists(src) or bed(k, round(d + 0.1, 2), src)
    files.append((src, q, d if k not in HITS else 0))
total = c['total']
if not files:
    g(*L(f'anullsrc=r={R}:cl=stereo'), '-t', str(total), f'public/{ch}/sfx.wav'); print('no cues: silent sfx.wav'); sys.exit()
ins, fc = [], ''
for n, (src, q, d) in enumerate(files):
    ins += ['-i', src]; ms = int(round(q['t'] * 1000))
    trim = f'atrim=0:{d},afade=t=out:st={max(0, d - 0.8):.2f}:d=0.8,' if d and q['kind'].startswith('file:') else ''
    fc += f'[{n}]aformat=sample_rates={R}:channel_layouts=stereo,{trim}adelay={ms}|{ms},volume={q["db"]}dB[a{n}];'
fc += ''.join(f'[a{n}]' for n in range(len(files))) + f'amix=inputs={len(files)}:normalize=0:duration=longest,apad=whole_dur={total},atrim=0:{total},alimiter=limit=0.9'
os.makedirs(f'public/{ch}', exist_ok=True)
g(*ins, '-filter_complex', fc, '-ar', str(R), f'public/{ch}/sfx.wav')
print(f'public/{ch}/sfx.wav {total}s, {len(files)} cues')
