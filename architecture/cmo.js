// Architecture reference only. This module never starts a run, posts or changes owner inputs.
// Its data comes from cmo-harness.json, which _cmo-harness/build.py writes from the same catalogs as the harness.
const esc = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const code = value => `<code>${esc(value)}</code>`;
const detail = (number, id, title, subtitle, body) => `<details class="sm-detail" id="${esc(id)}"><summary><span class="sm-detail-number" aria-hidden="true">${esc(number)}</span><span><strong>${esc(title)}</strong><small>${esc(subtitle)}</small></span><span class="sm-detail-mark" aria-hidden="true"></span></summary><div class="sm-detail-body">${body}</div></details>`;

const SOURCE_LABEL = { loop: 'Loop', mind: 'Mind', social: 'Social team' };

const COMMANDS = [
  ['/run-week', 'Plan and make', 'The CMO writes the week plan from targets and last week’s results. Research finds what the audience is asking and drafts posts and emails. Content designs, voices, edits and brand checks them, then packs the week into the owner queue.'],
  ['/process-approvals', 'Owner decides', 'After the owner ticks, Publish slots approved work and packages it for TikTok, Reels, Shorts, X and the newsletter, marked [PASTE] or [SEND].'],
  ['/daily-sweep', 'Answer and sell', 'Community answers comments and DMs, catches leads and escalates risk. Sales scores leads, books calls, reminds and follows up.'],
  ['/morning-page', 'One page a day', 'What worked, who booked a call, what goes out next and what waits for the owner.'],
  ['/close-week', 'Close the loop', 'Post, revenue, call and email results feed the weekly report and next week’s double down, drop and test list.'],
];

const OWNER_FILES = [
  ['owner/targets.md', 'The one goal this quarter, the weekly numbers, channels and the highest acceptable cost per call and per client.'],
  ['owner/positioning.md', 'The audience, offer, distinction and priorities.'],
  ['owner/brand-voice.md', 'How the brand sounds, words it avoids and the one consented ElevenLabs voice.'],
  ['owner/approval-bar.md', 'What may auto ship, what always waits and what is urgent.'],
  ['owner/budget-cap.md', 'The monthly and per item spending ceiling.'],
  ['owner/sales-rules.md', 'Ideal client, lead scoring, the booking link, offers that may get a payment request, review asks and CRM stages.'],
];

function render(data) {
  const target = document.getElementById('cmo-content');
  if (!target) return;
  const c = data.counts;
  target.classList.add('sm-harness', 'cmo-harness');
  target.innerHTML = `
    <div class="sm-overview">
      <div class="sm-summary">
        <p class="sm-eyebrow">One marketing function, one sign-off</p>
        <h3>A CMO that runs every marketing agent.</h3>
        <p class="sm-lead">The CMO plans each week against the owner’s targets and briefs twelve directors. Under them sit the 36 agent marketing loop, all ${esc(c.minds)} agency Mind agents and the Social team. Nothing goes live until the owner approves it.</p>
        <div class="sm-actions"><a class="btn btn--primary" href="#cmo-chain">See the chain</a><a class="btn" href="${esc(data.source_video)}" target="_blank" rel="noopener noreferrer">Watch the source video <span aria-hidden="true">↗</span></a></div>
        <p class="sm-credit">The marketing loop is adapted from a video by <a href="https://www.tiktok.com/@hannesrkuhn" target="_blank" rel="noopener noreferrer">@hannesrkuhn</a>: 36 agents across research, content, publishing, the loop, sales and community, with one human approval.</p>
      </div>
      <aside class="sm-state" aria-labelledby="cmo-state-title">
        <span class="status status--build"><span class="glyph glyph--build" aria-hidden="true"></span>Harness scaffolded</span>
        <h4 id="cmo-state-title">Ready for a brand workspace</h4>
        <p>Agents, directors, commands, owner files and controls are built and tested. Create a workspace for PerformanceReach or one client, fill the six owner files and add this week’s exports. Live integrations remain unverified.</p>
        <dl class="sm-counts"><div><dt>Directors</dt><dd>${esc(c.directors)}</dd></div><div><dt>Agents</dt><dd>${esc(c.agents)}</dd></div><div><dt>Commands</dt><dd>${COMMANDS.length}</dd></div></dl>
        <p class="sm-state-foot">Current mode: weekly exports, draft files and owner handoff. No live posting, email sending or spend.</p>
      </aside>
    </div>
    <div class="sm-boundary"><strong>How this fits Athem</strong><p>The CMO harness brings together ${esc(c.loop)} loop agents, the ${esc(c.minds)} agents in the Minds above and the Social team’s ${esc(c.social)} departments, so ${esc(c.agents)} agents report through twelve directors to one CMO. Agent ids match the catalog above. The Social orchestrator role is held by ${code('director-social')}.</p></div>
    <nav class="sm-jump" aria-label="CMO harness topics"><a href="#cmo-chain">Chain</a><a href="#cmo-loop">Weekly loop</a><a href="#cmo-video">The 36 agent loop</a><a href="#cmo-owner">Owner controls</a><a href="#cmo-start">First run</a></nav>
    <div class="sm-details">
      ${detail('01', 'cmo-chain', `Owner, CMO, ${c.directors} directors, ${c.agents} agents`, 'Every brief goes down the chain and every return comes back up it.', `
        <p>The CMO briefs directors. Directors brief their own agents. Nobody briefs across the chain: a director that needs another department asks the CMO. Where a loop agent and a Mind agent could do the same job, weekly and tactical work goes to the loop agent and deep or client facing work goes to the Mind.</p>
        <div class="sm-team-grid">
          <article class="sm-role sm-role--lead"><h4>CMO</h4><p class="sm-ident">cmo</p><p>Owns the plan and the targets, runs the weekly loop and the daily sweep, settles overlaps between directors, keeps the owner queue honest and writes the morning page. Never drafts, publishes, sends or spends.</p></article>
          ${data.directors.map(d => `<article class="cmo-director"><h4>${esc(d.name)}</h4><p class="sm-ident">${esc(d.id)}</p><p>${esc(d.job)}</p><details class="cmo-roster"><summary>${esc(d.agents.length)} agents</summary><ul>${d.agents.map(a => `<li><span>${esc(a.name)}</span><span class="cmo-source">${esc(a.source === 'mind' ? a.mind + ' Mind' : SOURCE_LABEL[a.source])}</span><span class="sm-ident">${esc(a.id)}</span></li>`).join('')}</ul></details></article>`).join('')}
        </div>
      `)}
      ${detail('02', 'cmo-loop', 'The weekly loop in five commands', 'Research, content, approval, publish, then results feed next week.', `
        <ol class="sm-moves">${COMMANDS.map(([cmd, name, desc]) => `<li><strong>${esc(name)}</strong><p class="sm-ident">${esc(cmd)}</p><p>${esc(desc)}</p></li>`).join('')}</ol>
        <p class="sm-callout">Every public link carries UTM tags, so Revenue Tracker can show which posts made money. Loop Feeder writes ${code('loop/next-week-inputs.md')}, which opens the next week’s plan.</p>
        <p>The Social team’s eight event playbooks, such as ${code('/one-star-review-lands')} and ${code('/dm-lead-at-11pm')}, still run as before, now through ${code('director-social')}.</p>
      `)}
      ${detail('03', 'cmo-video', 'The 36 agent marketing loop', 'Six departments of six, each led by a director.', `
        <div class="sm-brand-grid">${data.loop.map(d => `<article><h4>${esc(d.name)}</h4><p class="sm-ident">${esc(d.director)}</p><ul>${d.agents.map(a => `<li>${esc(a)}</li>`).join('')}</ul></article>`).join('')}</div>
        <p>Voiceover uses ElevenLabs with the one voice the owner names and consents to. Posters write ready to paste packages until a channel connection is verified.</p>
      `)}
      ${detail('04', 'cmo-owner', 'Six owner files, one queue, one stop switch', 'The owner decides the brand and the budget. The agents do the rest.', `
        <dl class="sm-zone-list">${OWNER_FILES.map(([file, desc]) => `<div><dt>${code(file)}</dt><dd>${esc(desc)}</dd></div>`).join('')}</dl>
        <div class="sm-control-grid"><article><h4>Decision queue</h4><p>${code('queue/needs-your-ok.md')} collects everything above the approval bar. Spend, prices, offers, payment requests, contracts, real names, competitor responses and open ${code('[VERIFY]')} marks always wait. Only the owner ticks a box.</p></article><article><h4>Stop switch</h4><p>${code('owner/STOP')} halts every agent in the workspace. Only the owner clears it.</p></article><article><h4>No live actions</h4><p>Agents have file tools, plus web search for research roles, and no shell. Posts are ${code('[PASTE]')}, emails ${code('[SEND]')}, audio and video ${code('[RENDER]')}, CRM updates ${code('[IMPORT]')}.</p></article><article><h4>Sealed workspaces</h4><p>PerformanceReach and each client get their own workspace. No agent reads or mentions another workspace’s files.</p></article></div>
      `)}
      ${detail('05', 'cmo-start', 'First run, in order', 'Prove one brand before adding the next.', `
        <ol class="sm-readiness"><li><strong>Create a workspace.</strong> ${code('python3 -I _cmo-harness/new_workspace.py <folder>')} for PerformanceReach itself or one client.</li><li><strong>Fill the six owner files.</strong> Any ${code('[FILL IN: ...]')} prompt left blocks the run.</li><li><strong>Add this week’s exports.</strong> Analytics, CRM, calendar, comments, DMs and email go into ${code('exports/')}.</li><li><strong>Run the week.</strong> Open Claude Code in the workspace and type ${code('/run-week')}. Review the plan, the briefs and the queue.</li><li><strong>Approve and publish.</strong> Tick items, run ${code('/process-approvals')} and post the ${code('[PASTE]')} packages.</li><li><strong>Close the week.</strong> Run ${code('/close-week')} and check the report and next week’s inputs.</li></ol>
      `)}
    </div>`;
}

fetch('/architecture/cmo-harness.json')
  .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
  .then(render)
  .catch(() => {});
