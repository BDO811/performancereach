"""Every agent: its contract, its output check, its agent file, and every director's staffing. Plus loop data.
No model, no network.

    python3 -I _cmo-harness/tests/test_agents.py

For each agent with a contract, the test writes a valid sample output, checks it passes, then breaks it in
every way its contract forbids and checks each break is caught.
"""
import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_cmo import Base, HERE, overlay, tool  # noqa: E402

DATE = '2026-11-24'
DATA = 'loop/2026-11-23-data.md'
LINK = 'https://example.com/page?utm_campaign=sample'
OWNER_LINK = 'https://example.com/book'


def load_cc(ws):
    sys.path.insert(0, str(ws / 'tools'))
    for m in ('contracts_check', 'harness'):
        sys.modules.pop(m, None)
    import contracts_check
    sys.path.pop(0)
    return contracts_check


def fill(pattern):
    return pattern.replace('{date}', DATE).replace('{slug}', 'sample-test-output').replace('{channel}', 'instagram')


def cell(t, col, rules):
    if col in t.get('ints', {}):
        return str(t['ints'][col][0])
    if col in t.get('enums', {}):
        return t['enums'][col][0]
    if col == 'Hex' and 'hex' in rules:
        return '#1A2B3C'
    if f'links:{col}' in rules:
        return DATA
    return 'sample'


def sample(agent, spec):
    rules = spec.get('rules', [])
    if 'csv' in spec:
        return ','.join(spec['csv']) + '\n' + ','.join('x' for _ in spec['csv']) + '\n'
    link = OWNER_LINK if 'owner_link' in rules else LINK
    out = []
    if not spec.get('front_free'):
        out.append('---')
        out += [f'agent: {agent}', 'brief: B-20261124-01', f'sources: [{DATA}]']
        for k in spec.get('front', []):
            out.append(f"{k}: {spec.get('values', {}).get(k, ['sample'])[0]}")
        out += ['---', '']
    for i, sec in enumerate(spec['sections']):
        out.append(f'## {sec}')
        if spec.get('front_free') and sec == 'This week':
            for sub in ('Double down', 'Drop', 'Test'):
                out += [f'### {sub}', f'- sample item ({DATA})']
        else:
            text = f'Sample text from {DATA}.'
            if i == 0:
                text += f' Link {link} [PASTE] [SEND] [RENDER]'
            out.append(text)
        t = spec.get('table')
        if t and t['in'] == sec:
            n = max(t.get('min', 1), 1)
            out.append('| ' + ' | '.join(t['cols']) + ' |')
            out.append('|' + '---|' * len(t['cols']))
            out += ['| ' + ' | '.join(cell(t, c, rules) for c in t['cols']) + ' |' for _ in range(n)]
        out.append('')
    return '\n'.join(out)


def breaks(agent, spec, text):
    """(name, broken text, expected message part)."""
    rules = spec.get('rules', [])
    out = []
    if 'csv' in spec:
        return [('csv column', text.replace(spec['csv'][0], 'other', 1), 'missing csv columns')]
    first = spec['sections'][0]
    out.append(('section', text.replace(f'## {first}\n', f'## Not {first}\n', 1), f'missing section "## {first}"'))
    out.append(('dash', text.replace('Sample text', 'Sample — text', 1), 'dash character'))
    out.append(('banned word', text.replace('Sample text', 'Sample text exactly', 1), '"exactly"'))
    if not spec.get('front_free'):
        out.append(('front', text.replace('brief: B-20261124-01\n', ''), 'front matter needs "brief"'))
        for k, allowed in spec.get('values', {}).items():
            out.append((f'value {k}', text.replace(f'{k}: {allowed[0]}\n', f'{k}: wrong\n', 1), f'{k} must be one of'))
    t = spec.get('table')
    if t:
        head = '| ' + ' | '.join(t['cols']) + ' |'
        out.append(('table column', text.replace(head, head.replace(f'| {t["cols"][-1]} |', '| Other |')), 'missing columns'))
        if t.get('min', 1) >= 1:
            rows = re.findall(r'^\| (?!' + re.escape(t['cols'][0]) + r' \|).*\|$', text, re.M)
            body = [r for r in rows if not r.startswith('|---')]
            if t.get('min', 1) > 1:
                out.append(('too few rows', text.replace(body[-1] + '\n', '', 1), 'needs at least'))
        if t.get('max'):
            row = [r for r in re.findall(r'^\|.*\|$', text, re.M) if not r.startswith('|---') and r != head][0]
            out.append(('too many rows', text.replace(row + '\n', (row + '\n') * (t['max'] + 1), 1), 'allows at most'))
        idx = {c: i for i, c in enumerate(t['cols'])}
        row = [r for r in re.findall(r'^\|.*\|$', text, re.M) if not r.startswith('|---') and r != head][0]
        for col in list(t.get('ints', {})) + list(t.get('enums', {})):
            cells_ = [c.strip() for c in row.strip('|').split('|')]
            cells_[idx[col]] = '999999' if col in t.get('ints', {}) else 'nonsense'
            msg = 'whole number' if col in t.get('ints', {}) else 'must be one of'
            out.append((f'cell {col}', text.replace(row, '| ' + ' | '.join(cells_) + ' |', 1), msg))
    first_body = f'Sample text from {DATA}.'
    for rule in rules:
        name, _, arg = rule.partition(':')
        if name == 'utm':
            out.append(('utm', text.replace(LINK, 'https://example.com/untagged', 1), 'no utm_campaign'))
        elif name == 'no_pii':
            out.append(('email', text.replace(first_body, first_body + ' lena@example.com', 1), 'email address'))
            out.append(('phone', text.replace(first_body, first_body + ' 415 555 0199', 1), 'phone number'))
        elif name == 'no_card':
            out.append(('card', text.replace(first_body, first_body + ' 4111 1111 1111 1111', 1), 'card or account'))
        elif name == 'loop_data':
            out.append(('loop data', text.replace(DATA, 'loop/notes.md'), 'does not cite a loop data file'))
        elif name == 'queue_ids':
            out.append(('queue id', text.replace(first_body, first_body + ' Q-20261124-09', 1), 'is not an item'))
        elif name in ('paste', 'send', 'render'):
            marker = {'paste': '[PASTE]', 'send': '[SEND]', 'render': '[RENDER]'}[name]
            out.append((name, text.replace(marker, ''), marker))
        elif name == 'hex':
            out.append(('hex', text.replace('#1A2B3C', 'blue', 1), 'Hex must'))
        elif name == 'links':
            out.append((f'links {arg}', text.replace(f'| {DATA} |', '| nowhere |', 1), 'must be a web link'))
        elif name == 'owner_link':
            out.append(('owner link', text.replace(OWNER_LINK, 'https://elsewhere.example/book', 1), 'is not in owner/sales-rules.md'))
        elif name == 'cite_paths':
            out.append(('cite', text.replace(f'- sample item ({DATA})', '- sample item', 1), 'needs its source file'))
    return out


class Agents(Base):
    def setUp(self):
        super().setUp()
        code, out = tool(self.ws, 'loop_data', '--date', '2026-11-23')
        self.assertEqual(code, 0, out)
        self.cc = load_cc(self.ws)
        self.contracts = json.loads((self.ws / 'tools/contracts.json').read_text())

    def test_contracts_cover_every_loop_and_mind_agent(self):
        page = json.loads((HERE.parent / 'architecture/cmo-harness.json').read_text())
        ids = {a['id'] for d in page['directors'] for a in d['agents'] if a['source'] != 'social'}
        self.assertEqual(set(self.contracts['agents']), ids)
        self.assertEqual(len(ids), 85)

    def test_every_agent_sample_passes_and_every_break_is_caught(self):
        checked = 0
        for agent, contract in sorted(self.contracts['agents'].items()):
            for spec in self.cc.specs(contract):
                rel = fill(spec['output'])
                path = self.ws / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                good = sample(agent, spec)
                path.write_text(good)
                with self.subTest(agent=agent, case='valid sample'):
                    self.assertEqual(self.cc.check_file(self.ws, agent, rel, self.contracts), [])
                for name, bad, expect in breaks(agent, spec, good):
                    with self.subTest(agent=agent, case=name):
                        self.assertNotEqual(bad, good, f'break {name} did not change the sample')
                        path.write_text(bad)
                        probs = self.cc.check_file(self.ws, agent, rel, self.contracts)
                        self.assertTrue(any(expect in p for p in probs), f'{name}: expected "{expect}" in {probs}')
                        checked += 1
                path.unlink()
        self.assertGreater(checked, 500)

    def test_wrong_path(self):
        probs = self.cc.check_file(self.ws, 'research-trend-scout', 'research/trends.md', self.contracts)
        self.assertIn('writes research/{date}-trends.md', probs[0])

    def test_agent_files_carry_their_contract(self):
        for agent, contract in self.contracts['agents'].items():
            text = (self.ws / f'.claude/agents/{agent}.md').read_text()
            with self.subTest(agent=agent):
                self.assertIn('## Output format', text)
                for spec in self.cc.specs(contract):
                    self.assertIn(spec['output'], text)
                    for sec in spec.get('sections', []):
                        self.assertIn(f'"## {sec}"', text)
                self.assertIn('tools/check.py output --brief', text)
                self.assertNotIn('—', text)
                uses = any('loop_data' in s.get('rules', []) for s in self.cc.specs(contract))
                self.assertEqual('loop/YYYY-MM-DD-data.md, the newest one' in text, uses)

    def test_mind_agents_write_to_their_mind_folder(self):
        minds = json.loads((HERE / 'catalog/agency-minds.json').read_text())
        loop_ids = {a['id'] for d in json.loads((HERE / 'catalog/growth-loop.json').read_text())['departments'] for a in d['agents']}
        for m in minds:
            for a in m['agents']:
                c = self.contracts['agents'][a['id']]
                if 'output' in json.loads((HERE / 'catalog/contracts.json').read_text())['agents'][a['id']]:
                    continue
                self.assertEqual(c['output'], f"drafts/{m['id']}/{{date}}-{a['id']}-{{slug}}.md")
                self.assertNotIn(a['id'], loop_ids)


class Directors(Base):
    def test_every_director_is_built_and_staffs_only_its_team(self):
        page = json.loads((HERE.parent / 'architecture/cmo-harness.json').read_text())
        for d in page['directors']:
            text = (self.ws / f".claude/agents/{d['id']}.md").read_text()
            team = {a['id'] for a in d['agents']}
            with self.subTest(director=d['id']):
                self.assertEqual(text, text.replace('{{', ''), 'placeholder left')
                self.assertTrue((HERE / f"specs/{d['id']}.md").exists())
                self.assertIn('## How to staff a brief', text)
                self.assertIn('## How every director works', text)
                self.assertIn(f"drafts/briefs/{d['id'].replace('director-', '')}/B-YYYYMMDD-NN-<agent>.md", text)
                staffing = text.partition('## How to staff a brief')[2].partition('## How every director works')[0]
                every = {x['id'] for dd in page['directors'] for x in dd['agents']}
                in_tables = {c.strip() for line in staffing.splitlines() if line.startswith('|')
                             for c in line.strip('|').split('|')} & every
                mentioned = {w for w in re.findall(r'[a-z][a-z0-9-]+', staffing)} & every
                self.assertTrue(in_tables, 'no staffing table')
                self.assertTrue(in_tables <= team, f'staffs agents outside its team: {in_tables - team}')
                self.assertEqual(team - mentioned, set(), f'team agents with no staffing rule: {team - mentioned}')


class OutputCli(Base):
    def setUp(self):
        super().setUp()
        self.golden()
        overlay(HERE / 'fixtures/northwind-research-golden', self.ws)
        tool(self.ws, 'loop_data', '--date', '2026-11-23')

    def test_output_check_by_brief(self):
        cc = load_cc(self.ws)
        contracts = json.loads((self.ws / 'tools/contracts.json').read_text())
        spec = contracts['agents']['research-trend-scout']
        (self.ws / 'research/2026-11-24-trends.md').write_text(sample('research-trend-scout', spec).replace(
            '| sample | loop/2026-11-23-data.md | 1 | 1 | sample |', '| sample | loop/2026-11-23-data.md | 1 | 1 | sample |'))
        code, out = tool(self.ws, 'check', 'output', '--brief', 'B-20261123-01')
        self.assertEqual(code, 0, out)
        (self.ws / 'research/2026-11-24-trends.md').write_text('no front matter')
        code, out = tool(self.ws, 'check', 'output', '--brief', 'B-20261123-01')
        self.assertEqual(code, 1)
        self.assertIn('no front matter', out)
        self.assertTrue(cc)

    def test_agent_brief_output_must_fit_contract(self):
        self.edit('drafts/briefs/research/B-20261123-01-research-trend-scout.md',
                  '- `research/2026-11-24-trends.md`', '- `research/2026-11-24-trends.md`\n- `drafts/trends.md`')
        code, out = tool(self.ws, 'check', 'agent-briefs', '--brief', 'C-20261123-01')
        self.assertIn('Output drafts/trends.md does not fit research-trend-scout', out)


class LoopData(Base):
    def data(self):
        code, out = tool(self.ws, 'loop_data', '--date', '2026-11-23')
        self.assertEqual(code, 0, out)
        return (self.ws / 'loop/2026-11-23-data.md').read_text()

    def test_numbers(self):
        t = self.data()
        self.assertIn('- From: 2026-11-17', t)
        self.assertIn('| roast-date-reel-2 | instagram | roast-date | 5000 | 350 | 60 | 25 | 50 |', t)
        self.assertIn('| latte-art | tiktok | latte-art | 2600 | 12 | 4 | 6 | 0 |', t)
        self.assertNotIn('old-post', t)
        self.assertIn('| roast-date | 2 | 360 | utm |', t)
        self.assertIn('| (none) | 1 | 340 | payment, no crm record, source |', t)
        self.assertIn('- Attributed revenue: 360', t)
        self.assertIn('- Unattributed revenue: 340', t)
        self.assertIn('| roast-date | 2 | 2 | 0 | 0 |', t)
        self.assertIn('| staff-training | 1 | 0 | 1 | 0 |', t)
        self.assertIn('- Calls booked in the window: 3', t)
        self.assertIn('- Exports with no rows in the window: email', t)
        self.assertIn('- Total spend: 40', t)
        self.assertIn('- Cost per booked call: 13.33', t)

    def test_mixed_currency_and_missing_column(self):
        (self.ws / 'exports/ads/2026-11-21-tiktok.csv').write_text(
            'date,channel,campaign,utm_campaign,currency\n2026-11-21,tiktok,boost,latte-art,EUR\n')
        t = self.data()
        self.assertIn('mixed currencies', t)
        self.assertIn('column "spend" is missing', t)

    def test_stop(self):
        (self.ws / 'owner/STOP').write_text('')
        code, _ = tool(self.ws, 'loop_data', '--date', '2026-11-23')
        self.assertEqual(code, 2)


if __name__ == '__main__':
    unittest.main()
