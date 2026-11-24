"""The CMO: context facts, the plan check and approvals. No model, no network.

    python3 -I _cmo-harness/tests/test_cmo.py

Uses the fictional Northwind Coffee workspace in fixtures/, on Monday 2026-11-23 (week 2026-W48).
"""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
DATE = '2026-11-23'
WEEK = '2026-W48'


def overlay(src, dest):
    for f in src.rglob('*'):
        if f.is_file():
            t = dest / f.relative_to(src)
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(f, t)


def tool(ws, *args):
    r = subprocess.run([sys.executable, '-I', f'tools/{args[0]}.py', *args[1:]], cwd=ws, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, '-I', str(HERE / 'build.py')], check=True, capture_output=True)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = Path(self.tmp.name) / 'ws'
        shutil.copytree(HERE / 'template', self.ws)
        overlay(HERE / 'fixtures/northwind', self.ws)

    def tearDown(self):
        self.tmp.cleanup()

    def golden(self):
        overlay(HERE / 'fixtures/northwind-cmo-golden', self.ws)

    def edit(self, rel, old, new):
        p = self.ws / rel
        text = p.read_text()
        self.assertIn(old, text, f'fixture changed: {old!r} not in {rel}')
        p.write_text(text.replace(old, new, 1))

    def check(self):
        return tool(self.ws, 'check', 'plan', '--week', WEEK)


class Context(Base):
    def test_facts(self):
        code, out = tool(self.ws, 'cmo_context', '--date', DATE)
        self.assertEqual(code, 0, out)
        text = (self.ws / f'reports/plans/{WEEK}-context.md').read_text()
        self.assertIn('- Week: 2026-W48', text)
        self.assertIn('- Starts: 2026-11-23 (Monday)', text)
        self.assertIn('- Ends: 2026-11-29 (Sunday)', text)
        self.assertIn('- Result: yes', text)
        self.assertIn('| analytics | 2026-11-21-metricool.csv | 2 | fresh |', text)
        self.assertIn('| email | 2026-11-01-newsletter.csv | 22 | stale |', text)
        self.assertIn('| seo | - | - | missing |', text)
        self.assertIn('| ads | 2026-11-20-meta.csv | 3 | fresh |', text)
        self.assertIn('| queue/needs-your-ok.md | 1 | 2 | 1 | 0 | 1 |', text)
        self.assertIn('- Roast date reels: 2 booked calls', text)
        self.assertIn('- Generic latte art videos', text)
        self.assertIn('- Weekly report: reports/weekly/2026-11-22.md', text)
        self.assertEqual(len(re.findall(r'^- director-', text, re.M)), 12)

    def test_unfilled_owner_file_blocks(self):
        (self.ws / 'owner/targets.md').write_text('# Targets\n[FILL IN: the goal]\n')
        code, _ = tool(self.ws, 'cmo_context', '--date', DATE)
        self.assertEqual(code, 2)
        text = (self.ws / f'reports/plans/{WEEK}-context.md').read_text()
        self.assertIn('Unfilled owner files: owner/targets.md', text)
        self.assertIn('NO. Stop and tell the owner.', text)

    def test_stop_blocks(self):
        (self.ws / 'owner/STOP').write_text('')
        code, _ = tool(self.ws, 'cmo_context', '--date', DATE)
        self.assertEqual(code, 2)

    def test_template_alone_is_blocked(self):
        ws = Path(self.tmp.name) / 'blank'
        shutil.copytree(HERE / 'template', ws)
        code, _ = tool(ws, 'cmo_context', '--date', DATE)
        self.assertEqual(code, 2)


class Plan(Base):
    def test_golden_passes(self):
        self.golden()
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn('plan 2026-W48: ok', out)

    def test_missing_plan(self):
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn('the plan file does not exist', out)

    def broken(self, rel, old, new, expect):
        self.golden()
        self.edit(rel, old, new)
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn(expect, out)

    PLAN = f'reports/plans/{WEEK}.md'

    def test_score_must_be_the_sum(self):
        self.broken(self.PLAN, '| 2 | 3 | 3 | 3 | 11 | plan |', '| 2 | 3 | 3 | 3 | 12 | plan |', 'is not the sum')

    def test_no_evidence_is_dropped(self):
        self.broken(self.PLAN, '| 0 | 1 | 0 | 0 | 1 | drop |', '| 0 | 1 | 0 | 0 | 1 | plan |', 'Evidence 0 means')

    def test_score_range(self):
        self.broken(self.PLAN, '| 1 | 2 | 1 | 0 | 4 | plan |', '| 1 | 2 | 1 | 4 | 8 | plan |', 'must be 0 to 3')

    def test_priorities_high_to_low(self):
        self.golden()
        self.edit(self.PLAN, '1. P1: Roast date reels | score 11', '1. P1: Office manager cost per cup test | score 4')
        self.edit(self.PLAN, '3. P3: Office manager cost per cup test | score 4', '3. P3: Roast date reels | score 11')
        code, out = self.check()
        self.assertIn('highest score to the lowest', out)

    def test_priority_must_be_planned(self):
        self.broken(self.PLAN, '3. P3: Office manager cost per cup test | score 4',
                    '3. P3: Newsletter export refresh | score 7', 'is marked later')

    def test_missing_section(self):
        self.broken(self.PLAN, '## Blocked\n', '## Problems\n', 'missing section "## Blocked"')

    def test_spend_needs_queue_item(self):
        self.broken(self.PLAN, 'None this week.',
                    '| Item | Amount | Channel | Queue |\n|---|---|---|---|\n| Boost reel | 40 USD | Instagram | pending |',
                    'has no queue item id')

    def test_dash_characters(self):
        self.broken(self.PLAN, 'second week, so', 'second week — so', 'uses a dash character')

    def test_unlisted_brief(self):
        self.golden()
        src = self.ws / 'drafts/briefs/cmo/C-20261123-02-director-research.md'
        shutil.copy(src, src.with_name('C-20261123-04-director-research.md'))
        code, out = self.check()
        self.assertIn('C-20261123-04-director-research.md is not listed in Briefs', out)

    def test_brief_due_inside_week(self):
        self.broken('drafts/briefs/cmo/C-20261123-02-director-research.md', 'due: 2026-11-26', 'due: 2026-12-02',
                    'is outside 2026-W48')

    def test_brief_name_matches_director(self):
        self.broken('drafts/briefs/cmo/C-20261123-02-director-research.md', 'director: director-research',
                    'director: director-content', 'does not match the file name')

    def test_brief_inputs_exist(self):
        self.broken('drafts/briefs/cmo/C-20261123-02-director-research.md', '- `owner/sales-rules.md`',
                    '- `exports/crm/2026-11-30-hubspot.csv`', 'does not exist')

    def test_brief_dependency_known(self):
        self.broken('drafts/briefs/cmo/C-20261123-03-director-content.md', 'depends_on: [C-20261123-01]',
                    'depends_on: [C-20261123-09]', 'is not a brief this week')

    def test_director_without_brief(self):
        self.broken(self.PLAN, 'directors: [director-research, director-content]',
                    'directors: [director-research, director-content, director-loop]', 'director-loop is in directors but has no brief')


class Approvals(Base):
    def test_process_moves_decided_items(self):
        log_before = (self.ws / 'logs/activity.md').read_text()
        code, out = tool(self.ws, 'queue', 'process')
        self.assertEqual(code, 0, out)
        self.assertIn('APPROVED Q-20261121-01', out)
        self.assertIn('REJECTED Q-20261121-02', out)
        self.assertIn('owner note: drop latte art', out)
        text = (self.ws / 'queue/needs-your-ok.md').read_text()
        open_part, done_part = text.split('## Done')
        self.assertIn('Q-20261122-01', open_part)
        self.assertNotIn('Q-20261121-01', open_part)
        self.assertIn('Q-20261121-01', done_part)
        self.assertIn('Q-20261121-02', done_part)
        self.assertIn('- [ ] Approve\n- [ ] Reject', open_part)
        log = (self.ws / 'logs/activity.md').read_text()
        self.assertTrue(log.startswith(log_before))
        self.assertIn('| cmo | owner approved Q-20261121-01 | queue/needs-your-ok.md', log)
        code, out = tool(self.ws, 'queue', 'process')
        self.assertIn('nothing ticked', out)

    def test_both_boxes_left_open(self):
        self.edit('queue/needs-your-ok.md', '- [x] Approve\n- [ ] Reject', '- [x] Approve\n- [x] Reject')
        code, out = tool(self.ws, 'queue', 'process')
        self.assertIn('BOTH BOXES Q-20261121-01', out)
        open_part = (self.ws / 'queue/needs-your-ok.md').read_text().split('## Done')[0]
        self.assertIn('Q-20261121-01', open_part)

    def test_stop(self):
        (self.ws / 'owner/STOP').write_text('')
        code, out = tool(self.ws, 'queue', 'process')
        self.assertEqual(code, 2)
        self.assertIn('Q-20261121-01', (self.ws / 'queue/needs-your-ok.md').read_text().split('## Done')[0])


class Agent(Base):
    def test_spec_installed(self):
        text = (self.ws / '.claude/agents/cmo.md').read_text()
        self.assertEqual(text, (HERE / 'specs/cmo.md').read_text().replace(
            '{{DIRECTORS_TABLE}}', text.split('## Your directors\n')[1].split('\n\n## Mode 1')[0]))
        self.assertNotIn('{{', text)
        for d in re.findall(r'director-[a-z]+', text.split('## Mode 1')[0]):
            self.assertTrue((self.ws / f'.claude/agents/{d}.md').exists(), d)
        self.assertNotIn('—', text)

    def test_tools_installed_and_locked(self):
        import json
        s = json.loads((self.ws / '.claude/settings.json').read_text())
        for t in ('cmo_context', 'check', 'queue'):
            self.assertTrue((self.ws / f'tools/{t}.py').exists())
            self.assertIn(f'Bash(python3 -I tools/{t}.py:*)', s['permissions']['allow'])
        self.assertTrue(all(a.startswith('Bash(python3 -I tools/') for a in s['permissions']['allow']))
        for rule in ('Edit(./owner/**)', 'Write(./tools/**)', 'Write(./.claude/**)', 'Edit(./CLAUDE.md)'):
            self.assertIn(rule, s['permissions']['deny'])
        self.assertFalse(list(self.ws.rglob('__pycache__')))


if __name__ == '__main__':
    unittest.main()
