import test from 'node:test';
import assert from 'node:assert/strict';
import {
  normalizeWorkspace,
  renderCompanies,
  openCompanyEditor,
  handleCompanyAction,
} from '../companies.js';

const TIME = '2026-11-14T18:00:00.000Z';
const CHANNELS = ['linkedin', 'instagram', 'tiktok', 'x', 'youtube'];
const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, character => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[character]));
const decodeHTML = value => value.replace(/&quot;/g, '"').replace(/&#39;/g, "'")
  .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');

function element(value = '') {
  return {
    value, innerHTML: '', attributes: {}, listeners: {},
    setAttribute(name, next) { this.attributes[name] = next; },
    addEventListener(name, listener) { this.listeners[name] = listener; },
    input(next) { this.value = next; this.listeners.input?.(); },
  };
}

// A form-only boundary: callbacks are captured and save/select are local call logs.
// No Firebase, browser globals, worker commands or remote persistence are involved.
function context(records = [], currentId = records[0]?.id || '') {
  const elements = new Map([['view', element()]]);
  const get = id => {
    assert.ok(elements.has(id), `Expected form element ${id}`);
    return elements.get(id);
  };
  const register = (label, id, value = '', type = 'text', required = true) => {
    const field = element(String(value ?? ''));
    field.required = required;
    elements.set(id, field);
    return `<input id="${id}" value="${escapeHTML(value)}">`;
  };
  const ctx = {
    $: get, esc: escapeHTML, now: () => TIME,
    products: () => records, currentId: () => currentId,
    field: register,
    area: (label, id, value = '', required = true) => register(label, id, value, 'text', required),
    saved: [], selected: [], editor: null,
    openEditor(title, body, save, label) {
      // Native selects use the marked option, or their first option by default.
      for (const match of body.matchAll(/<select id="([^"]+)"[^>]*>([\s\S]*?)<\/select>/g)) {
        const options = [...match[2].matchAll(/<option value="([^"]*)"([^>]*)>/g)];
        const choice = options.find(option => /\bselected\b/.test(option[2])) || options[0];
        elements.set(match[1], element(decodeHTML(choice?.[1] || '')));
      }
      this.editor = { title, body, save, label };
    },
    async save(...args) { this.saved.push(structuredClone(args)); },
    select(...args) { this.selected.push(args); },
    notice() {},
  };
  return ctx;
}

function readyCreate(ctx, overrides = {}) {
  openCompanyEditor(ctx);
  const values = { companyName: 'New Company', companyGoal: 'Ship the next useful product.', ...overrides };
  for (const [id, value] of Object.entries(values)) ctx.$(id).value = value;
  return ctx.editor.save;
}

function deepFreeze(value) {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    Object.values(value).forEach(deepFreeze);
    Object.freeze(value);
  }
  return value;
}

test('legacy normalization preserves account identity, connections, history and custom metadata without mutating its input', () => {
  const source = deepFreeze({
    id: 'legacy', name: 'Existing Brand', customMetadata: { system: 'original' },
    accounts: {
      linkedin: {
        accountId: 'existing-account', url: 'https://www.linkedin.com/company/existing/',
        connected: true, adapter: 'native', connectionLabel: 'Verified account',
        needs: ['Review profile'], stepsDone: [0], handleCandidates: ['existing'],
      },
      customChannel: { accountId: 'custom-identity', connected: true },
    },
    feedback: [{ note: 'Retain our voice.' }], metrics: [{ clicks: 7 }],
    schedule: { enabled: true, lastRunAt: TIME },
  });
  const before = structuredClone(source);
  const result = normalizeWorkspace(source);
  assert.deepEqual(source, before);
  assert.notEqual(result, source);
  assert.notEqual(result.accounts, source.accounts);
  assert.notEqual(result.accounts.linkedin, source.accounts.linkedin);
  assert.notEqual(result.schedule, source.schedule);
  for (const key of ['accountId', 'url', 'connected', 'adapter', 'connectionLabel', 'needs', 'stepsDone', 'handleCandidates']) {
    assert.deepEqual(result.accounts.linkedin[key], source.accounts.linkedin[key]);
  }
  assert.deepEqual(result.accounts.customChannel, source.accounts.customChannel);
  assert.deepEqual(result.feedback, source.feedback);
  assert.deepEqual(result.metrics, source.metrics);
  assert.deepEqual(result.customMetadata, source.customMetadata);
  assert.deepEqual(result.schedule, source.schedule);
  assert.equal(result.entityType, '');
  assert.deepEqual(result.facts, []);
  assert.deepEqual(result.pillars, []);
  assert.deepEqual(result.forbidden, []);
});

test('a new workspace has manual disconnected channels and scheduling off', () => {
  const result = normalizeWorkspace({ id: 'new', name: 'New Company' });
  assert.deepEqual(Object.keys(result.accounts), CHANNELS);
  assert.equal(result.schedule.enabled, false);
  for (const account of Object.values(result.accounts)) {
    assert.equal(account.connected, false);
    assert.equal(account.adapter, 'manual');
    assert.equal(account.status, 'not_created');
    assert.equal(account.accountId, '');
    assert.equal(account.url, '');
    assert.deepEqual(account.needs, []);
    assert.deepEqual(account.stepsDone, []);
  }
});

test('creating without a website generates an ID and never inherits an existing company’s accounts', async () => {
  const existing = {
    id: 'serasona', name: 'Existing Company',
    accounts: { linkedin: { accountId: 'private-existing-account', connected: true, url: 'https://example.com/profile' } },
  };
  const ctx = context([existing]);
  openCompanyEditor(ctx);
  assert.equal(ctx.$('companyWebsite').required, false);
  ctx.$('companyName').input('Élan Ventures');
  assert.equal(ctx.$('companyNewId').value, 'elan-ventures');
  ctx.$('companyGoal').value = '  Launch the pilot.  ';
  await ctx.editor.save();
  assert.equal(ctx.saved.length, 1);
  const [id, record, options] = ctx.saved[0];
  assert.equal(id, 'elan-ventures');
  assert.equal(record.id, id);
  assert.equal(record.website, '');
  assert.equal(record.goal, 'Launch the pilot.');
  assert.equal(record.createdAt, TIME);
  assert.equal(record.updatedAt, TIME);
  assert.equal(record.entityType, 'company');
  assert.equal(record.timezone, 'America/Chicago');
  assert.equal(record.schedule.enabled, false);
  assert.deepEqual(options, { create: true });
  for (const account of Object.values(record.accounts)) {
    assert.equal(account.accountId, '');
    assert.equal(account.url, '');
    assert.equal(account.connected, false);
    assert.equal(account.adapter, 'manual');
  }
  assert.deepEqual(ctx.selected, [['elan-ventures', 'overview']]);
  assert.equal(existing.accounts.linkedin.accountId, 'private-existing-account');
});

test('an explicitly edited ID survives subsequent name changes', async () => {
  const ctx = context();
  openCompanyEditor(ctx);
  ctx.$('companyName').input('First Name');
  ctx.$('companyNewId').input('chosen-id');
  ctx.$('companyName').input('Second Name');
  ctx.$('companyGoal').value = 'Run a pilot.';
  await ctx.editor.save();
  assert.equal(ctx.saved[0][0], 'chosen-id');
});

test('editing sends a metadata-only patch and leaves existing account and history fields out of the write', async () => {
  const source = deepFreeze({
    id: 'current', name: 'Original', goal: 'Original goal', entityType: 'company',
    createdAt: '2026-01-01T00:00:00.000Z',
    accounts: { linkedin: { accountId: 'keep-me', connected: true } },
    pillars: ['Original pillar'], facts: [{ claim: 'Supported fact' }], feedback: [{ note: 'Keep this.' }],
    customMetadata: { keep: true },
  });
  const ctx = context([source]);
  openCompanyEditor(ctx, 'current');
  ctx.$('companyName').value = 'Updated name';
  ctx.$('companyGoal').value = 'Updated goal';
  await ctx.editor.save();
  const [id, patch, options] = ctx.saved[0];
  assert.equal(id, 'current');
  assert.deepEqual(options, { create: false });
  assert.equal(patch.name, 'Updated name');
  assert.equal(patch.goal, 'Updated goal');
  assert.equal(patch.updatedAt, TIME);
  assert.deepEqual(Object.keys(patch).sort(), [
    'name', 'website', 'timezone', 'goal', 'entityType', 'parentCompanyId',
    'priority', 'status', 'operatingOwner', 'positioning', 'audience', 'voice', 'updatedAt',
  ].sort());
  for (const key of ['id', 'createdAt', 'accounts', 'schedule', 'pillars', 'facts', 'feedback', 'customMetadata']) {
    assert.equal(Object.hasOwn(patch, key), false, `${key} must remain in the stored record`);
  }
  assert.deepEqual(ctx.selected, []);
  assert.equal(source.accounts.linkedin.accountId, 'keep-me');
});

test('duplicate workspace IDs are rejected before any save', async () => {
  const ctx = context([{ id: 'already-here', name: 'Original' }]);
  const save = readyCreate(ctx, { companyNewId: 'already-here' });
  await assert.rejects(save, /already exists/i);
  assert.deepEqual(ctx.saved, []);
  assert.deepEqual(ctx.selected, []);
});

test('company websites require HTTPS and reject embedded credentials', async t => {
  for (const website of ['http://example.com', 'javascript:alert(1)', 'not a URL', 'https://user:secret@example.com/', 'https://user@example.com/']) {
    await t.test(website, async () => {
      const ctx = context();
      const save = readyCreate(ctx, { companyWebsite: website });
      await assert.rejects(save, /HTTPS/i);
      assert.deepEqual(ctx.saved, []);
    });
  }
});

test('invalid or empty time zones are rejected before any save', async t => {
  for (const timezone of ['Invalid/Nowhere', '']) {
    await t.test(timezone || 'empty', async () => {
      const ctx = context();
      const save = readyCreate(ctx, { companyTimezone: timezone });
      await assert.rejects(save, /valid time zone/i);
      assert.deepEqual(ctx.saved, []);
    });
  }
});

test('parent selection rejects cycles, missing companies and product parents', async t => {
  const records = [
    { id: 'parent', name: 'Parent', entityType: 'company', goal: 'Parent goal' },
    { id: 'child', name: 'Child', entityType: 'company', parentCompanyId: 'parent', goal: 'Child goal' },
    { id: 'product', name: 'Product', entityType: 'product', goal: 'Product goal' },
  ];
  await t.test('a descendant cannot become the parent', async () => {
    const ctx = context(records);
    openCompanyEditor(ctx, 'parent');
    ctx.$('companyParent').value = 'child';
    await assert.rejects(ctx.editor.save, /cycle/i);
    assert.deepEqual(ctx.saved, []);
  });
  for (const parent of ['missing', 'product']) {
    await t.test(`reject ${parent} parent`, async () => {
      const ctx = context(records);
      const save = readyCreate(ctx, { companyParent: parent });
      await assert.rejects(save, /existing company/i);
      assert.deepEqual(ctx.saved, []);
    });
  }
  await t.test('a company with children cannot change into a product', async () => {
    const ctx = context(records);
    openCompanyEditor(ctx, 'parent');
    ctx.$('companyEntityType').value = 'product';
    await assert.rejects(ctx.editor.save, /child workspaces/i);
    assert.deepEqual(ctx.saved, []);
  });
});

test('company rendering escapes record text and URL attributes and never links unsafe URLs', () => {
  const name = '<img src=x onerror=alert(1)>';
  const website = 'https://example.com/?a=1&b=2';
  const ctx = context([
    { id: 'safe', name, goal: 'Grow <script>alert(1)</script>', operatingOwner: 'A & B', website },
    { id: 'unsafe', name: 'Unsafe URL', website: 'javascript:alert("x")' },
    { id: 'credential', name: 'Credentials URL', website: 'https://user:secret@example.com/' },
  ], 'safe');
  renderCompanies(ctx);
  const html = ctx.$('view').innerHTML;
  assert.ok(html.includes('&lt;img src=x onerror=alert(1)&gt;'));
  assert.ok(html.includes('Grow &lt;script&gt;alert(1)&lt;/script&gt;'));
  assert.ok(html.includes('A &amp; B'));
  assert.ok(html.includes('href="https://example.com/?a=1&amp;b=2"'));
  assert.ok(html.includes('javascript:alert(&quot;x&quot;)'));
  assert.ok(html.includes('Selected workspace'));
  assert.ok(!html.includes('<img src=x'));
  assert.ok(!html.includes('<script>'));
  assert.ok(!html.includes('href="javascript:'));
  assert.ok(!html.includes('href="https://user:secret@'));
});

test('company actions select the requested current workspace and ignore unrelated actions', () => {
  const ctx = context([{ id: 'current', name: 'Current' }, { id: 'other', name: 'Other' }], 'current');
  assert.equal(handleCompanyAction({ dataset: { companyAction: 'open', companyId: 'current' } }, ctx), true);
  assert.deepEqual(ctx.selected, [['current', 'overview']]);
  assert.equal(handleCompanyAction({ dataset: { companyAction: 'open', companyId: 'other' } }, ctx), true);
  assert.deepEqual(ctx.selected[1], ['other', 'overview']);
  assert.equal(handleCompanyAction({ dataset: { action: 'unrelated' } }, ctx), false);
  assert.throws(() => handleCompanyAction({ dataset: { companyAction: 'open', companyId: 'missing' } }, ctx), /no longer available/i);
  assert.equal(ctx.selected.length, 2);
});
