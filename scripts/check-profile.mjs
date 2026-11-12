import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

export function localReferences(text) {
  const refs = [];
  for (const match of text.matchAll(/!\[[^\]]*\]\(([^)]+)\)|(?<!!)\[[^\]]+\]\(([^)]+)\)|\b(?:src|href)\s*=\s*["']([^"']+)["']/g)) {
    const candidate = (match[1] || match[2] || match[3] || '').trim().replace(/\s+["'][^"']+["']$/, '');
    if (!candidate || /^(?:https?:|mailto:|tel:|data:|#|javascript:)/i.test(candidate)) continue;
    refs.push(candidate.split(/[?#]/)[0]);
  }
  return [...new Set(refs)];
}

export async function missingLocalReferences(root, sourceFile, text) {
  const misses = [];
  for (const ref of localReferences(text)) {
    let decoded;
    try { decoded = decodeURIComponent(ref); }
    catch { misses.push({ ref, reason: 'invalid URI encoding' }); continue; }
    const relative = decoded.startsWith('/') ? decoded.slice(1) : decoded;
    const destination = path.resolve(root, path.dirname(sourceFile), relative);
    if (destination !== root && !destination.startsWith(root + path.sep)) {
      misses.push({ ref, reason: 'path escapes repository root' });
      continue;
    }
    try {
      const file = await fs.stat(destination);
      if (!file.isFile()) misses.push({ ref, reason: 'not a file' });
    } catch {
      misses.push({ ref, reason: 'not found' });
    }
  }
  return misses;
}

export function markersValid(readme) {
  const start = '<!-- AUTO-PROJECTS:START -->';
  const end = '<!-- AUTO-PROJECTS:END -->';
  return readme.split(start).length === 2 &&
    readme.split(end).length === 2 &&
    readme.indexOf(start) < readme.indexOf(end);
}

export async function checkProfile(root = projectRoot) {
  const issues = [];
  const read = name => fs.readFile(path.join(root, name), 'utf8');
  const readme = await read('README.md');
  const index = await read('docs/index.html');
  const hero = await read('assets/hero.svg');

  if (!markersValid(readme)) issues.push('Automated project section markers must appear exactly once and in order.');
  if (!readme.includes('<!-- MUSIC FLOW FOOTER START -->') || !readme.includes('<!-- MUSIC FLOW FOOTER END -->'))
    issues.push('The music flow footer markers are missing.');
  if (!readme.includes('profile-3d-contrib/profile-night-rainbow.svg'))
    issues.push('The real GitHub contribution visualization is not linked.');
  const visibleHeader = [...hero.matchAll(/<text\b[^>]*>([^<]*)<\/text>/g)].map(match => match[1].trim());
  if (JSON.stringify(visibleHeader) !== JSON.stringify(['AHMED', 'Software Engineer']))
    issues.push('The hero must display only AHMED and Software Engineer.');

  for (const [name, content] of [['README.md', readme], ['docs/index.html', index]]) {
    for (const error of await missingLocalReferences(root, name, content))
      issues.push(name + ': ' + error.ref + ' (' + error.reason + ')');
  }

  const data = JSON.parse(await read('data/public-repositories.json'));
  if (!Array.isArray(data.projects) || data.projects.some(project => project.private === true))
    issues.push('Public repository metadata is missing or contains private entries.');
  if (!index.includes('application/ld+json') || !index.includes('rel="canonical"'))
    issues.push('The interactive site is missing semantic metadata.');
  const gif = await fs.readFile(path.join(root, 'assets/footer-music-coding.gif'));
  if (!(gif.subarray(0, 6).toString('ascii') === 'GIF89a' || gif.subarray(0, 6).toString('ascii') === 'GIF87a'))
    issues.push('The music footer asset is not a valid GIF.');

  return issues;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  checkProfile().then(issues => {
    if (issues.length) {
      console.error('Profile integrity issues:\n' + issues.map(v => '  - ' + v).join('\n'));
      process.exitCode = 1;
    } else console.log('Profile integrity checks passed.');
  }).catch(error => { console.error(error); process.exitCode = 1; });
}
