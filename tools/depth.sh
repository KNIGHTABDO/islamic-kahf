#!/usr/bin/env bash
# Depth maps for parallax shots (AI Studio nano-banana through kapi). Usage: bash tools/depth.sh public/ch01/k3.png [more.png ...]
# Writes public/ch01/d_k3.png (1920x1080 gray, blurred). Skips stills that already have one. 3 tries each.
KAPI=~/Desktop/projects/knight-api/target/debug/kapi
P="Convert this image into a monocular depth map: grayscale only, pure white = nearest to the camera, black = farthest (sky). Smooth gradients, sharp edges at object boundaries, same framing and aspect ratio 16:9, no text, no color."
for img in "$@"; do
  img=$(realpath "$img"); dir=$(dirname "$img"); name=$(basename "$img" .png); out="$dir/d_$name.png"
  [ -f "$out" ] && { echo "skip $out"; continue; }
  for try in 1 2 3; do
    w="$PWD/work/depth/${name}_$try"; mkdir -p "$w"
    "$KAPI" gen --model gemini-nano-banana-2.1 --file "$img" --out "$w" --wait-s 180 --request-id "depth-$(basename "$PWD")-$name-$(md5sum "$img" | cut -c1-8)-$try" "$P Reference $name." 2>&1 | head -1 | grep -oE '"status":"[a-z]+"' 
    f=$(find "$w" -type f \( -name '*.png' -o -name '*.jpg' -o -name '*.webp' \) | head -1)
    if [ -n "$f" ]; then ffmpeg -v error -y -i "$f" -vf "scale=1920:1080,format=gray,gblur=sigma=3" "$out" && echo "ok $out" && break; fi
    echo "retry $name ($try)"; sleep 4
  done
done
