// Company registry UI. Persistence and owner authorization belong to the dashboard.
const CHANNELS = {
  linkedin: { type: 'Company Page', home: 'https://www.linkedin.com/' },
  instagram: { type: 'Professional account', home: 'https://www.instagram.com/' },
  tiktok: { type: 'Business account', home: 'https://www.tiktok.com/' },
  x: { type: 'Brand account', home: 'https://x.com/' },
  youtube: { type: 'Brand channel', home: 'https://www.youtube.com/' },
};
const ARRAY_FIELDS = ['pillars', 'facts', 'forbidden', 'feedback', 'trendEvidence', 'metrics', 'savedSources', 'competitors'];
const ownObject = value => value && typeof value === 'object' && !Array.isArray(value) ? value : {};
const slug = value => String(value || '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 64).replace(/-+$/g, '');
const entityLabel = type => ({ company: 'Company', product: 'Product or brand' }[type] || 'Existing workspace');

function blankAccount(channel, website = '') {
  const { type, home } = CHANNELS[channel];
  return { type, createUrl: home, profileUrl: home, needs: [], stepsDone: [], handle: '', handleCandidates: [], bio: '', availability: 'Not checked', status: 'not_created', adapter: 'manual', connected: false, accountId: '', url: '', website };
}

export function normalizeWorkspace(record = {}) {
  const source = ownObject(record);
  const result = { id: '', name: '', website: '', timezone: 'America/Chicago', goal: '', positioning: '', audience: '', voice: '', entityType: '', parentCompanyId: '', priority: 'normal', status: 'setup', operatingOwner: '', ...source };
  for (const key of ARRAY_FIELDS) result[key] = Array.isArray(source[key]) ? source[key] : [];
  result.schedule = { enabled: false, ...ownObject(source.schedule) };
  const savedAccounts = ownObject(source.accounts);
  result.accounts = { ...savedAccounts };
  for (const channel of Object.keys(CHANNELS)) {
    const saved = ownObject(savedAccounts[channel]);
    result.accounts[channel] = { ...blankAccount(channel, result.website || ''), ...saved };
    for (const key of ['needs', 'stepsDone', 'handleCandidates']) {
      result.accounts[channel][key] = Array.isArray(saved[key]) ? saved[key] : [];
    }
  }
  return result;
}

function workspaceList(ctx) {
  return (ctx.products() || []).map(normalizeWorkspace);
}

function websiteLink(value, esc) {
  if (!value) return '<span class="company-muted">No website recorded</span>';
  try {
    const url = new URL(value);
    if (url.protocol === 'https:' && !url.username && !url.password) return `<a href="${esc(url.href)}" target="_blank" rel="noopener noreferrer">${esc(url.hostname)}<span class="visually-hidden"> (opens in a new tab)</span></a>`;
  } catch { /* Existing invalid data stays visible as text. */ }
  return `<span class="company-muted">${esc(value)}</span>`;
}

export function renderCompanies(ctx) {
  const { $, esc } = ctx;
  const records = workspaceList(ctx);
  const companies = records.filter(record => record.entityType === 'company').length;
  const products = records.filter(record => record.entityType === 'product').length;
  $('view').innerHTML = `<div class="company-registry">
    <div class="company-intro"><div><p class="lead">Every company, with its own workspace.</p><p>Keep each company or product’s goals, brand context, channels and work together. Open a workspace to manage its agents, content and Social team.</p></div><button type="button" class="primary" data-company-action="add">Add a company</button></div>
    <dl class="company-counts"><div><dt>Companies</dt><dd>${companies}</dd></div><div><dt>Products and brands</dt><dd>${products}</dd></div><div><dt>Existing workspaces</dt><dd>${records.length - companies - products}</dd></div></dl>
    <p class="company-note">“Active” is an organizational status you set. Channel connections, worker health and completed runs are verified separately inside each workspace.</p>
    ${records.length ? `<div class="company-list">${records.map(record => {
      const parent = records.find(item => item.id === record.parentCompanyId);
      const current = record.id === ctx.currentId();
      const name = record.name || record.id || 'Unnamed workspace';
      return `<article class="company-card${current ? ' company-card--selected' : ''}" aria-labelledby="company-name-${esc(record.id)}">
        <div class="company-card-heading"><div><p class="company-kicker">${esc(entityLabel(record.entityType))}${parent ? ` · ${esc(parent.name || parent.id)}` : record.parentCompanyId ? ' · Parent needs review' : ''}</p><h2 id="company-name-${esc(record.id)}">${esc(name)}</h2><p class="company-id">${esc(record.id)}</p></div><div class="company-badges"><span class="company-status">${esc(record.status === 'active' ? 'Active' : record.status === 'setup' ? 'Setup' : record.status || 'Setup')}</span>${current ? '<span class="company-current">Selected workspace</span>' : ''}</div></div>
        <p class="company-goal">${esc(record.goal || 'Add this workspace’s goal to guide its priorities.')}</p>
        <dl class="company-facts"><div><dt>Website</dt><dd>${websiteLink(record.website, esc)}</dd></div><div><dt>Operating owner</dt><dd>${esc(record.operatingOwner || 'Not assigned')}</dd></div><div><dt>Priority</dt><dd>${esc(({ high: 'High', normal: 'Normal', low: 'Low' })[record.priority] || record.priority || 'Normal')}</dd></div><div><dt>Time zone</dt><dd>${esc(record.timezone || 'Not set')}</dd></div></dl>
        <div class="company-actions"><button type="button" class="primary" data-company-action="open" data-company-id="${esc(record.id)}">Open workspace<span class="visually-hidden"> for ${esc(name)}</span></button><button type="button" data-company-action="edit" data-company-id="${esc(record.id)}">Edit details<span class="visually-hidden"> for ${esc(name)}</span></button></div>
      </article>`;
    }).join('')}</div>` : '<div class="company-empty"><h2>Add your first company</h2><p>Start with its name and current goal. A website is optional. You can add products and brands under a company as your registry grows.</p><button type="button" class="primary" data-company-action="add">Add a company</button></div>'}
  </div>`;
}

function selectField(label, id, options, current, esc) {
  const choices = [...options];
  if (!choices.some(([value]) => value === current)) choices.unshift([current, `Existing: ${current}`]);
  return `<label>${esc(label)}<select id="${id}">${choices.map(([value, text]) => `<option value="${esc(value)}"${value === current ? ' selected' : ''}>${esc(text)}</option>`).join('')}</select></label>`;
}

function validateParent(records, id, parentId) {
  if (!parentId) return;
  const parent = records.find(record => record.id === parentId);
  if (!parent || parent.entityType !== 'company') throw Error('Choose an existing company as the parent, or choose no parent.');
  const seen = new Set([id]);
  let cursor = parentId;
  while (cursor) {
    if (seen.has(cursor)) throw Error('The parent relationship would create a cycle. Choose another company.');
    seen.add(cursor);
    cursor = records.find(record => record.id === cursor)?.parentCompanyId || '';
  }
}

export function openCompanyEditor(ctx, id = null) {
  const { $, esc, field, area } = ctx;
  const records = workspaceList(ctx);
  const existing = id === null ? null : records.find(record => record.id === id);
  if (id !== null && !existing) throw Error('That workspace is no longer available. Refresh the registry.');
  const creating = !existing;
  const record = existing || normalizeWorkspace({ entityType: 'company' });
  const parents = records.filter(item => item.entityType === 'company' && item.id !== id);
  const body = `<div class="company-editor">
    <p>${creating ? 'Create a separate workspace for a company, product or brand. Its channels begin as uncreated manual accounts, with scheduling off.' : 'Update this workspace’s details. Its ID, saved work, account identities and connections stay with the workspace.'}</p>
    <div class="company-form-grid">${field('Name', 'companyName', record.name)}${selectField('Workspace type', 'companyEntityType', [['company', 'Company'], ['product', 'Product or brand'], ...(!creating && !record.entityType ? [['', 'Existing workspace']] : [])], record.entityType, esc)}</div>
    ${creating ? `${field('Workspace ID, generated from the name and editable', 'companyNewId', '', 'text', false)}<p class="company-help" id="companyIdHelp">Lowercase letters, numbers and hyphens, up to 64 characters. This ID stays fixed after creation.</p>` : `<p class="company-fixed-id">Workspace ID: <code>${esc(record.id)}</code></p>`}
    ${area('Current goal', 'companyGoal', record.goal)}
    <div class="company-form-grid">${field('Website, optional', 'companyWebsite', record.website, 'url', false)}${field('Time zone', 'companyTimezone', record.timezone || 'America/Chicago')}</div>
    <div class="company-form-grid">${field('Operating owner, optional', 'companyOwner', record.operatingOwner, 'text', false)}${selectField('Parent company, optional', 'companyParent', [['', 'No parent company'], ...parents.map(item => [item.id, item.name || item.id])], record.parentCompanyId || '', esc)}</div>
    <div class="company-form-grid">${selectField('Priority', 'companyPriority', [['high', 'High'], ['normal', 'Normal'], ['low', 'Low']], record.priority || 'normal', esc)}${selectField('Organizational status', 'companyStatus', [['setup', 'Setup'], ['active', 'Active']], record.status || 'setup', esc)}</div>
    <p class="company-help">Status describes your operating priorities. It does not mark accounts connected or authorize posting.</p>
    <details class="company-brand-fields"${creating ? ' open' : ''}><summary>Brand context</summary><p class="company-help">Add what you know now. Each workspace keeps its own context.</p>${area('What the company or product does, optional', 'companyPositioning', record.positioning, false)}${area('Audience, optional', 'companyAudience', record.audience, false)}${area('Voice and boundaries, optional', 'companyVoice', record.voice, false)}</details>
    <p class="company-help">Saving creates no agent run, social team or platform account. You choose the next step inside the workspace.</p>
  </div>`;

  ctx.openEditor(creating ? 'Add a company or product' : `Edit ${record.name || record.id}`, body, async () => {
    const name = $('companyName').value.trim();
    const goal = $('companyGoal').value.trim();
    if (!name) throw Error('Enter a name for this workspace.');
    if (!goal) throw Error('Enter the current goal for this workspace.');
    const workspaceId = creating ? ($('companyNewId').value.trim() || slug(name)) : record.id;
    if (creating && !/^[a-z0-9][a-z0-9-]{0,63}$/.test(workspaceId)) throw Error('Use lowercase letters, numbers and hyphens for the ID, up to 64 characters.');
    const latest = workspaceList(ctx);
    if (creating && latest.some(item => item.id === workspaceId)) throw Error('That workspace ID already exists. Choose another ID.');
    let website = $('companyWebsite').value.trim();
    if (website) {
      let parsed;
      try { parsed = new URL(website); } catch { throw Error('Enter a full HTTPS website address, or leave it blank.'); }
      if (parsed.protocol !== 'https:' || parsed.username || parsed.password) throw Error('Use an HTTPS website without login credentials, or leave it blank.');
      website = parsed.href;
    }
    const timezone = $('companyTimezone').value.trim();
    try { if (!timezone) throw Error(); new Intl.DateTimeFormat('en-US', { timeZone: timezone }).format(); } catch { throw Error('Enter a valid time zone, such as America/Chicago.'); }
    const entityType = $('companyEntityType').value;
    if (!['company', 'product', ''].includes(entityType)) throw Error('Choose a company or product workspace type.');
    const parentCompanyId = $('companyParent').value;
    validateParent(latest, workspaceId, parentCompanyId);
    if (existing?.entityType === 'company' && entityType !== 'company' && latest.some(item => item.parentCompanyId === workspaceId)) throw Error('This company has child workspaces. Keep it as a company, or reassign those children first.');
    const timestamp = ctx.now();
    const patch = { name, website, timezone, goal, entityType, parentCompanyId, priority: $('companyPriority').value, status: $('companyStatus').value, operatingOwner: $('companyOwner').value.trim(), positioning: $('companyPositioning').value.trim(), audience: $('companyAudience').value.trim(), voice: $('companyVoice').value.trim(), updatedAt: timestamp };
    // Edits send metadata only. The transaction merges with the latest saved record.
    if (creating) {
      const created = normalizeWorkspace({ ...patch, id: workspaceId, createdAt: timestamp });
      await ctx.save(workspaceId, created, { create: true });
      ctx.select(workspaceId, 'overview');
    } else {
      await ctx.save(workspaceId, patch, { create: false });
    }
  }, creating ? 'Create workspace' : 'Save details');

  if (creating) {
    let touchedId = false;
    $('companyNewId').setAttribute('aria-describedby', 'companyIdHelp');
    $('companyNewId').setAttribute('maxlength', '64');
    $('companyNewId').setAttribute('spellcheck', 'false');
    $('companyNewId').addEventListener('input', () => { touchedId = true; });
    $('companyName').addEventListener('input', () => { if (!touchedId) $('companyNewId').value = slug($('companyName').value); });
  }
}

export function handleCompanyAction(button, ctx) {
  const action = button?.dataset?.companyAction;
  if (!['add', 'edit', 'open'].includes(action)) return false;
  if (action === 'add') openCompanyEditor(ctx);
  else {
    const id = button.dataset.companyId;
    if (!workspaceList(ctx).some(record => record.id === id)) throw Error('That workspace is no longer available. Refresh the registry.');
    if (action === 'edit') openCompanyEditor(ctx, id);
    else ctx.select(id, 'overview');
  }
  return true;
}
