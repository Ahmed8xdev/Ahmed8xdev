import { readFile, mkdtemp, writeFile, rm } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import path from 'node:path';

const source = await readFile(new URL('../docs/index.html', import.meta.url), 'utf8');
const scripts = [...source.matchAll(/<script\s+type="module"[^>]*>([\s\S]*?)<\/script>/g)];
if (scripts.length !== 1) throw new Error('Expected exactly one ES module in the interactive 3D page');

const required = [
  ['technology selector', /<select\b[^>]*id="scene-technology"[^>]*>/],
  ['accessible label', /<label\b[^>]*for="scene-technology"[^>]*>/],
  ['technology change handler', /technologyPicker\.addEventListener\('change'/],
  ['mouse selection synchronization', /chooseTechnology\(topics\.indexOf\(selection\.topic\)\)/],
  ['keyboard accessible canvas', /<canvas\b[^>]*tabindex="0"/],
  ['screen reader announcements', /aria-live="polite"/],
  ['reduced motion support', /prefers-reduced-motion:\s*reduce/],
  ['offscreen GPU pause', /!sceneInViewport/],
];
for (const [name, expression] of required) {
  if (!expression.test(source)) throw new Error('Missing interactive viewer feature: ' + name);
}
const temp = await mkdtemp(path.join(tmpdir(), '3d-scene-check-'));
try {
  const scriptPath = path.join(temp, 'viewer.mjs');
  await writeFile(scriptPath, scripts[0][1], 'utf8');
  execFileSync(process.execPath, ['--check', scriptPath], { stdio: 'pipe' });
  console.log('3D viewer passed script syntax and accessibility checks.');
} finally {
  await rm(temp, { recursive: true, force: true });
}
