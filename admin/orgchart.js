// Agent org chart for the Growth Studio Agents view.
// Layout follows a live org chart: operator -> Chief of Staff -> teams -> specialists.
// Nodes glow and particles move only for real run activity: running tasks dispatch from the
// Chief of Staff, tasks finished in the last 7 days send results back. Nothing animates for show.

const C = {
  bg: '#0B0E1A', star: 'rgba(170,180,255,', edge: 'rgba(140,150,225,', text: '#E6E8F5', muted: '#8A90B0',
  operator: '#F2F3FA', chief: '#6E8BFF', team: '#A78BFA', agent: '#8FB4FF', run: '#6E8BFF', done: '#C4B5FD', fail: '#FF6B5B',
};
const WEEK = 7 * 864e5;
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
let live = null;

export function mountOrgChart(host, opts) {
  if (live) live.destroy();
  live = new OrgChart(host, opts);
  return live;
}

class OrgChart {
  constructor(host, { agents, runs, departments = [], workflows = [], selectedId, rootId = 'chief-of-staff', esc }) {
    this.host = host; this.esc = esc; this.agents = agents; this.selectedId = selectedId;
    this.byId = new Map(agents.map(a => [a.id, a]));
    this.root = this.byId.get(rootId) || agents.find(a => !a.dependsOn.length) || agents[0];
    this.status = activity(runs);
    this.hover = null; this.pinned = null; this.particles = []; this.t0 = performance.now();

    const rootGroup = this.root.group;
    const order = [...new Set(agents.map(a => a.group))].filter(g => g !== rootGroup);
    const dept = new Set(departments);
    this.studio = order.filter(g => !dept.has(g));
    this.depts = order.filter(g => dept.has(g));
    this.teams = order.map(g => ({ name: g, members: agents.filter(a => a.group === g) }));
    this.satellites = agents.filter(a => a.group === rootGroup && a.id !== this.root.id);

    host.innerHTML = `<div class="oc-panel"><canvas class="oc-canvas" aria-label="Agent org chart. Use the team list below to browse agents."></canvas>
      <div class="oc-legend" aria-hidden="true"><span><i style="background:${C.run}"></i>dispatch · running</span><span><i style="background:${C.done}"></i>results · last 7 days</span><span><i style="background:${C.fail}"></i>needs attention</span></div>
      <aside class="oc-card" aria-live="polite"></aside></div>
      <div class="oc-stats">${[[1, 'operator'], [1, 'chief of staff'], [this.teams.length, 'teams'], [agents.length, 'agents'],
        [[...this.status.values()].filter(s => s === 'running').length, 'running now'],
        [runs.filter(r => Date.parse(r.createdAt) > Date.now() - WEEK).length, 'runs this week']]
        .map(([n, l]) => `<div><b>${n}</b><span>${l}</span></div>`).join('')}</div>
      <p class="oc-label">Teams</p>
      <div class="oc-pills">${this.teams.map(t => `<button type="button" data-oc-team="${esc(t.name)}">${esc(t.name)}<small>${t.members.length}</small></button>`).join('')}</div>
      ${workflows.length ? `<p class="oc-label">Workflows</p><div class="oc-pills">${workflows.map(w => `<button type="button" data-workflow="${esc(w)}">${esc(w)}</button>`).join('')}</div>` : ''}`;
    host.querySelectorAll('[data-oc-team]').forEach(b => b.addEventListener('click', () => {
      this.pinned = this.nodes.find(n => n.kind === 'team' && n.name === b.dataset.ocTeam); this.showCard();
      this.panel.scrollIntoView({ block: 'nearest', behavior: REDUCED ? 'auto' : 'smooth' });
    }));
    this.panel = host.querySelector('.oc-panel');
    this.canvas = host.querySelector('canvas');
    this.card = host.querySelector('.oc-card');
    this.ctx = this.canvas.getContext('2d');

    this.onMove = e => { const n = this.hit(e); if (n !== this.hover) { this.hover = n; this.canvas.style.cursor = n ? 'pointer' : 'default'; this.showCard(); } };
    this.onLeave = () => { this.hover = null; this.showCard(); };
    this.onClick = e => {
      const n = this.hit(e); if (!n) { this.pinned = null; this.showCard(); return; }
      if (n.kind === 'agent' || n.kind === 'chief' || n.kind === 'sat') { this.host.dispatchEvent(new CustomEvent('oc-select', { bubbles: true, detail: n.id })); return; }
      this.pinned = n; this.showCard();
    };
    this.canvas.addEventListener('pointermove', this.onMove);
    this.canvas.addEventListener('pointerleave', this.onLeave);
    this.canvas.addEventListener('click', this.onClick);
    this.ro = new ResizeObserver(() => this.layout()); this.ro.observe(this.panel);
    this.layout();
    const sel = this.byId.get(selectedId);
    this.pinned = sel && sel.id !== this.root.id ? this.nodes.find(n => n.kind === 'team' && n.name === sel.group) : null;
    this.showCard();
    this.frame = requestAnimationFrame(t => this.tick(t));
  }

  destroy() { cancelAnimationFrame(this.frame); this.ro.disconnect(); }

  layout() {
    const W = this.panel.clientWidth, mobile = W < 680;
    const H = mobile ? 760 : 760;
    const dpr = Math.min(devicePixelRatio || 1, 2);
    this.W = W; this.H = H; this.mobile = mobile;
    this.canvas.width = W * dpr; this.canvas.height = H * dpr;
    this.canvas.style.height = H + 'px';
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const nodes = [];
    const op = { kind: 'operator', id: 'operator', name: 'Operator', x: W * 0.5, y: H * 0.05, r: 6 };
    const chief = { kind: 'chief', id: this.root.id, name: this.root.name, x: W * 0.5, y: H * (mobile ? 0.15 : 0.17), r: 13 };
    nodes.push(op, chief);
    this.satellites.forEach((a, i) => nodes.push({ kind: 'sat', id: a.id, name: a.name, x: W * (mobile ? [0.2, 0.8][i % 2] : 0.5 - 0.17 - i * 0.1), y: H * (mobile ? 0.12 : 0.11 + i * 0.06), r: 5 }));

    const rows = mobile ? chunk([...this.studio, ...this.depts], 4) : [this.studio, ...chunk(this.depts, Math.ceil(this.depts.length / 2))];
    const top = mobile ? 0.29 : 0.46, bottom = mobile ? 0.9 : 0.84;
    rows.forEach((row, ri) => {
      const y = H * (rows.length > 1 ? top + (bottom - top) * ri / (rows.length - 1) : top);
      row.forEach((g, i) => {
        const x = W * ((i + 0.5) / row.length) * (mobile ? 1 : 0.94) + (mobile ? 0 : W * 0.03);
        const team = { kind: 'team', id: 'team:' + g, name: g, x, y, r: 7, row: ri, studio: this.studio.includes(g) };
        nodes.push(team);
        const members = this.teams.find(t => t.name === g).members;
        members.forEach((a, k) => {
          const span = Math.min(Math.PI * 0.9, 0.32 * members.length), ang = Math.PI / 2 + (members.length > 1 ? -span / 2 + span * k / (members.length - 1) : 0);
          nodes.push({ kind: 'agent', id: a.id, name: a.name, team, ang, x, y, r: 3.2 });
        });
      });
    });
    this.rowLabels = mobile ? [] : [{ y: H * top, text: 'STUDIO' }, { y: H * (top + (bottom - top) / (rows.length - 1)), text: 'MARKETING DEPARTMENTS' }];
    this.nodes = nodes;
    this.stars = Array.from({ length: Math.round(W * H / 5200) }, (_, i) => ({ x: rand(i * 3) * W, y: rand(i * 3 + 1) * H, a: 0.08 + rand(i * 3 + 2) * 0.22 }));
  }

  node(id) { return this.nodes.find(n => n.id === id); }

  // Leaf positions fan out under their team, and spread wider when that team is the focus.
  place(t) {
    const focus = this.focusTeam();
    for (const n of this.nodes) if (n.kind === 'agent') {
      const open = n.team === focus, target = open ? (this.mobile ? 30 : 46) : (this.mobile ? 16 : 22);
      n.rad = n.rad == null ? target : n.rad + (target - n.rad) * 0.15;
      n.x = n.team.x + Math.cos(n.ang) * n.rad; n.y = n.team.y + Math.sin(n.ang) * n.rad;
    }
  }

  focusTeam() {
    const f = this.hover || this.pinned;
    if (!f) { const s = this.node(this.selectedId); return s && s.kind === 'agent' ? s.team : null; }
    return f.kind === 'team' ? f : f.kind === 'agent' ? f.team : null;
  }

  hit(e) {
    const b = this.canvas.getBoundingClientRect(), x = e.clientX - b.left, y = e.clientY - b.top;
    let best = null, bd = 1e9;
    for (const n of this.nodes) { const d = Math.hypot(n.x - x, n.y - y), lim = n.r + (n.kind === 'agent' ? 6 : 12); if (d < lim && d < bd) { best = n; bd = d; } }
    return best;
  }

  tick(now) {
    const ctx = this.ctx, W = this.W, H = this.H, t = (now - this.t0) / 1000;
    this.place(t);
    ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
    for (const s of this.stars) { ctx.fillStyle = C.star + s.a + ')'; ctx.fillRect(s.x, s.y, 1.2, 1.2); }
    ctx.font = '700 10px "JetBrains Mono", ui-monospace, monospace'; ctx.fillStyle = 'rgba(138,144,176,.55)'; ctx.textAlign = 'left';
    for (const r of this.rowLabels) ctx.fillText(r.text, 14, r.y - 34);

    const op = this.node('operator'), chief = this.node(this.root.id), focus = this.focusTeam();
    line(ctx, op, chief, C.edge + '.5)', 1);
    for (const n of this.nodes) {
      if (n.kind === 'sat') line(ctx, chief, n, C.edge + '.35)', 1);
      if (n.kind === 'team') line(ctx, chief, n, C.edge + (focus === n ? '.6)' : '.16)'), focus === n ? 1.4 : 1);
      if (n.kind === 'agent') line(ctx, n.team, n, C.edge + (focus === n.team ? '.45)' : '.14)'), 1);
    }
    this.drawDeps(ctx);

    if (!REDUCED) this.flow(now);
    for (const p of this.particles) { ctx.fillStyle = p.color; ctx.globalAlpha = p.alpha; ctx.beginPath(); ctx.arc(p.x, p.y, 1.8, 0, 7); ctx.fill(); }
    ctx.globalAlpha = 1;

    for (const n of this.nodes) this.drawNode(ctx, n, t, focus);
    this.frame = requestAnimationFrame(x => this.tick(x));
  }

  drawDeps(ctx) {
    const sel = this.byId.get(this.selectedId); if (!sel) return;
    const me = this.node(sel.id); if (!me) return;
    const curve = (a, b, color) => { ctx.strokeStyle = color; ctx.lineWidth = 1.3; ctx.beginPath(); ctx.moveTo(a.x, a.y); const mx = (a.x + b.x) / 2, my = Math.min(a.y, b.y) - 40; ctx.quadraticCurveTo(mx, my, b.x, b.y); ctx.stroke(); };
    for (const dep of sel.dependsOn) { const d = this.node(dep); if (d) curve(d, me, 'rgba(110,139,255,.75)'); }
    for (const a of this.agents) if (a.dependsOn.includes(sel.id)) { const d = this.node(a.id); if (d) curve(me, d, 'rgba(196,181,253,.6)'); }
  }

  drawNode(ctx, n, t, focus) {
    const st = this.status.get(n.id), sel = n.id === this.selectedId, hov = n === this.hover;
    const base = n.kind === 'operator' ? C.operator : n.kind === 'chief' ? C.chief : n.kind === 'team' ? C.team : n.kind === 'sat' ? C.chief : C.agent;
    const color = st === 'failed' ? C.fail : base;
    const lit = st === 'running' || st === 'done' || n.kind === 'chief' || sel || hov || (n.kind === 'team' && (focus === n || this.teamLit(n)));
    const breathe = REDUCED ? 1 : 1 + Math.sin(t * 2 + n.x * 0.01) * 0.08;
    if (lit || n.kind !== 'agent') glow(ctx, n.x, n.y, n.r * (n.kind === 'chief' ? 4 : 3) * breathe, color, n.kind === 'chief' ? 0.45 : lit ? 0.35 : 0.12);
    ctx.globalAlpha = n.kind === 'agent' && !lit && focus !== n.team ? 0.45 : 1;
    if (n.kind === 'agent') { ctx.fillStyle = color; ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, 7); ctx.fill(); }
    else {
      ctx.strokeStyle = color; ctx.lineWidth = n.kind === 'chief' ? 2.5 : 1.8; ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, 7); ctx.stroke();
      ctx.fillStyle = color; ctx.beginPath(); ctx.arc(n.x, n.y, n.r * 0.45, 0, 7); ctx.fill();
    }
    if (st === 'running' && !REDUCED) { ctx.strokeStyle = C.run; ctx.globalAlpha = 0.6 * (1 - (t % 1.6) / 1.6); ctx.beginPath(); ctx.arc(n.x, n.y, n.r + 3 + (t % 1.6) * 8, 0, 7); ctx.stroke(); }
    ctx.globalAlpha = 1;
    if (sel) { ctx.strokeStyle = '#FFFFFF'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(n.x, n.y, n.r + 4, 0, 7); ctx.stroke(); }

    if (n.kind === 'agent' && !(hov || sel)) return;
    const big = n.kind === 'chief', size = big ? 12 : n.kind === 'agent' ? 11 : this.mobile ? 9.5 : 10.5;
    ctx.font = `${big ? 800 : 600} ${size}px "Funnel Sans", ui-sans-serif, system-ui, sans-serif`;
    ctx.fillStyle = n.kind === 'team' ? C.text : n.kind === 'agent' ? '#FFFFFF' : C.text; ctx.textAlign = 'center';
    const label = n.kind === 'chief' || n.kind === 'operator' ? n.name.toUpperCase() : n.name;
    const lines = n.kind === 'team' && this.mobile ? wrap(label, 11) : [label];
    const above = n.kind === 'team' || n.kind === 'chief' || n.kind === 'operator' || n.kind === 'sat';
    lines.forEach((l, i) => ctx.fillText(l, n.x, above ? n.y - n.r - 8 - (lines.length - 1 - i) * 11 : n.y + n.r + 14 + i * 11));
  }

  teamLit(team) { return this.teams.find(x => x.name === team.name).members.some(a => this.status.has(a.id)); }

  flow(now) {
    const chief = this.node(this.root.id);
    for (const [id, st] of this.status) {
      const n = this.node(id); if (!n || n === chief) continue;
      const path = n.kind === 'agent' ? [chief, n.team, n] : [chief, n];
      const rate = st === 'running' ? 0.05 : st === 'done' ? 0.006 : 0;
      if (Math.random() < rate) this.particles.push({ path: st === 'done' ? [...path].reverse() : path, k: 0, color: st === 'done' ? C.done : C.run, alpha: 0.95 });
    }
    for (const p of this.particles) {
      p.k += 0.012; const seg = Math.min(p.path.length - 2, Math.floor(p.k * (p.path.length - 1))), f = p.k * (p.path.length - 1) - seg;
      const a = p.path[seg], b = p.path[seg + 1]; p.x = a.x + (b.x - a.x) * f; p.y = a.y + (b.y - a.y) * f; p.alpha = p.k > 0.85 ? (1 - p.k) / 0.15 : 0.95;
    }
    this.particles = this.particles.filter(p => p.k < 1).slice(-160);
  }

  showCard() {
    const n = this.hover || this.pinned || this.node(this.root.id), e = this.esc;
    const a = this.byId.get(n.id), st = id => this.status.get(id);
    const dot = id => { const s = st(id); return s ? `<i class="oc-dot ${s}" title="${s === 'done' ? 'finished in the last 7 days' : s}"></i>` : '<i class="oc-dot"></i>'; };
    let html;
    if (n.kind === 'team') {
      const m = this.teams.find(t => t.name === n.name).members;
      html = `<p class="oc-eyebrow">${n.studio ? 'Studio team' : 'Marketing department'} · ${m.length} specialist${m.length > 1 ? 's' : ''}</p><h3>${e(n.name)}</h3>
        <ul class="oc-list">${m.map(x => `<li><button data-agent="${e(x.id)}">${dot(x.id)}${e(x.name)}</button></li>`).join('')}</ul>`;
    } else if (n.kind === 'operator') {
      html = `<p class="oc-eyebrow">Operator · human sign-off</p><h3>You</h3><p>Every job starts with you and comes back to you. No agent publishes, posts or spends without your approval.</p>`;
    } else {
      const out = this.agents.filter(x => x.dependsOn.includes(a.id));
      const ins = a.dependsOn.map(id => this.byId.get(id)?.name || id);
      const about = String(a.prompt || '').replace(/\s+/g, ' ').trim().split(/(?<=\.)\s/).slice(0, 2).join(' ').slice(0, 260);
      html = `<p class="oc-eyebrow">${n.kind === 'chief' ? 'Chief of Staff · the single front door' : e(a.group)} · v${a.version}</p><h3>${e(a.name)}</h3>
        ${about ? `<p>${e(about)}</p>` : ''}
        <p class="oc-meta"><b>Receives from</b> ${e(ins.join(', ') || 'operator job and product context')}</p>
        <p class="oc-meta"><b>Feeds into</b> ${out.length ? e(out.map(x => x.name).slice(0, 8).join(', ')) + (out.length > 8 ? ` +${out.length - 8}` : '') : 'final review'}</p>
        <button class="oc-open" data-agent="${e(a.id)}">Open in inspector</button>`;
    }
    this.card.innerHTML = html;
  }
}

function activity(runs) {
  const m = new Map(), cutoff = Date.now() - WEEK;
  for (const r of runs) for (const t of r.tasks || []) {
    const when = Date.parse(t.completedAt || t.startedAt || r.updatedAt || r.createdAt || 0);
    if (t.status === 'running' || t.status === 'queued' && r.status === 'running') m.set(t.id, 'running');
    else if ((t.status === 'failed' || t.status === 'needs_attention') && when > cutoff && m.get(t.id) !== 'running') m.set(t.id, 'failed');
    else if (t.status === 'done' && when > cutoff && !m.has(t.id)) m.set(t.id, 'done');
  }
  return m;
}

function line(ctx, a, b, color, w) { ctx.strokeStyle = color; ctx.lineWidth = w; ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke(); }
function glow(ctx, x, y, r, color, a) { const g = ctx.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, hexA(color, a)); g.addColorStop(1, hexA(color, 0)); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fill(); }
function hexA(h, a) { const n = parseInt(h.slice(1), 16); return `rgba(${n >> 16},${n >> 8 & 255},${n & 255},${a})`; }
function chunk(arr, n) { const out = []; for (let i = 0; i < arr.length; i += n) out.push(arr.slice(i, i + n)); return out.length ? out : [[]]; }
function rand(i) { const x = Math.sin(i * 12.9898) * 43758.5453; return x - Math.floor(x); }
function wrap(s, max) { const w = s.split(' '), out = ['']; for (const x of w) { if ((out.at(-1) + ' ' + x).trim().length > max && out.at(-1)) out.push(x); else out[out.length - 1] = (out.at(-1) + ' ' + x).trim(); } return out.slice(0, 2); }
