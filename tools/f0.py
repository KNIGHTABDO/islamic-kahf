# Median/percentile F0 of voiced frames via autocorrelation. Usage: python3 f0.py a.wav [b.wav ...]
import sys, subprocess, numpy as np
R = 16000
for p in sys.argv[1:]:
    raw = subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','1','-ar',str(R),'-f','f32le','-'],capture_output=True).stdout
    x = np.frombuffer(raw, np.float32); n = 640; hop = 160; f0 = []
    lo, hi = R//300, R//65
    for i in range(0, len(x)-n, hop):
        fr = x[i:i+n] - x[i:i+n].mean()
        if np.sqrt((fr**2).mean()) < 0.02: continue
        ac = np.correlate(fr, fr, 'full')[n-1:]
        if ac[0] <= 0: continue
        ac = ac / ac[0]; k = lo + np.argmax(ac[lo:hi])
        if ac[k] > 0.45: f0.append(R / k)
    f = np.array(f0)
    print(f"{p.split('/')[-1]:14s} median {np.median(f):6.1f} Hz  p10 {np.percentile(f,10):6.1f}  p90 {np.percentile(f,90):6.1f}  voiced {len(f)}")
