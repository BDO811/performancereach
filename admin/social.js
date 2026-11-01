// Social team view for Growth Studio: the owner's side of the AI social media team.
// The agents run on the Mac worker. This page edits growthSocialInputs and queues growthCommands.
// It reads growthSocial, which only the worker writes. No button here posts, sends or spends.

const TEAM = [
  { id: 'orchestrator', name: 'Orchestrator', job: 'Reads every signal, scores the week, writes one brief per job and decides what needs you.', never: 'Never drafts, publishes, schedules or spends.' },
  { id: 'search-visibility', name: 'Search visibility', job: 'Watches queries, rankings and which page owns each keyword.', never: 'Never changes a live page.' },
  { id: 'market-radar', name: 'Market radar', job: 'Tracks competitors, audiences and web mentions, then sorts what matters.', never: 'Never answers a competitor.' },
  { id: 'content-engine', name: 'Content engine', job: 'Writes posts and articles in your voice with three hooks and a pass or fail voice check.', never: 'Never fixes a voice failure quietly. It holds the draft.' },
  { id: 'creative-studio', name: 'Creative studio', job: 'Turns a brief into visual and video specs that match your brand rules.', never: 'Never uses an asset that is not in the asset library.' },
  { id: 'publishing-social', name: 'Publishing & social', job: 'Fits approved work to each channel and picks the slot. Marks it [PASTE] until a scheduler is connected.', never: 'Never schedules anything above your approval bar.' },
  { id: 'reviews-reputation', name: 'Reviews & reputation', job: 'Drafts replies to reviews and mentions.', never: 'Never posts a reply to a negative review without you.' },
  { id: 'leads-conversations', name: 'Leads & conversations', job: 'Answers from your approved scripts and passes real leads to you.', never: 'Never improvises an answer outside the FAQ library.' },
  { id: 'results-roi', name: 'Results & ROI', job: 'Writes one weekly note: what went out, what it earned, what cost too much.', never: 'Never changes a budget or invents a benchmark.' },
];
const PLAYBOOKS = [
  { id: 'search-demand-spikes', name: 'Search demand spikes', first: 'Content engine', gate: 'Approval bar', hint: 'The keyword or topic that spiked, plus what the tool showed' },
  { id: 'competitor-drops-a-promo', name: 'Competitor drops a promo', first: 'Market radar', gate: 'Always waits if it touches price or an offer', hint: 'Who, what the promo is, where you saw it, the date' },
  { id: 'one-star-review-lands', name: 'One-star review lands', first: 'Reviews & reputation', gate: 'Always waits', hint: 'Reviewer name, date, stars and the full text' },
  { id: 'content-calendar-looks-thin', name: 'Content calendar looks thin', first: 'Publishing & social', gate: 'Approval bar', hint: 'Which channels have gaps, and for which dates' },
  { id: 'a-post-goes-viral', name: 'A post goes viral', first: 'Publishing & social', gate: 'Any boost always waits', hint: 'The post, the channel and the numbers you see' },
  { id: 'ranking-drops-a-page', name: 'Ranking drops a page', first: 'Search visibility', gate: 'Approval bar', hint: 'The page, the keyword, the old and new positions' },
  { id: 'ad-creative-fatigues', name: 'Ad creative fatigues', first: 'Creative studio', gate: 'Always waits (paid)', hint: 'The ad, its frequency and the change in click rate' },
  { id: 'dm-lead-at-11pm', name: 'DM or lead at 11pm', first: 'Leads & conversations', gate: 'Wakes you only for a real lead', hint: 'The message, the channel and the time' },
];
const MOVES = [
  ['Collects', 'Exports land in Brand OS'], ['Scores', 'Orchestrator ranks the week'], ['Briefs', 'One brief per job'],
  ['Drafts', 'Departments write in your voice'], ['Schedules', 'Approved work gets a slot'], ['Approves', 'You clear the queue'],
];
const ZONES = [
  ['Signals', [['Google Search Console', 'Search queries people use to find you'], ['Google Analytics 4', 'Sessions and where they came from'], ['Semrush', 'Rankings and rivals'], ['Google Business Profile', 'New reviews'], ['Meta insights', 'Facebook and Instagram reach'], ['LinkedIn analytics', 'Page analytics'], ['YouTube analytics', 'Channel analytics'], ['Brand24', 'Web mentions']]],
  ['System of record', [['HubSpot', 'Every lead and customer'], ['Airtable', 'Content calendar'], ['Google Drive', 'Brand asset drive'], ['Notion', 'Brand wiki'], ['Segment', 'Customer data'], ['Supabase', 'Unified store'], ['Google Calendar', 'Publish calendar']]],
  ['The brain', [['Claude', 'Reasoning and writing. Live, on Sonnet'], ['LangGraph', 'Multi-step agents'], ['Postgres with pgvector', 'Topic and customer memory'], ['Midjourney', 'Visuals'], ['ElevenLabs', 'Voice-over'], ['Whisper', 'Transcription']]],
  ['Search and market', [['Ahrefs', 'Backlinks'], ['Screaming Frog', 'Site crawl'], ['SparkToro', 'Audience research'], ['Similarweb', 'Competitor traffic'], ['Google Alerts', 'Alerts watch']]],
  ['Content and creative', [['Surfer', 'Briefs and draft scoring'], ['Frase', 'Brief research'], ['Grammarly', 'Editing pass'], ['Canva', 'Graphics'], ['Figma', 'Layouts'], ['Remotion', 'Video']]],
  ['Publishing, reviews and leads', [['Metricool', 'Scheduler for every channel'], ['WordPress', 'Publishes articles'], ['Podium', 'Reviews'], ['NiceJob', 'Reviews'], ['ManyChat', 'Chat and DM replies'], ['Twilio', 'SMS'], ['Calendly', 'Booking links'], ['Front', 'Shared inbox']]],
  ['Data and observability', [['Airbyte', 'Moves data in'], ['dbt', 'Cleans the data'], ['BigQuery', 'Stores the data'], ['Looker', 'Shows the numbers'], ['Metabase', 'Shows the numbers'], ['Vercel', 'Hosting'], ['Sentry', 'Catches errors'], ['LaunchDarkly', 'Feature flags']]],
];
const TOOL_STATES = ['Weekly export', 'Connected', 'Not used'];
const EXPORT_FOLDERS = { 'signals-seo': 'Search, reviews, mentions, post insights', reputation: 'Reviews and mentions', conversation: 'Chat and DM history', reporting: 'Results and spend' };
const OWNER_LABELS = { 'owner/brand-voice.md': ['Brand voice', 'How you sound. The voice check tests every draft against it.'], 'owner/budget-cap.md': ['Budget cap', 'The most the team may spend. Every spend still waits for you.'], 'owner/approval-bar.md': ['Approval bar', 'What may go out without you. If it is not listed, it waits.'], 'owner/positioning.md': ['Positioning', 'What you stand for. Every job is scored against it.'] };
const FIRST_FILES = ['brand-os/brand-brain/voice-guide.md', 'brand-os/brand-brain/tone-rules.md', 'brand-os/content/content-calendar.md'];

const hasPrompt = t => /\[FILL IN:/.test(t || '');
const prompts = t => (String(t || '').match(/\[FILL IN:/g) || []).length;
let tab = 'desk';

export function socialCounts(state) {
  const open = (state?.queue || []).filter(i => i.section === 'open').length, held = (state?.held || []).filter(i => i.section === 'open').length;
  return { open, held };
}

export function renderSocial(ctx) {
  const { $, esc } = ctx, state = ctx.state(), inputs = ctx.inputs();
  if (!state || !inputs) {
    $('view').innerHTML = `<div class="empty"><h2>This workspace has no social team yet</h2><p>Each product gets its own team, files and queue. The Mac worker creates them.</p><div class="actions"><button data-social="init">Set up the social team for ${esc(ctx.product().name)}</button></div></div>`;
    return;
  }
  const { open, held } = socialCounts(state);
  const tabs = [['desk', 'Desk'], ['queue', `Your queue (${open + held})`], ['drafts', `Drafts (${(state.drafts || []).length})`], ['owner', 'Owner inputs'], ['brand', 'Brand OS'], ['playbooks', 'Playbooks'], ['team', 'Team'], ['tools', 'Tools'], ['log', 'Activity log']];
  const body = { desk, queue, drafts, owner, brand, playbooks, team, tools, log }[tab];
  $('view').innerHTML = `<div class="tabs" role="tablist">${tabs.map(([k, l]) => `<button data-social-tab="${k}" class="${tab === k ? 'active' : ''}">${esc(l)}</button>`).join('')}</div>${body(ctx, state, inputs)}`;
}

function readiness(state, inputs) {
  const missing = Object.keys(OWNER_LABELS).filter(k => hasPrompt(inputs.files[k]));
  const first = FIRST_FILES.filter(k => hasPrompt(inputs.files[k]));
  return { missing, first };
}

function desk(ctx, state, inputs) {
  const { esc, tag, date } = ctx, { missing, first } = readiness(state, inputs), { open, held } = socialCounts(state);
  const run = state.run, stale = run && Date.now() - new Date(run.startedAt).getTime() > 3 * 36e5, active = run && !stale;
  const status = inputs.stopped ? tag('Stopped') : missing.length ? tag('Blocked: owner files') : active ? tag('Running') : tag('Ready');
  const next = inputs.stopped ? 'The kill switch is on. Every agent refuses to act until you release it.'
    : missing.length ? `Fill ${missing.length} owner ${missing.length === 1 ? 'file' : 'files'} before the first run. Agents stop on any open prompt.`
    : first.length ? `The owner files are done. Fill ${first.map(f => f.split('/').pop()).join(', ')} so drafts have a voice and a calendar to work from.`
    : open + held ? `${open + held} ${open + held === 1 ? 'item waits' : 'items wait'} for you in the queue.`
    : (state.pendingBriefs || []).length ? `${state.pendingBriefs.length} briefs are waiting for their departments.` : 'Nothing waits for you. Add this week\'s exports, then run the week.';
  return `<div class="row wrap"><div>${status}<p class="lead">${esc(next)}</p></div>
  <div class="actions"><button data-social="toggleStop" class="${inputs.stopped ? '' : 'social-stop'}">${inputs.stopped ? 'Release the kill switch' : 'Kill switch: stop everything'}</button></div></div>
  <div class="actions">
   <button data-social="week" ${inputs.stopped || missing.length || active ? 'disabled' : ''}>Run this week's loop</button>
   <button data-social="export">Add an export</button>
   <button data-social="handoffs" ${inputs.stopped || missing.length || active || !(state.pendingBriefs || []).length ? 'disabled' : ''}>Run pending briefs (${(state.pendingBriefs || []).length})</button>
   <button data-social="report" ${inputs.stopped || missing.length || active ? 'disabled' : ''}>Write the results note</button>
   <button data-social="learn" ${inputs.stopped || missing.length || active ? 'disabled' : ''}>Suggest brand file updates</button>
  </div>
  <ol class="social-moves">${MOVES.map(([m, d]) => `<li><strong>${esc(m)}</strong><span>${esc(d)}</span></li>`).join('')}</ol>
  ${missing.length ? `<section class="section"><h2>Owner files to fill</h2>${missing.map(k => `<p>${tag('Open')} <strong>${esc(OWNER_LABELS[k][0])}</strong>, ${prompts(inputs.files[k])} prompts left. <button class="subtle" data-social="editFile" data-file="${esc(k)}">Fill it in</button></p>`).join('')}</section>` : ''}
  ${active ? runBlock(ctx, run, true) : ''}
  <section class="section"><h2>Recent runs</h2>${(state.runs || []).length ? state.runs.map(r => runBlock(ctx, r)).join('') : '<p>No runs yet.</p>'}</section>
  <p class="meta">Each step spends at most $2 and each run at most $8. Only one model call runs at a time on the Mac, shared with the rest of Growth Studio. Last update ${esc(date(state.updatedAt))}.</p>`;
}

function runBlock(ctx, r, live) {
  const { esc, tag, date } = ctx;
  return `<details class="run" ${live ? 'open' : ''}><summary><span>${esc(r.label)}, ${esc(date(r.startedAt))}</span><span>${tag(r.status)} $${Number(r.costUsd || 0).toFixed(2)}</span></summary>
  ${r.error ? `<p>${esc(r.error)}</p>` : ''}${(r.steps || []).map(s => `<details class="task"><summary>${esc(s.label)} ${tag(s.status)}</summary>${s.error ? `<p>${esc(s.error)}</p>` : ''}${s.result ? `<pre class="report">${esc(s.result)}</pre>` : ''}</details>`).join('')}</details>`;
}

function itemBlock(ctx, state, item, kind) {
  const { esc, tag } = ctx, f = item.fields || {}, path = f.File, draft = (state.drafts || []).find(d => d.path === path);
  const buttons = kind === 'needs' ? ['Approve', 'Reject'] : ['Fixed: send it on', 'Drop it'];
  return `<article class="post"><div class="row wrap"><div><span class="meta">${esc(item.id)}</span><h3>${esc(item.title)}</h3></div><div>${item.urgent ? tag('URGENT') : ''} ${item.overCap ? tag('OVER CAP') : ''}</div></div>
  ${Object.entries(f).filter(([k]) => k !== 'Owner note' || f[k]).map(([k, v]) => `<p><strong>${esc(k)}:</strong> ${esc(v)}</p>`).join('')}
  ${draft ? `<details><summary>Read the draft</summary><pre class="report">${esc(draft.content)}</pre></details>` : ''}
  ${item.section === 'open' ? `<div class="actions">${buttons.map(b => `<button data-social="decide" data-queue="${kind}" data-item="${esc(item.id)}" data-decision="${esc(b)}" ${item.ticked?.length ? 'disabled' : ''}>${esc(b)}</button>`).join('')}</div>${item.ticked?.length ? `<p class="meta">You chose ${esc(item.ticked[0])}. The worker is processing it.</p>` : ''}` : `<p class="meta">${esc((item.ticked || []).join(', ') || 'Decided')}</p>`}</article>`;
}

function queue(ctx, state) {
  const needs = (state.queue || []).filter(i => i.section === 'open').sort((a, b) => b.urgent - a.urgent), heldOpen = (state.held || []).filter(i => i.section === 'open');
  const done = [...(state.queue || []), ...(state.held || [])].filter(i => i.section === 'done');
  return `<p>Only you decide these. Your click ticks the box in the queue file, then the orchestrator acts on it.</p>
  <section class="section"><h2>Needs your OK (${needs.length})</h2>${needs.map(i => itemBlock(ctx, state, i, 'needs')).join('') || '<p>Nothing waits for you.</p>'}</section>
  <section class="section"><h2>Held for voice review (${heldOpen.length})</h2><p>These failed the voice check. Nothing here goes out. If every draft fails, a rule in tone-rules.md is probably wrong: fix the rule.</p>${heldOpen.map(i => itemBlock(ctx, state, i, 'held')).join('') || '<p>Nothing is held.</p>'}</section>
  ${done.length ? `<section class="section"><details><summary>Decided (${done.length})</summary>${done.map(i => itemBlock(ctx, state, i, 'needs')).join('')}</details></section>` : ''}`;
}

function drafts(ctx, state) {
  const { esc, tag, date } = ctx, list = state.drafts || [], briefs = state.briefs || [], pending = new Set(state.pendingBriefs || []);
  return `<p>Everything the departments wrote. Nothing here is live. Copy a [PASTE] version to post it yourself, or send it to Content studio, which asks you to approve the exact revision.</p>
  ${list.map(d => { const m = d.meta || {}; return `<article class="post"><div class="row wrap"><div><span class="meta">${esc(m.channel || 'draft')}, ${esc(date(d.modifiedAt))}</span><h3>${esc(d.name)}</h3></div><div>${m.voice_check ? tag('voice ' + m.voice_check) : ''} ${/\[VERIFY\]/.test(d.content) ? tag('needs review: VERIFY') : ''} ${/\[PASTE\]/.test(d.content) ? tag('ready: PASTE') : ''}</div></div>
  <details><summary>Read it</summary><pre class="report">${esc(d.content)}</pre>${d.truncated ? '<p class="meta">Shortened here. The full file is in the Mac workspace.</p>' : ''}</details>
  <div class="actions"><button data-social="copyDraft" data-path="${esc(d.path)}">Copy text</button><button data-social="toStudio" data-path="${esc(d.path)}" ${/\[VERIFY\]/.test(d.content) ? 'disabled' : ''}>Send to Content studio</button></div></article>`; }).join('') || '<p>No drafts yet. Run the week to get the first ones.</p>'}
  <section class="section"><h2>Briefs (${briefs.length})</h2>${briefs.map(b => `<details class="task"><summary>${esc(b.name)} ${pending.has(b.path) ? tag('pending') : tag(b.meta?.department ? 'done' : 'plan')}</summary><pre class="report">${esc(b.content)}</pre></details>`).join('') || '<p>No briefs yet.</p>'}</section>`;
}

function owner(ctx, state, inputs) {
  const { esc, tag } = ctx;
  return `<p>The four things only you set. Agents read them before acting and cannot change them. The worker restores these files if a run ever touches one.</p>
  ${Object.entries(OWNER_LABELS).map(([k, [n, d]]) => `<article class="post"><div class="row wrap"><div><h3>${esc(n)}</h3><p>${esc(d)}</p></div>${hasPrompt(inputs.files[k]) ? tag(`Open: ${prompts(inputs.files[k])} prompts`) : tag('Ready')}</div><div class="actions"><button data-social="editFile" data-file="${esc(k)}">Edit</button></div></article>`).join('')}`;
}

function brand(ctx, state, inputs) {
  const { esc, tag } = ctx, groups = {};
  Object.keys(inputs.files).filter(k => k.startsWith('brand-os/') && k.split('/').length === 3).sort().forEach(k => (groups[k.split('/')[1]] ||= []).push(k));
  const filled = Object.keys(inputs.files).filter(k => k.startsWith('brand-os/') && k.split('/').length === 3 && !hasPrompt(inputs.files[k])).length;
  const total = Object.values(groups).flat().length;
  return `<div class="row wrap"><p>What the team knows about this brand. ${filled} of ${total} files are filled. Fill the first three before the first run. Agents can update these files, and your edit wins if you both change one during a run.</p><button data-social="export">Add an export</button></div>
  ${Object.entries(groups).map(([g, files]) => `<section class="section"><h2>${esc(g)}</h2><div class="table-wrap"><table><tbody>${files.map(k => `<tr><td><strong>${esc(k.split('/').pop())}</strong>${FIRST_FILES.includes(k) ? ' <span class="meta">fill first</span>' : ''}</td><td>${hasPrompt(inputs.files[k]) ? tag(`Open: ${prompts(inputs.files[k])}`) : tag('Ready')}</td><td><button data-social="editFile" data-file="${esc(k)}">Edit</button></td></tr>`).join('')}</tbody></table></div></section>`).join('')}`;
}

function playbooks(ctx, state, inputs) {
  const { esc } = ctx, blocked = inputs.stopped || readiness(state, inputs).missing.length;
  return `<p>For the moments that break a normal week. Each event goes to the orchestrator first and jumps ahead of the weekly plan. None of them publishes.</p>
  <div class="table-wrap"><table><thead><tr><th>Event</th><th>First department</th><th>Who approves</th><th></th></tr></thead><tbody>${PLAYBOOKS.map(p => `<tr><td><strong>${esc(p.name)}</strong></td><td>${esc(p.first)}</td><td>${esc(p.gate)}</td><td><button data-social="playbook" data-playbook="${p.id}" ${blocked ? 'disabled' : ''}>Fire</button></td></tr>`).join('')}</tbody></table></div>`;
}

function team(ctx, state) {
  const { esc, tag } = ctx, log = state.log || [], last = id => [...log].reverse().find(l => l.split(' | ')[1] === id);
  return `<p>One orchestrator and eight departments, separate for every product. Departments never brief each other.</p><div class="table-wrap"><table><thead><tr><th>Agent</th><th>Does</th><th>Never</th><th>Last action</th></tr></thead><tbody>${TEAM.map(a => { const l = last(a.id); return `<tr><td><strong>${esc(a.name)}</strong><br><code>${esc(a.id)}</code></td><td>${esc(a.job)}</td><td>${esc(a.never)}</td><td>${l ? esc(l.split(' | ').slice(0, 1) + ': ' + l.split(' | ')[2]) : tag('Not run')}</td></tr>`; }).join('')}</tbody></table></div>`;
}

function tools(ctx, state, inputs) {
  const { esc } = ctx, set = inputs.tools || {};
  return `<p>Every tool on the guide's board. Nothing is connected yet, so the team runs on weekly exports. This list records your plan. Marking a tool Connected does not connect it: each one still needs its own API or MCP setup on the Mac.</p>
  ${ZONES.map(([z, list]) => `<section class="section"><h2>${esc(z)}</h2><div class="table-wrap"><table><tbody>${list.map(([n, j]) => { const key = n.toLowerCase().replace(/[^a-z0-9]+/g, '-'), cur = n === 'Claude' ? 'Connected' : set[key] || TOOL_STATES[0]; return `<tr><td><strong>${esc(n)}</strong></td><td>${esc(j)}</td><td>${n === 'Claude' ? 'Connected' : `<select data-social-tool="${key}" aria-label="${esc(n)} status">${TOOL_STATES.map(s => `<option ${s === cur ? 'selected' : ''}>${s}</option>`).join('')}</select>`}</td></tr>`; }).join('')}</tbody></table></div></section>`).join('')}`;
}

function log(ctx, state) {
  const { esc } = ctx, lines = [...(state.log || [])].reverse();
  return `<p>One line for every action, newest first. The file on the Mac is append only.</p><div class="table-wrap"><table><thead><tr><th>When</th><th>Who</th><th>Action</th><th>File</th></tr></thead><tbody>${lines.map(l => { const [w, a, x, f] = l.split(' | '); return `<tr><td>${esc(w)}</td><td><code>${esc(a)}</code></td><td>${esc(x)}</td><td>${esc(f)}</td></tr>`; }).join('') || '<tr><td colspan="4">Nothing has run yet.</td></tr>'}</tbody></table></div>`;
}

async function command(ctx, action, data = {}) {
  const id = ctx.uid();
  await ctx.put('growthCommands/' + id, { id, action, productId: ctx.productId(), status: 'queued', createdAt: ctx.now(), ...data });
  ctx.notice('Queued. The Mac worker picks this up within 15 seconds while it is awake. Progress shows on the Desk.');
}

const inputsPath = ctx => 'growthSocialInputs/' + ctx.productId();

export async function handleSocial(b, ctx) {
  const { $, esc, field, area, openEditor, mutate } = ctx, act = b.dataset.social;
  if (b.dataset.socialTab) { tab = b.dataset.socialTab; ctx.render(); return; }
  const state = ctx.state();
  if (act === 'init') await command(ctx, 'social_init');
  else if (act === 'toggleStop') {
    const stopping = !ctx.inputs().stopped;
    await mutate(inputsPath(ctx), i => ({ ...i, stopped: stopping, stoppedAt: ctx.now(), updatedAt: ctx.now() }));
    ctx.notice(stopping ? 'Kill switch on. A running agent ends within seconds. Whatever it wrote stays in the workspace for you to read.' : 'Kill switch released. Read the activity log, then run the week again.');
  } else if (act === 'week') await command(ctx, 'social_week');
  else if (act === 'handoffs') await command(ctx, 'social_handoffs');
  else if (act === 'report') await command(ctx, 'social_report');
  else if (act === 'learn') await command(ctx, 'social_learn');
  else if (act === 'editFile') {
    const file = b.dataset.file, text = ctx.inputs().files[file] || '';
    openEditor(file.split('/').pop(), `<p class="meta">${esc(file)}. Replace each [FILL IN: ...] prompt with your own words, then delete the Example line under it.</p><label>Contents<textarea id="socialFile" rows="24" spellcheck="true" required>${esc(text)}</textarea></label>`, async () => {
      const value = $('socialFile').value;
      await mutate(inputsPath(ctx), i => ({ ...i, files: { ...i.files, [file]: value }, updatedAt: ctx.now() }));
    });
  } else if (act === 'decide') {
    const { queue: q, item, decision } = b.dataset, needsNote = decision === 'Reject';
    openEditor(`${decision}: ${item}`, `<p>The worker ticks this one box in the queue file, then runs the orchestrator on it.</p>${area(needsNote ? 'Why, so it can drop or re-brief it' : 'Note, optional', 'socialNote', '', needsNote)}`, async () => {
      await command(ctx, 'social_decide', { queue: q, itemId: item, decision, note: $('socialNote').value.trim() });
    }, decision);
  } else if (act === 'playbook') {
    const p = PLAYBOOKS.find(x => x.id === b.dataset.playbook);
    openEditor(p.name, `<p>First department: ${esc(p.first)}. Who approves: ${esc(p.gate)}.</p>${area(p.hint, 'socialEvent')}`, async () => {
      await command(ctx, 'social_playbook', { playbook: p.id, event: $('socialEvent').value.trim() });
    }, 'Fire playbook');
  } else if (act === 'export') {
    openEditor('Add an export', `<p>Paste a CSV or report. It is saved with today's date in the folder the agents read. Saving runs no model.</p><label>Folder<select id="socialFolder">${Object.entries(EXPORT_FOLDERS).map(([k, v]) => `<option value="${k}">${esc(k)}: ${esc(v)}</option>`).join('')}</select></label>${field('File name, such as gsc-queries.csv', 'socialFileName')}${area('Contents', 'socialExport')}`, async () => {
      const content = $('socialExport').value;
      if (content.length > 800000) throw Error('That export is too big to paste. Keep it under 800 KB.');
      await command(ctx, 'social_export', { folder: $('socialFolder').value, fileName: $('socialFileName').value.trim(), content });
    }, 'Save export');
  } else if (act === 'copyDraft') {
    await navigator.clipboard.writeText(state.drafts.find(d => d.path === b.dataset.path).content);
    ctx.notice('Draft copied.');
  } else if (act === 'toStudio') {
    const d = state.drafts.find(x => x.path === b.dataset.path), accounts = Object.keys(ctx.product().accounts || {}), channel = d.meta?.channel;
    if (!accounts.includes(channel)) throw Error(`Content studio has no ${channel || 'matching'} account for this product. Copy the text instead.`);
    const caption = d.content.replace(/^---\n[\s\S]*?\n---\n?/, '').replaceAll('[PASTE]', '').trim(), id = ctx.uid(), when = ctx.now();
    await ctx.put('growthContent/' + id, { id, productId: ctx.productId(), title: d.name.replace(/\.md$/, ''), platform: channel, format: 'Text', caption, script: '', visualBrief: '', pillar: ctx.product().pillars?.[0] || '', proposedDate: '', mediaUrl: '', status: 'draft', review: 'From the social team. Needs human claim and media review', approval: null, scheduledAt: null, revision: 1, createdAt: when, sourceAgent: 'social-team' });
    ctx.notice('Sent to Content studio as a draft. It still needs your approval there.');
  }
}

export async function handleSocialChange(e, ctx) {
  const key = e.target.dataset.socialTool;
  if (!key) return false;
  await ctx.mutate(inputsPath(ctx), i => ({ ...i, tools: { ...(i.tools || {}), [key]: e.target.value }, updatedAt: ctx.now() }));
  return true;
}
