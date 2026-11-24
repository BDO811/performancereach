"""Checks the built template. No model, no network.

    python3 -I _cmo-harness/tests/test_cmo_harness.py
"""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
T = HERE / 'template'
AGENTS = T / '.claude/agents'


def front(path):
    text = path.read_text()
    m = re.match(r'---\n(.*?)\n---\n', text, re.S)
    assert m, f'{path.name} has no front matter'
    return dict(line.split(': ', 1) for line in m.group(1).splitlines() if ': ' in line), text[m.end():]


class Harness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, '-I', str(HERE / 'build.py')], check=True, capture_output=True)

    def test_counts(self):
        loop = json.loads((HERE / 'catalog/growth-loop.json').read_text())
        minds = json.loads((HERE / 'catalog/agency-minds.json').read_text())
        n_loop = sum(len(d['agents']) for d in loop['departments'])
        n_minds = sum(len(m['agents']) for m in minds)
        self.assertEqual(n_loop, 36)
        self.assertEqual(len(minds), 13)
        self.assertEqual(n_minds, 49)
        # cmo + 12 directors + 36 + 49 + 8 social departments
        self.assertEqual(len(list(AGENTS.glob('*.md'))), 1 + 12 + n_loop + n_minds + 8)

    def test_every_catalog_agent_exists(self):
        loop = json.loads((HERE / 'catalog/growth-loop.json').read_text())
        minds = json.loads((HERE / 'catalog/agency-minds.json').read_text())
        ids = [a['id'] for d in loop['departments'] for a in d['agents']]
        ids += [a['id'] for m in minds for a in m['agents']]
        self.assertEqual(len(ids), len(set(ids)), 'duplicate agent ids')
        for i in ids:
            self.assertTrue((AGENTS / f'{i}.md').exists(), i)

    def test_front_matter_model_and_tools(self):
        for f in AGENTS.glob('*.md'):
            meta, _ = front(f)
            self.assertEqual(meta.get('name'), f.stem, f.name)
            self.assertEqual(meta.get('model'), 'sonnet', f.name)
            self.assertNotIn('Bash', meta.get('tools', ''), f.name)
            self.assertTrue(meta.get('description'), f.name)

    def test_every_agent_has_a_director_and_stop_check(self):
        directors = {f.stem for f in AGENTS.glob('director-*.md')}
        self.assertEqual(len(directors), 12)
        for f in AGENTS.glob('*.md'):
            if f.stem == 'cmo' or f.stem in directors:
                continue
            _, body = front(f)
            self.assertTrue(any(d in body for d in directors), f'{f.name} names no director')
            self.assertIn('STOP', body, f.name)

    def test_cmo_names_every_director(self):
        _, body = front(AGENTS / 'cmo.md')
        for f in AGENTS.glob('director-*.md'):
            self.assertIn(f.stem, body)

    def test_social_team_rewired(self):
        for f in list(AGENTS.glob('*.md')) + list((T / '.claude/commands').glob('*.md')):
            self.assertNotRegex(f.read_text(), r'\borchestrator agent\b', f.name)

    def test_owner_files_and_lock(self):
        for name in ('targets', 'positioning', 'brand-voice', 'approval-bar', 'budget-cap', 'sales-rules'):
            self.assertIn('[FILL IN:', (T / f'owner/{name}.md').read_text(), name)
        self.assertFalse((T / 'owner/STOP').exists())
        perms = json.loads((T / '.claude/settings.json').read_text())['permissions']
        for rule in ('Edit(./owner/**)', 'Write(./owner/**)'):
            self.assertIn(rule, perms['deny'])
        self.assertTrue(all(a.startswith('Bash(python3 -I tools/') for a in perms.get('allow', [])))

    def test_queues_start_empty(self):
        for name in ('needs-your-ok', 'held-for-voice-review'):
            s = (T / f'queue/{name}.md').read_text()
            self.assertRegex(s, r'## Open\n\s*\n## Done')

    def test_page_data_matches_harness(self):
        data = json.loads((HERE.parent / 'architecture/cmo-harness.json').read_text())
        page_ids = {a['id'] for d in data['directors'] for a in d['agents']}
        built = {f.stem for f in AGENTS.glob('*.md')} - {'cmo'} - {d['id'] for d in data['directors']}
        self.assertEqual(page_ids, built)
        self.assertEqual(data['counts']['agents'], len(built))
        self.assertEqual(data['counts']['directors'], 12)

    def test_no_dashes_in_generated_prose(self):
        for f in list(AGENTS.glob('*.md')) + [T / 'CLAUDE.md']:
            text = f.read_text()
            self.assertNotIn('—', text, f.name)
            self.assertNotIn('–', text, f.name)


if __name__ == '__main__':
    unittest.main()
