"""director-research: agent briefs and the return to the CMO. No model, no network.

    python3 -I _cmo-harness/tests/test_director_research.py

Builds on the Northwind week: the CMO's reference plan, then the Research director's reference split of
C-20261123-01 and its return.
"""
import json
import re
import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_cmo import Base, HERE, overlay, tool  # noqa: E402

C = 'C-20261123-01'
B = 'drafts/briefs/research'


class Research(Base):
    def setUp(self):
        super().setUp()
        self.golden()
        overlay(HERE / 'fixtures/northwind-research-golden', self.ws)

    def briefs(self):
        return tool(self.ws, 'check', 'agent-briefs', '--brief', C)

    def ret(self):
        return tool(self.ws, 'check', 'return', '--brief', C)

    def broken(self, which, rel, old, new, expect):
        self.edit(rel, old, new)
        code, out = which()
        self.assertEqual(code, 1, out)
        self.assertIn(expect, out)


class AgentBriefs(Research):
    def test_golden_passes(self):
        code, out = self.briefs()
        self.assertEqual(code, 0, out)
        self.assertIn(f'agent-briefs {C}: ok', out)

    def test_needs_briefs(self):
        shutil.rmtree(self.ws / B)
        code, out = self.briefs()
        self.assertIn('no agent briefs', out)

    def test_agent_outside_team(self):
        p = self.ws / B / 'B-20261123-03-research-comment-miner.md'
        p.write_text(p.read_text().replace('agent: research-comment-miner', 'agent: content-visual-designer'))
        p.rename(p.with_name('B-20261123-03-content-visual-designer.md'))
        code, out = self.briefs()
        self.assertIn('content-visual-designer is not in the director-research team', out)

    def test_due_by_cmo_due(self):
        self.broken(self.briefs, f'{B}/B-20261123-05-research-email-writer.md', 'due: 2026-11-25', 'due: 2026-11-27',
                    'must be between')

    def test_dependency_order(self):
        self.broken(self.briefs, f'{B}/B-20261123-04-research-post-writer.md', 'order: 2', 'order: 1',
                    'its order must come after')

    def test_after_input_needs_dependency(self):
        self.broken(self.briefs, f'{B}/B-20261123-05-research-email-writer.md',
                    'depends_on: [B-20261123-01, B-20261123-04]', 'depends_on: [B-20261123-01]',
                    'so depends_on must list it')

    def test_missing_input(self):
        self.broken(self.briefs, f'{B}/B-20261123-03-research-comment-miner.md',
                    'exports/comments/2026-11-20-instagram.csv', 'exports/dms/2026-11-20-instagram.csv', 'does not exist')

    def test_every_cmo_output_is_covered(self):
        (self.ws / B / 'B-20261123-05-research-email-writer.md').unlink()
        code, out = self.briefs()
        self.assertIn('asks for drafts/2026-11-25-email-roast-date-issue.md, but no agent brief has it', out)

    def test_ids_unique_across_departments(self):
        other = self.ws / 'drafts/briefs/content'
        other.mkdir(parents=True)
        shutil.copy(self.ws / B / 'B-20261123-01-research-trend-scout.md', other / 'B-20261123-01-content-brand-check.md')
        code, out = self.briefs()
        self.assertIn('brief id B-20261123-01 is used twice', out)

    def test_right_folder(self):
        src = self.ws / B / 'B-20261123-03-research-comment-miner.md'
        dest = self.ws / 'drafts/briefs/content'
        dest.mkdir(parents=True)
        shutil.move(src, dest / src.name)
        code, out = self.briefs()
        self.assertIn('go in drafts/briefs/research/', out)

    def test_dash(self):
        self.broken(self.briefs, f'{B}/B-20261123-01-research-trend-scout.md', 'cafes and offices', 'cafes – offices',
                    'uses a dash character')


class Return(Research):
    R = f'drafts/returns/{C}-return.md'

    def test_golden_passes(self):
        code, out = self.ret()
        self.assertEqual(code, 0, out)

    def test_done_needs_nothing_blocked(self):
        self.broken(self.ret, self.R, 'status: partial', 'status: done', 'Blocked must say Nothing')

    def test_done_when_clear(self):
        self.edit(self.R, 'status: partial', 'status: done')
        p = self.ws / self.R
        text = p.read_text()
        p.write_text(re.sub(r'## Blocked\n.*?\n\n## Needs', '## Blocked\nNothing\n\n## Needs', text, flags=re.S))
        code, out = self.ret()
        self.assertEqual(code, 0, out)

    def test_done_files_exist(self):
        (self.ws / 'research/2026-11-24-comment-mine.md').unlink()
        code, out = self.ret()
        self.assertIn('Done lists research/2026-11-24-comment-mine.md, which does not exist', out)

    def test_lists_every_agent_brief(self):
        self.broken(self.ret, self.R, ', B-20261123-05]', ']', 'agent_briefs is missing B-20261123-05')

    def test_queue_ids_real(self):
        self.broken(self.ret, self.R, '## Waiting for the owner\nNothing', '## Waiting for the owner\n- Q-20261123-07: reel',
                    'Q-20261123-07 is not in queue/needs-your-ok.md')

    def test_missing_return(self):
        (self.ws / self.R).unlink()
        code, out = self.ret()
        self.assertIn('the return file does not exist', out)


class Spec(Research):
    def test_installed_and_filled(self):
        text = (self.ws / '.claude/agents/director-research.md').read_text()
        self.assertNotIn('{{', text)
        self.assertIn('## How every director works', text)
        self.assertIn('drafts/briefs/research/B-YYYYMMDD-NN-<agent>.md', text)
        self.assertIn('director: director-research', text)
        self.assertNotIn('—', text)
        page = json.loads((HERE.parent / 'architecture/cmo-harness.json').read_text())
        expected = {a['id'] for d in page['directors'] if d['id'] == 'director-research' for a in d['agents']}
        team = set(re.findall(r'^\| `([a-z0-9-]+)` \|', text.partition('## Your team')[2].partition('\n## ')[0], re.M))
        self.assertEqual(team, expected)
        staffed = set(re.findall(r'^\| (research-[a-z-]+) \|', text, re.M))
        self.assertTrue(staffed <= team, staffed - team)
        self.assertEqual(staffed, team)

    def test_cmo_reads_return_files(self):
        self.assertIn('drafts/returns/<CMO brief id>-return.md', (self.ws / '.claude/agents/cmo.md').read_text())


if __name__ == '__main__':
    unittest.main()
