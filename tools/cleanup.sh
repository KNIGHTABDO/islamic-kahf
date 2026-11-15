#!/usr/bin/env bash
# Free local storage once a chapter is live on YouTube.
# Usage: bash tools/cleanup.sh            (dry run: lists what would go and how much)
#        bash tools/cleanup.sh --yes      (deletes)
#
# Deletes only local, untracked working data: TTS takes, intermediates, local downloads, node_modules and
# big wavs. Keeps everything committed to GitHub (script, plan, src, tools, public images and mp3s), plus the
# small decision files (audio/*/picks.json, trims.json, anchors/), so any chapter can still be re-rendered
# on GitHub. The final 4K stays as the `chXX-final` artifact on the render run (30 days) and on YouTube.
set -euo pipefail
cd "$(dirname "$0")/.."
YES=${1:-}
git diff --quiet && git diff --cached --quiet || { echo "Uncommitted changes: commit and push first."; exit 1; }
[ -z "$(git log --branches --not --remotes --oneline)" ] || { echo "Unpushed commits: push first."; exit 1; }

targets=(work out sfx_parts node_modules sources/quran/audio)
for f in public/*/narration.wav public/*/music.wav public/*/sfx.wav; do [ -e "$f" ] && targets+=("$f"); done
# TTS takes and raw audio, but keep the small decision files
while IFS= read -r f; do targets+=("$f"); done < <(find audio -type f \( -name '*.wav' -o -name '*.mp3' \) 2>/dev/null)

total=0
for t in "${targets[@]}"; do
  [ -e "$t" ] || continue
  kb=$(du -sk "$t" | cut -f1); total=$((total + kb))
done
echo "Would free $((total / 1024)) MB:"
for t in work out sfx_parts node_modules sources/quran/audio; do if [ -e "$t" ]; then echo "  $t"; fi; done; echo "  audio/*/ wav+mp3 takes (json kept), public/*/*.wav"

if [ "$YES" = "--yes" ]; then
  for t in "${targets[@]}"; do if [ -e "$t" ]; then rm -rf -- "$t"; fi; done
  echo "Done. Run 'npm install' before working on this project again."
else
  echo "Dry run. Rerun with --yes to delete."
fi
