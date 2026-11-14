#!/usr/bin/env bash
# Upscale a Flow 360p/720p clip to 1080p30 for Remotion (muted). Usage: bash tools/prep_clip.sh in.mp4 public/ch01/name.mp4
ffmpeg -v error -y -i "$1" -an -vf "scale=1920:1080:flags=lanczos,unsharp=5:5:0.6,fps=30" -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p "$2" && \
  echo "$2 $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$2")s"
