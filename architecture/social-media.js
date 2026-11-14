// Architecture reference only. This module never starts a run, posts or changes owner inputs.
const SOURCE = 'https://dandy-bug-77c.notion.site/AI-Native-Social-Media-Agent-Team-402a1f98521280859feede9319ce1aa0';
const esc = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const TEAM = [
  ['orchestrator', 'Social orchestrator', 'Scores signals, writes the week plan and briefs, applies owner gates and handles returns. Does not draft, schedule, publish or spend.'],
  ['search-visibility', 'Search visibility', 'Maps queries to pages, checks rankings and prepares search refresh recommendations. Does not change a live page.'],
  ['market-radar', 'Market radar', 'Interprets competitor activity, audience research and mentions with dated evidence. Does not engage competitors.'],
  ['content-engine', 'Content engine', 'Creates sourced posts and articles, three hook options and a voice check. A failed check holds the draft.'],
  ['creative-studio', 'Creative studio', 'Prepares image, layout and video specifications using approved brand assets and visual rules.'],
  ['publishing-social', 'Publishing & social', 'Adapts approved drafts to channels, adds tracking tags and proposes slots. Current output is marked [PASTE].'],
  ['reviews-reputation', 'Reviews & reputation', 'Prepares review and mention replies. Negative review replies always require the owner.'],
  ['leads-conversations', 'Leads & conversations', 'Uses approved FAQs and scripts, qualifies conversations and identifies real leads for the owner.'],
  ['results-roi', 'Results & ROI', 'Reports outcomes, attribution and channel costs. Recommends changes without moving a budget.'],
];

const PLAYBOOKS = [
  ['search-demand-spikes', 'Search demand rises', 'Content engine → Search visibility validates the target page', 'Approval bar; unresolved facts wait.'],
  ['competitor-drops-a-promo', 'A competitor launches a promotion', 'Market radar → Content engine → Creative studio', 'Prices and offers always wait.'],
  ['one-star-review-lands', 'A negative review arrives', 'Reviews & reputation drafts the response', 'Owner approval always required.'],
  ['content-calendar-looks-thin', 'The calendar has gaps', 'Publishing & social audits slots → Content engine fills gaps', 'Approval bar; only approved drafts receive slots.'],
  ['a-post-goes-viral', 'A post performs unusually well', 'Publishing & social repurposes → Results & ROI checks value', 'Any proposed boost waits for the owner.'],
  ['ranking-drops-a-page', 'A page loses search position', 'Search visibility diagnoses → Content engine prepares a refresh', 'Approval bar; live page edits are unavailable here.'],
  ['ad-creative-fatigues', 'An ad shows creative fatigue', 'Creative studio prepares variants → Publishing & social plans rotation', 'Paid changes always wait; confirm other variables stayed stable.'],
  ['dm-lead-at-11pm', 'A late DM or lead arrives', 'Leads & conversations checks the FAQ and routing rules', 'Escalate a real lead; do not invent a reply outside approved scripts.'],
];

const BRAND = [
  ['brand-brain', 'Voice and positioning', ['voice-guide', 'tone-rules', 'positioning', 'messaging-bank']],
  ['signals-seo', 'Search evidence and measurement', ['keyword-map', 'ranking-targets', 'serp-rules', 'tracking-setup']],
  ['content', 'The content pipeline', ['content-calendar', 'brief-templates', 'hook-bank', 'seo-checklist']],
  ['creative', 'Approved visual production', ['visual-specs', 'asset-library', 'video-scripts']],
  ['social', 'Channel rules and slots', ['channel-playbooks', 'posting-schedule', 'hashtag-rules']],
  ['reputation', 'Reviews and mentions', ['review-flow', 'gbp-response', 'mentions-rules']],
  ['conversation', 'Replies and lead handoff', ['faq-library', 'auto-reply-scripts', 'routing-rules']],
  ['reporting', 'Definitions, costs and credit', ['kpi-model', 'margin-rules', 'attribution']],
];

// These are choices from the reference tool board, not a connection inventory.
const TOOLS = [
  ['Signals', 'Google Search Console · Google Analytics 4 · Semrush · Google Business Profile · Meta insights · LinkedIn analytics · YouTube analytics · Brand24'],
  ['System of record', 'HubSpot · Airtable · Google Drive · Notion · Segment · Supabase · Google Calendar'],
  ['Brain', 'Claude · LangGraph · Postgres with pgvector · Midjourney · ElevenLabs · Whisper'],
  ['Search and market', 'Ahrefs · Screaming Frog · SparkToro · Similarweb · Google Alerts'],
  ['Content and creative', 'Surfer · Frase · Grammarly · Canva · Figma · Remotion'],
  ['Publishing, reviews and leads', 'Metricool · WordPress · Podium · NiceJob · ManyChat · Twilio · Calendly · Front'],
  ['Data and observability', 'Airbyte · dbt · BigQuery · Looker · Metabase · Vercel · Sentry · LaunchDarkly'],
];

const ZONES = [
  ['Signals', 'Dated search, reviews, mentions, social insights and results.'],
  ['System of record', 'Customer context, calendars, assets and shared knowledge.'],
  ['Owner inputs', 'The voice, positioning, approval policy and spending ceiling.'],
  ['Brain', 'Project rules, scoring, briefs and controlled handoffs.'],
  ['Departments', 'Eight specialists produce the requested work and checks.'],
  ['Engage', 'The reference design routes approved work to publishing and conversations. Athem currently produces handoff drafts.'],
  ['Data and observability', 'Results, costs, failures and an activity trail inform the next week.'],
];

const MOVES = [
  ['Collect', 'Read dated exports, the calendar and open queues.'],
  ['Score', 'Rank urgency, brand fit and evidence.'],
  ['Brief', 'Give one department one job with sources and an owner gate.'],
  ['Draft', 'Return the file, check results and blockers.'],
  ['Schedule', 'Assign a slot to approved work only.'],
  ['Approve', 'Resolve exceptions and feed decisions back into the next pass.'],
];

const detail = (number, id, title, subtitle, body) => `<details class="sm-detail" id="${esc(id)}"><summary><span class="sm-detail-number" aria-hidden="true">${esc(number)}</span><span><strong>${esc(title)}</strong><small>${esc(subtitle)}</small></span><span class="sm-detail-mark" aria-hidden="true"></span></summary><div class="sm-detail-body">${body}</div></details>`;
const code = value => `<code>${esc(value)}</code>`;

function renderSocialArchitecture() {
  const target = document.getElementById('social-media-content');
  if (!target) return;
  target.classList.add('sm-harness');
  target.innerHTML = `
    <div class="sm-overview">
      <div class="sm-summary">
        <p class="sm-eyebrow">A brand team for each product</p>
        <h3>From signals to a weekly plan. With you in control.</h3>
        <p class="sm-lead">One social orchestrator coordinates eight specialist departments. They turn brand knowledge and market evidence into briefs, content, creative, reply drafts and a results report.</p>
        <div class="sm-actions"><a class="btn btn--primary" href="/admin/#social">Open Social team</a><a class="btn" href="${SOURCE}" target="_blank" rel="noopener noreferrer">Read the original guide <span aria-hidden="true">↗</span></a></div>
        <p class="sm-credit">Adapted from <a href="${SOURCE}" target="_blank" rel="noopener noreferrer">AI Native Social Media Agent Team</a> by <a href="https://www.linkedin.com/in/meghanify/" target="_blank" rel="noopener noreferrer">Megha Sharma</a>, co-founder of <a href="https://www.onegtmlab.dev/" target="_blank" rel="noopener noreferrer">OneGTMLab</a>.</p>
      </div>
      <aside class="sm-state" aria-labelledby="sm-state-title">
        <span class="status status--build"><span class="glyph glyph--build" aria-hidden="true"></span>Harness scaffolded</span>
        <h4 id="sm-state-title">Ready for product setup</h4>
        <p>Templates, controls and the drafting workflow are in place. Choose a product, complete its brand inputs and verify worker health plus one complete run in Growth Studio. Live integrations remain unverified.</p>
        <dl class="sm-counts"><div><dt>Agent roles</dt><dd>9</dd></div><div><dt>Event playbooks</dt><dd>8</dd></div><div><dt>Brand templates</dt><dd>27</dd></div></dl>
        <p class="sm-state-foot">Current mode: weekly exports, draft files and manual handoff. No live posting or email sending.</p>
      </aside>
    </div>
    <div class="sm-boundary"><strong>How this fits Athem</strong><p>This product team is separate from the four existing <code>social-*</code> client agents shown above. Those agents and the agency total remain unchanged. A reporting line from the social orchestrator to the Chief of Staff is a <strong>proposed integration, pending implementation</strong>.</p></div>
    <nav class="sm-jump" aria-label="Social media harness topics"><a href="#sm-team">Team</a><a href="#sm-loop">Workflow</a><a href="#sm-playbooks">Playbooks</a><a href="#sm-brand">Brand OS</a><a href="#sm-tools">Tools</a><a href="#sm-controls">Controls</a><a href="#sm-results">Results</a><a href="#sm-ready">First run</a></nav>
    <div class="sm-details">
      ${detail('01', 'sm-team', 'Nine roles, one route for handoffs', 'The social orchestrator is distinct from the Chief of Staff.', `
        <p>Departments do not brief each other. Every return goes through the social orchestrator, which selects the next department. Each handoff includes a file path, check results and anything blocked.</p>
        <div class="sm-team-grid">${TEAM.map(([id, name, job], i) => `<article class="sm-role${i === 0 ? ' sm-role--lead' : ''}"><h4>${esc(name)}</h4><p class="sm-ident">${esc(id)}</p><p>${esc(job)}</p></article>`).join('')}</div>
      `)}
      ${detail('02', 'sm-loop', 'The operating loop and seven zones', 'Evidence becomes a brief, then a checked draft and an owner decision.', `
        <ol class="sm-moves">${MOVES.map(([name, desc]) => `<li><strong>${esc(name)}</strong><p>${esc(desc)}</p></li>`).join('')}</ol>
        <p class="sm-callout">Approval is checked before scheduling. The guide calls its sixth move “Approves”; this does not authorize scheduling an unapproved draft. In this installation, a slot produces a paste-ready handoff, not a live scheduled post.</p>
        <p>Each candidate receives 0–3 for urgency, fit and evidence, totaling 0–9. Evidence zero removes it from the plan. Events come first; remaining work fills available slots. Ties favor the work that needs less owner involvement.</p>
        <h4>Seven conceptual zones</h4><dl class="sm-zone-list">${ZONES.map(([name, desc]) => `<div><dt>${esc(name)}</dt><dd>${esc(desc)}</dd></div>`).join('')}</dl>
      `)}
      ${detail('03', 'sm-playbooks', 'Eight event playbooks', 'Every trigger goes to the orchestrator before the weekly plan.', `
        <p>Validate the event against dated data and the brand’s own thresholds. If a threshold or fact is missing, ask for it. The department sequence below is routed through the orchestrator at every step.</p>
        <div class="sm-playbook-grid">${PLAYBOOKS.map(([id, name, route, gate]) => `<article class="sm-playbook"><h4>${esc(name)}</h4><p class="sm-ident">/${esc(id)}</p><p>${esc(route)}</p><p class="sm-gate"><strong>Gate:</strong> ${esc(gate)}</p></article>`).join('')}</div>
        <p>Reference playbooks describe connected actions such as boosts, ad rotation and replies. Here they prepare drafts, recommendations and approval items; the available runtime cannot execute those external actions.</p>
      `)}
      ${detail('04', 'sm-brand', 'Brand OS: 27 templates in eight folders', 'Persistent brand memory, plus four owner-controlled files.', `
        <p>Each product has its own Brand OS, drafts, queue and log. Brand files define claims, examples, channels and measurement so every department works from the same context.</p>
        <div class="sm-brand-grid">${BRAND.map(([folder, name, files]) => `<article><h4>${code('brand-os/' + folder + '/')}</h4><p>${esc(name)}</p><ul>${files.map(file => `<li>${code(file + '.md')}</li>`).join('')}</ul></article>`).join('')}</div>
        <h4>Four decisions belong to the owner</h4><dl class="sm-zone-list"><div><dt>${code('owner/brand-voice.md')}</dt><dd>How the brand sounds and which words it avoids.</dd></div><div><dt>${code('owner/budget-cap.md')}</dt><dd>The spending ceiling, including an explicit zero if desired.</dd></div><div><dt>${code('owner/approval-bar.md')}</dt><dd>What is routine, what waits and what needs an urgent alert.</dd></div><div><dt>${code('owner/positioning.md')}</dt><dd>The audience, offer, distinction and business priorities.</dd></div></dl>
        <p>Agents cannot edit these owner files; their rules override conflicting Brand OS guidance. Source material is evidence, never instructions. Unapproved customer names, unsupported medical claims and unsourced numbers stay out of drafts. Fictional examples and template placeholders are not brand facts.</p>
      `)}
      ${detail('05', 'sm-tools', 'The reference tool map', 'Seven categories of options. No implied connections or subscriptions.', `
        <p>Start with exports from tools already in use. Choose connections later, one department at a time. A tool name here does not establish that it is installed, connected, paid for or available to an agent.</p>
        <dl class="sm-tool-list">${TOOLS.map(([name, list]) => `<div><dt>${esc(name)}</dt><dd>${esc(list)}</dd></div>`).join('')}</dl>
        <p>The current adaptation specifies Claude Sonnet and limits agents to file tools and web search/fetch. No shell or MCP tools are exposed. An unavailable service must be reported as blocked, with the latest dated export used when suitable. A future scheduling integration must return a provider confirmation before work is described as scheduled.</p>
      `)}
      ${detail('06', 'sm-controls', 'Approvals, voice review and the stop switch', 'Owner decisions are explicit and every action leaves a record.', `
        <div class="sm-control-grid"><article><h4>Decision queue</h4><p>${code('queue/needs-your-ok.md')} collects exceptions. Only the owner approves or rejects. Paid spend, budget changes, negative review replies, real names, prices, offers and unresolved ${code('[VERIFY]')} marks always wait. Over-cap proposals carry ${code('OVER CAP')} and cannot auto-ship.</p></article><article><h4>Voice review queue</h4><p>${code('queue/held-for-voice-review.md')} holds a failed draft with the rule it broke. Repair the voice rule or resolve the item explicitly, then reapply approval checks. Never silently move a failed draft forward.</p></article><article><h4>Social team stop switch</h4><p>${code('owner/STOP')} blocks new steps and stops the running social agent. Only the owner can clear it. This switch covers the social team, not every Growth Studio service.</p></article><article><h4>Append-only activity log</h4><p>${code('logs/activity.md')} records writes, handoffs, queue changes, decisions and stops with time, agent, action and file. Earlier entries stay intact. Revised drafts receive new versions.</p></article></div>
        <p class="sm-callout">The current runtime cannot post, send email or spend. Publishing produces ${code('[PASTE]')} drafts for the owner, or hands them to Content studio, where the exact revision must be approved before existing channel adapters can publish.</p>
      `)}
      ${detail('07', 'sm-results', 'Measure outcomes and the cost of earning them', 'A sourced weekly note that improves the following week.', `
        <p>Define one north-star result, a source and target for each department, and a normal comparison period per channel. The weekly report covers results versus last week, KPI targets, winning and weak content, margin concerns, and missing or stale data.</p>
        <div class="sm-formulas"><p><strong>Channel cost</strong><span>Tools + ads + hours × hourly cost</span></p><p><strong>Cost per result</strong><span>Total cost ÷ credited results</span></p><p><strong>Margin</strong><span>Credited result value − total cost</span></p></div>
        <p>Choose and date one attribution model: first touch, last touch, equal split or customer-reported source. Define the lookback window and result value. Unknown sources stay unknown; missing cost or value prevents a margin claim. Budget recommendations return to the owner.</p>
        <p>Outgoing links carry ${code('utm_source')} (platform), ${code('utm_medium')} (channel type), ${code('utm_campaign')} (dated topic) and ${code('utm_content')} (calendar ID). Record blind spots such as private sharing and offline conversions instead of claiming complete attribution.</p>
      `)}
      ${detail('08', 'sm-ready', 'First-run readiness, in order', 'A sequence to prove one product before expanding.', `
        <ol class="sm-readiness"><li><strong>Choose one product.</strong> Initialize its Social team workspace in Growth Studio. Keep every product’s brand inputs, files and queue isolated.</li><li><strong>Complete the seven required files.</strong> Fill all four owner files plus ${code('voice-guide.md')}, ${code('tone-rules.md')} and ${code('content-calendar.md')}. Remaining ${code('[FILL IN: ...]')} prompts block the run before a model is called; the owner must also ensure these files contain meaningful rules.</li><li><strong>Add dated weekly exports.</strong> Bring search, social insights, reviews, mentions, conversations and results into the relevant Brand OS folders. Establish the calendar and measurable thresholds; identify unavailable evidence.</li><li><strong>Confirm controls and worker health.</strong> Check the selected product, owner permissions, queue and stop state. The runtime enforces Sonnet only, a $2 limit per step and $8 per run; these execution limits are separate from the brand’s marketing budget.</li><li><strong>Run one planning loop.</strong> Review scored jobs, the cut line and departmental briefs. Hand one brief to Content engine and inspect its source list, three hooks, voice result and verification marks.</li><li><strong>Exercise the owner gate.</strong> Approve or reject an item, rerun the orchestrator and inspect the log and decided queue. A ready draft becomes a manual paste or an exact-revision Content studio handoff.</li><li><strong>Test one event, then review the week.</strong> Use the thin-calendar playbook, inspect the results note and resolve missing data. Verify an end-to-end run before treating the team as live; add integrations only when their permissions and behavior are proven.</li></ol>
        <p>Passing the seven-file readiness check is only the starting gate. Actual positioning, approved claims, assets, channel rules and dated evidence must support each brief. Missing proof stays missing; the team cannot invent it to finish a run.</p>
        <div class="sm-actions"><a class="btn btn--primary" href="/admin/#social">Configure the first product</a></div>
      `)}
      ${detail('09', 'sm-sources', 'Original source library', '44 companion pages: setup, departments, templates, tools and weekly operations.', `
        <p>This page is an Athem-specific summary and operating map. The linked guide contains the original setup instructions, project rules, agents, playbooks and file templates.</p>
        <ul class="sm-source-list">${SOURCE_LIBRARY.map(({title, url}) => `<li><a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(title)}<span class="visually-hidden"> (opens in a new tab)</span></a></li>`).join('')}</ul>
      `)}
    </div>`;

  // Topic links open the corresponding native disclosure before scrolling to it.
  target.querySelectorAll('.sm-jump a').forEach(link => {
    link.addEventListener('click', () => {
      const panel = document.getElementById(link.hash.slice(1));
      if (panel instanceof HTMLDetailsElement) panel.open = true;
    });
  });
  const hashPanel = document.getElementById(window.location.hash.slice(1));
  if (hashPanel instanceof HTMLDetailsElement && target.contains(hashPanel)) hashPanel.open = true;
}

// SOURCE_LIBRARY is generated from the inspected guide manifest at build time.
const SOURCE_LIBRARY = [
  {
    "title": "What this system does and what it hands you",
    "url": "https://dandy-bug-77c.notion.site/What-this-system-does-and-what-it-hands-you-402a1f985212813893e5eedb05a00175?pvs=25"
  },
  {
    "title": "How the system works: the 7 zones",
    "url": "https://dandy-bug-77c.notion.site/How-the-system-works-the-7-zones-402a1f98521281efbbd0d4361f3a3c12?pvs=25"
  },
  {
    "title": "What you need before you start",
    "url": "https://dandy-bug-77c.notion.site/What-you-need-before-you-start-402a1f985212813f9c7fc1719ee304c3?pvs=25"
  },
  {
    "title": "Install the project in Claude Code",
    "url": "https://dandy-bug-77c.notion.site/Install-the-project-in-Claude-Code-402a1f985212812d9c68fdd2d5dc9cc6?pvs=25"
  },
  {
    "title": "Your first run end to end",
    "url": "https://dandy-bug-77c.notion.site/Your-first-run-end-to-end-402a1f985212815ab9a0e9a672aee351?pvs=25"
  },
  {
    "title": "CLAUDE.md: the rules every agent follows",
    "url": "https://dandy-bug-77c.notion.site/CLAUDE-md-the-rules-every-agent-follows-402a1f98521281af9b82edc287b72c4e?pvs=25"
  },
  {
    "title": "The Orchestrator agent",
    "url": "https://dandy-bug-77c.notion.site/The-Orchestrator-agent-402a1f98521281f4922afaad66369cb8?pvs=25"
  },
  {
    "title": "Owner inputs: voice, budget, approval bar, positioning",
    "url": "https://dandy-bug-77c.notion.site/Owner-inputs-voice-budget-approval-bar-positioning-402a1f985212816eb68cf3077c0983ad?pvs=25"
  },
  {
    "title": "Search visibility",
    "url": "https://dandy-bug-77c.notion.site/Search-visibility-402a1f98521281c5ad43f894473f5149?pvs=25"
  },
  {
    "title": "Market radar",
    "url": "https://dandy-bug-77c.notion.site/Market-radar-402a1f98521281548d31cc2498d9ab99?pvs=25"
  },
  {
    "title": "Content engine",
    "url": "https://dandy-bug-77c.notion.site/Content-engine-402a1f98521281e3a8bff5f7061dfc3c?pvs=25"
  },
  {
    "title": "Creative studio",
    "url": "https://dandy-bug-77c.notion.site/Creative-studio-402a1f9852128153b7d1e1dbbd2e95de?pvs=25"
  },
  {
    "title": "Publishing & social",
    "url": "https://dandy-bug-77c.notion.site/Publishing-social-402a1f98521281ec9efdef950e1a7225?pvs=25"
  },
  {
    "title": "Reviews & reputation",
    "url": "https://dandy-bug-77c.notion.site/Reviews-reputation-402a1f985212814f8464dabf79b2b3d2?pvs=25"
  },
  {
    "title": "Leads & conversations",
    "url": "https://dandy-bug-77c.notion.site/Leads-conversations-402a1f985212813aa582d89dc54a9e3d?pvs=25"
  },
  {
    "title": "Results & ROI",
    "url": "https://dandy-bug-77c.notion.site/Results-ROI-402a1f9852128102a607e555ce898d4c?pvs=25"
  },
  {
    "title": "Search demand spikes",
    "url": "https://dandy-bug-77c.notion.site/Search-demand-spikes-402a1f985212814b8194c7debede8016?pvs=25"
  },
  {
    "title": "Competitor drops a promo",
    "url": "https://dandy-bug-77c.notion.site/Competitor-drops-a-promo-402a1f98521281e4a3d9de392f1e9673?pvs=25"
  },
  {
    "title": "One star review lands",
    "url": "https://dandy-bug-77c.notion.site/One-star-review-lands-402a1f98521281e2b444f2db699ff179?pvs=25"
  },
  {
    "title": "Content calendar looks thin",
    "url": "https://dandy-bug-77c.notion.site/Content-calendar-looks-thin-402a1f98521281279e4ac80ae7503c1e?pvs=25"
  },
  {
    "title": "A post goes viral",
    "url": "https://dandy-bug-77c.notion.site/A-post-goes-viral-402a1f9852128180bdebd8d715b2a242?pvs=25"
  },
  {
    "title": "Ranking drops a page",
    "url": "https://dandy-bug-77c.notion.site/Ranking-drops-a-page-402a1f985212814184bde669d788b7f4?pvs=25"
  },
  {
    "title": "Ad creative fatigues",
    "url": "https://dandy-bug-77c.notion.site/Ad-creative-fatigues-402a1f9852128103b96ed908cd1854de?pvs=25"
  },
  {
    "title": "DM or lead at 11pm",
    "url": "https://dandy-bug-77c.notion.site/DM-or-lead-at-11pm-402a1f98521281f980d5d373a7d06347?pvs=25"
  },
  {
    "title": "Brand OS: how the folder works",
    "url": "https://dandy-bug-77c.notion.site/Brand-OS-how-the-folder-works-402a1f98521281c6b86bd0d129cc51e8?pvs=25"
  },
  {
    "title": "/brand-brain",
    "url": "https://dandy-bug-77c.notion.site/brand-brain-402a1f98521281e38ca6e9d0e7b3c7ed?pvs=25"
  },
  {
    "title": "/signals-seo",
    "url": "https://dandy-bug-77c.notion.site/signals-seo-402a1f98521281358fe7df5d2fd02901?pvs=25"
  },
  {
    "title": "/content",
    "url": "https://dandy-bug-77c.notion.site/content-402a1f98521281e9a6cfce8e315b0808?pvs=25"
  },
  {
    "title": "/creative",
    "url": "https://dandy-bug-77c.notion.site/creative-402a1f985212818bb032c58aeeb4c3b3?pvs=25"
  },
  {
    "title": "/social",
    "url": "https://dandy-bug-77c.notion.site/social-402a1f98521281d7a14cd10c6cd3c03c?pvs=25"
  },
  {
    "title": "/reputation",
    "url": "https://dandy-bug-77c.notion.site/reputation-402a1f985212810893bac7ff32401374?pvs=25"
  },
  {
    "title": "/conversation",
    "url": "https://dandy-bug-77c.notion.site/conversation-402a1f98521281f0affbe76c67dd78cf?pvs=25"
  },
  {
    "title": "/reporting",
    "url": "https://dandy-bug-77c.notion.site/reporting-402a1f98521281f3b4dfd9d38898de9c?pvs=25"
  },
  {
    "title": "The tool map",
    "url": "https://dandy-bug-77c.notion.site/The-tool-map-402a1f98521281a795eac4e246696927?pvs=25"
  },
  {
    "title": "Signals tools",
    "url": "https://dandy-bug-77c.notion.site/Signals-tools-402a1f9852128192a1f5d695400934fe?pvs=25"
  },
  {
    "title": "System of record tools",
    "url": "https://dandy-bug-77c.notion.site/System-of-record-tools-402a1f98521281ecb791e736f480a43d?pvs=25"
  },
  {
    "title": "Brain tools",
    "url": "https://dandy-bug-77c.notion.site/Brain-tools-402a1f98521281129912d9987b267b4b?pvs=25"
  },
  {
    "title": "Search and market tools",
    "url": "https://dandy-bug-77c.notion.site/Search-and-market-tools-402a1f9852128127a200c6a905c48cbc?pvs=25"
  },
  {
    "title": "Content and creative tools",
    "url": "https://dandy-bug-77c.notion.site/Content-and-creative-tools-402a1f985212812fa420e355eb2301da?pvs=25"
  },
  {
    "title": "Publishing, reviews and leads tools",
    "url": "https://dandy-bug-77c.notion.site/Publishing-reviews-and-leads-tools-402a1f985212811db1d5feab1e6daa24?pvs=25"
  },
  {
    "title": "Data and observability tools",
    "url": "https://dandy-bug-77c.notion.site/Data-and-observability-tools-402a1f98521281b880bae221966d83d4?pvs=25"
  },
  {
    "title": "The weekly loop",
    "url": "https://dandy-bug-77c.notion.site/The-weekly-loop-402a1f985212814a9214f99130928d45?pvs=25"
  },
  {
    "title": "Approvals queues and the kill switch",
    "url": "https://dandy-bug-77c.notion.site/Approvals-queues-and-the-kill-switch-402a1f985212812d9c62e1676affdc55?pvs=25"
  },
  {
    "title": "Measuring what it earns",
    "url": "https://dandy-bug-77c.notion.site/Measuring-what-it-earns-402a1f985212812e804bc46180921aa4?pvs=25"
  }
];
renderSocialArchitecture();
