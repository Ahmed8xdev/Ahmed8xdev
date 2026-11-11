import fs from 'node:fs/promises';

const username = process.env.GITHUB_USERNAME || 'Ahmed8xdev';
if (!/^[a-z0-9-]{1,39}$/i.test(username)) throw new Error('Invalid GitHub username');
const token = process.env.GH_TOKEN || '';
const START = '<!-- AUTO-PROJECTS:START -->';
const END = '<!-- AUTO-PROJECTS:END -->';

const editorial = {
  'barber-shop': { icon: '💈', brief: 'A Next.js front end with a 3D- and motion-capable visual stack.', stack: ['Next.js', 'React', 'TypeScript', 'Three.js', 'GSAP'] },
  studio: { icon: '✦', brief: 'A Next.js application codebase integrating Firebase, Genkit and a substantial UI component system.', stack: ['Next.js', 'TypeScript', 'Firebase', 'Genkit'] },
  toolshub: { icon: '🛠️', brief: 'An agent utility dashboard with documentation and delay tools and a Three.js visual background.', stack: ['HTML', 'JavaScript', 'Tailwind CSS', 'Three.js'] }
};

function clean(v, max = 220) {
  return String(v == null ? '' : v).replace(/[\x00-\x1f\x7f]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, max);
}
function escapeHTML(v) {
  return clean(v, 360).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}
function escapeMD(v) {
  return clean(v, 360).replace(/([\\\`*_{}\[\]()#+.!|<>])/g, '\\$1');
}
async function github(endpoint) {
  const res = await fetch('https://api.github.com' + endpoint, {
    headers: {
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'Ahmed8xdev-public-repository-discovery',
      ...(token ? { Authorization: 'Bearer ' + token } : {})
    },
    signal: AbortSignal.timeout(20000)
  });
  if (!res.ok) throw new Error('GitHub API status ' + res.status + ' for ' + endpoint);
  return res.json();
}

const all = [];
for (let page = 1; page <= 20; page++) {
  const next = await github('/users/' + encodeURIComponent(username) + '/repos?type=owner&per_page=100&page=' + page + '&sort=updated');
  if (!Array.isArray(next)) throw new Error('Unexpected repositories response');
  all.push(...next);
  if (next.length < 100) break;
}
const repos = all.filter(r => r && !r.private && !r.fork && !r.archived && r.name.toLowerCase() !== username.toLowerCase());
repos.sort((a, b) => (b.stargazers_count || 0) - (a.stargazers_count || 0) || Date.parse(b.pushed_at || b.updated_at || 0) - Date.parse(a.pushed_at || a.updated_at || 0));

const projects = [];
for (const repo of repos) {
  let languages = [];
  try {
    const data = await github('/repos/' + encodeURIComponent(username) + '/' + encodeURIComponent(repo.name) + '/languages');
    languages = Object.entries(data).sort((a, b) => b[1] - a[1]).slice(0, 5).map(p => p[0]);
  } catch (e) { console.warn('Languages unavailable for ' + repo.name + ': ' + e.message); }
  const known = editorial[repo.name];
  projects.push({
    name: repo.name,
    url: 'https://github.com/' + encodeURIComponent(username) + '/' + encodeURIComponent(repo.name),
    description: clean(repo.description, 220) || (known ? known.brief : 'Explore the public source code and project files.'),
    editorialBrief: known ? known.brief : null,
    stackHints: known ? known.stack : [],
    languages,
    topics: (repo.topics || []).filter(x => typeof x === 'string').slice(0, 8),
    stars: repo.stargazers_count || 0,
    forks: repo.forks_count || 0,
    lastPushed: repo.pushed_at || null
  });
}
const featured = [...['barber-shop', 'studio', 'toolshub'].map(n => projects.find(p => p.name === n)).filter(Boolean),
  ...projects.filter(p => !['barber-shop', 'studio', 'toolshub'].includes(p.name))].slice(0, 6);

const cells = featured.map(p => {
  const known = editorial[p.name];
  const tags = [...new Set([...p.stackHints, ...p.languages])].slice(0, 5);
  return '<td width="50%" valign="top"><a href="' + escapeHTML(p.url) + '"><strong>' + (known ? known.icon : '📦') + ' ' + escapeHTML(p.name) + '</strong></a><br/><br/>' + escapeHTML(p.editorialBrief || p.description) + '<br/><br/><sub>' + escapeHTML(tags.join(' · ') || 'Public GitHub repository') + '</sub></td>';
});
if (cells.length % 2) cells.push('<td width="50%" valign="top"><strong>Explore more projects</strong><br/><br/><a href="https://github.com/' + encodeURIComponent(username) + '?tab=repositories">All public repositories</a></td>');
const rows = [];
for (let i = 0; i < cells.length; i += 2) rows.push('<tr>\n' + cells.slice(i, i + 2).join('\n') + '\n</tr>');
const table = '<table>\n' + (rows.join('\n') || '<tr><td>No public projects have been detected yet.</td></tr>') + '\n</table>';

const original = await fs.readFile('README.md', 'utf8');
const start = original.indexOf(START);
const end = original.indexOf(END);
if (start < 0 || end <= start || original.indexOf(START, start + START.length) >= 0 || original.indexOf(END, end + END.length) >= 0)
  throw new Error('README markers are missing or duplicated. No changes made.');
const updated = original.slice(0, start + START.length) + '\n' + table + '\n' + original.slice(end);
if (updated !== original) await fs.writeFile('README.md', updated, 'utf8');

const doc = [
  '# Public project index', '',
  'Automatically discovered from public, non-fork repositories belonging to [' + escapeMD(username) + '](https://github.com/' + encodeURIComponent(username) + ').',
  'Project descriptions are based on observed files or public metadata; no private code or invented outcomes are included.', '',
  '**Public projects detected:** ' + projects.length, ''
];
for (const p of projects) {
  doc.push('## [' + escapeMD(p.name) + '](' + p.url + ')', '', '**Brief:** ' + escapeMD(p.editorialBrief || p.description), '',
    '**Languages:** ' + (p.languages.map(escapeMD).join(', ') || 'Not available'));
  if (p.stackHints.length) doc.push('**Technologies observed in files or packages:** ' + p.stackHints.map(escapeMD).join(', '));
  if (p.topics.length) doc.push('**Topics:** ' + p.topics.map(escapeMD).join(', '));
  doc.push('**Stars / forks:** ' + p.stars + ' / ' + p.forks,
    '**Last pushed:** ' + (p.lastPushed ? p.lastPushed.slice(0, 10) : 'Unknown'), '');
}
await fs.writeFile('PROJECTS.md', doc.join('\n') + '\n', 'utf8');
await fs.mkdir('data', { recursive: true });
await fs.writeFile('data/public-repositories.json', JSON.stringify({
  username, scannedAt: new Date().toISOString(), publicRepoCount: projects.length, projects
}, null, 2) + '\n');
console.log('Scanned ' + projects.length + ' public repositories; featured ' + featured.length + '.');
