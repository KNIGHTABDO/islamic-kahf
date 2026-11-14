#!/usr/bin/env bash
# Fable's light studio chain. Usage: studio.sh in.wav out.wav  -> 48k/24-bit, voice stem ~-16 LUFS
in=$1; out=$2
CH="aresample=48000:resampler=soxr:precision=28,highpass=f=70:poles=2,equalizer=f=110:t=q:w=0.9:g=1.5,equalizer=f=300:t=q:w=1.2:g=-2,equalizer=f=3800:t=q:w=0.9:g=2.5,highshelf=f=8500:g=2,acompressor=threshold=-22dB:ratio=2.5:attack=15:release=160:knee=6:makeup=1"
# measure, then set static gain to hit -16 LUFS before the limiter
L=$(ffmpeg -nostats -i "$in" -af "$CH,ebur128" -f null - 2>&1 | grep -E '^\s+I:' | tail -1 | awk '{print $2}')
G=$(python3 -c "print(round(-16.0-($L),2))")
ffmpeg -v error -y -i "$in" -af "$CH,volume=${G}dB,alimiter=limit=0.79:attack=3:release=40:level=false" -ar 48000 -c:a pcm_s24le "$out"
echo "$out gain=$G $(ffmpeg -nostats -i "$out" -af ebur128 -f null - 2>&1 | grep -E '^\s+(I|LRA):' | tail -2 | tr -s ' ' | tr '\n' ' ')"
