// Usage: node tools/frames.mjs <compId>  -> prints the frame count Remotion will use (same rule as src/Root.tsx).
import fs from 'node:fs';
const id = process.argv[2];
const ceil = (s) => Math.ceil(s * 30);
if (id.startsWith('short-')) {
  const s = JSON.parse(fs.readFileSync('src/shorts.json', 'utf8')).find((x) => 'short-' + x.id === id);
  if (!s) throw new Error('no short ' + id);
  console.log(ceil(s.to - s.from));
} else {
  const c = JSON.parse(fs.readFileSync(`src/chapters/${id}.json`, 'utf8'));
  console.log(ceil(c.total));
}
