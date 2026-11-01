import json, shutil, sys, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
TEMPLATE = HERE / 'template' if (HERE / 'template').exists() else HERE / 'social-team' / 'template'
sys.path.insert(0, str(HERE / 'runtime'))
import social_team as st


class FakeStore:
    def __init__(self):
        self.docs = {}

    def get(self, path):
        d = self.docs.get(path)
        return (json.loads(json.dumps(d)), 'v') if d is not None else (None, None)

    def put(self, path, value, version=None, create=False):
        self.docs[path] = json.loads(json.dumps(value))


class FakeProc:
    """Stands in for `claude -p`: applies an edit to the workspace, then returns a report."""
    returncode = 0

    def __init__(self, edit, ws, model='claude-sonnet-4-6'):
        self.edit, self.ws, self.model = edit, ws, model

    def communicate(self, prompt):
        self.edit(self.ws, prompt)
        return json.dumps({'result': 'ok', 'total_cost_usd': 0.1, 'modelUsage': {self.model: {}}}), ''

    def kill(self):
        pass


QUEUE = '''# Needs your OK

## Open

### Q-20261101-01: First
- [ ] Approve
- [ ] Reject
- What: post it
- Spend: none
- Owner note:

### Q-20261101-02: URGENT second
- [ ] Approve
- [ ] Reject
- What: reply
- Owner note:

## Done

### Q-20261001-09: Old
- [x] Approve
- [ ] Reject
- What: old
'''


class SocialTeamTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.old = st.WORK, st.TEMPLATE
        st.WORK, st.TEMPLATE = self.tmp / 'ws', TEMPLATE
        self.addCleanup(lambda: (setattr(st, 'WORK', self.old[0]), setattr(st, 'TEMPLATE', self.old[1])))
        self.s = FakeStore()

    def ready(self):
        ws = st.init_product(self.s, 'demo')
        inputs = self.s.docs['growthSocialInputs/demo']
        for rel in st.OWNER_FILES + st.FIRST_FILES:
            inputs['files'][rel] = '# filled\n'
        st.pull_inputs(self.s, 'demo', ws)
        return ws

    def test_template_has_the_whole_system(self):
        t = TEMPLATE
        self.assertEqual(len(list((t / '.claude/agents').glob('*.md'))), 9)
        self.assertEqual(sorted(p.stem for p in (t / '.claude/commands').glob('*.md')), sorted(st.PLAYBOOKS))
        self.assertEqual(len([p for p in (t / 'brand-os').rglob('*.md') if p.name != 'README.md']), 27)
        for f in (t / '.claude/agents').glob('*.md'):
            self.assertIn('model: sonnet', f.read_text(), f.name)
        self.assertIn('Athem additions', (t / 'CLAUDE.md').read_text())
        self.assertEqual([i for i in st.parse_queue((t / 'queue/needs-your-ok.md').read_text())], [])

    def test_parse_queue_splits_open_and_done_and_flags(self):
        items = st.parse_queue(QUEUE)
        self.assertEqual([(i['id'], i['section']) for i in items], [('Q-20261101-01', 'open'), ('Q-20261101-02', 'open'), ('Q-20261001-09', 'done')])
        self.assertTrue(items[1]['urgent'])
        self.assertEqual(items[0]['fields']['Spend'], 'none')
        self.assertEqual(items[2]['ticked'], ['Approve'])

    def test_tick_touches_only_the_named_open_item(self):
        out = st.tick(QUEUE, 'Q-20261101-02', 'Reject', 'not  this\nweek')
        items = {i['id']: i for i in st.parse_queue(out)}
        self.assertEqual(items['Q-20261101-02']['ticked'], ['Reject'])
        self.assertEqual(items['Q-20261101-02']['fields']['Owner note'], 'not this week')
        self.assertEqual(items['Q-20261101-01']['ticked'], [])

    def test_tick_refuses_done_items_and_double_ticks(self):
        with self.assertRaises(ValueError):
            st.tick(QUEUE, 'Q-20261001-09', 'Reject')
        once = st.tick(QUEUE, 'Q-20261101-01', 'Approve')
        with self.assertRaises(ValueError):
            st.tick(once, 'Q-20261101-01', 'Approve')

    def test_unfilled_owner_files_block_a_run_before_any_model_call(self):
        st.init_product(self.s, 'demo')
        with self.assertRaisesRegex(ValueError, 'owner/brand-voice.md'):
            st.process_command(self.s, {'action': 'social_week', 'productId': 'demo'})

    def test_empty_voice_rules_block_a_run(self):
        ws = self.ready()
        self.s.docs['growthSocialInputs/demo']['files']['brand-os/brand-brain/tone-rules.md'] = '[FILL IN: rules]'
        with self.assertRaisesRegex(ValueError, 'tone-rules.md'):
            st.process_command(self.s, {'action': 'social_week', 'productId': 'demo'})
        self.assertTrue(ws.exists())

    def test_kill_switch_blocks_runs_and_follows_the_owner_flag(self):
        ws = self.ready()
        self.s.docs['growthSocialInputs/demo']['stopped'] = True
        with self.assertRaises(st.Stopped):
            st.process_command(self.s, {'action': 'social_week', 'productId': 'demo'})
        self.assertTrue((ws / 'owner/STOP').exists())
        self.assertIn('stopped: owner/STOP present', (ws / 'logs/activity.md').read_text())
        self.s.docs['growthSocialInputs/demo']['stopped'] = False
        st.pull_inputs(self.s, 'demo', ws)
        self.assertFalse((ws / 'owner/STOP').exists())

    def test_agent_edit_to_owner_file_is_restored_and_brand_edit_syncs(self):
        ws = self.ready()

        def edit(w, prompt):
            (w / 'owner/budget-cap.md').write_text('# spend it all\n')
            (w / 'brand-os/content/content-calendar.md').write_text('# new calendar\n')
        st.run_step(self.s, ws, 'demo', 'test', 'go', 1, popen=lambda *a, **k: FakeProc(edit, ws))
        self.assertEqual((ws / 'owner/budget-cap.md').read_text(), '# filled\n')
        self.assertIn('blocked: restored owner file', (ws / 'logs/activity.md').read_text())
        self.assertEqual(self.s.docs['growthSocialInputs/demo']['files']['brand-os/content/content-calendar.md'], '# new calendar\n')

    def test_owner_edit_during_a_run_beats_the_agent(self):
        ws = self.ready()

        def edit(w, prompt):
            (w / 'brand-os/content/hook-bank.md').write_text('# agent\n')
            self.s.docs['growthSocialInputs/demo']['files']['brand-os/content/hook-bank.md'] = '# owner\n'
        st.run_step(self.s, ws, 'demo', 'test', 'go', 1, popen=lambda *a, **k: FakeProc(edit, ws))
        self.assertEqual(self.s.docs['growthSocialInputs/demo']['files']['brand-os/content/hook-bank.md'], '# owner\n')
        self.assertEqual((ws / 'brand-os/content/hook-bank.md').read_text(), '# owner\n')

    def test_other_models_are_refused(self):
        ws = self.ready()
        with self.assertRaisesRegex(ValueError, 'Sonnet'):
            st.run_step(self.s, ws, 'demo', 'test', 'go', 1, popen=lambda *a, **k: FakeProc(lambda w, p: None, ws, 'claude-opus-4-1'))

    def test_input_paths_cannot_escape(self):
        for bad in ('../x.md', '/etc/x.md', 'owner/STOP', 'owner/other.md', 'CLAUDE.md', '.claude/agents/orchestrator.md', 'brand-os/../CLAUDE.md', 'brand-os/x.sh'):
            self.assertFalse(st.safe_input_path(bad), bad)
        self.assertTrue(st.safe_input_path('owner/budget-cap.md'))
        self.assertTrue(st.safe_input_path('brand-os/social/hashtag-rules.md'))

    def test_export_lands_in_the_right_folder_with_a_date_and_safe_name(self):
        ws = self.ready()
        st.process_command(self.s, {'action': 'social_export', 'productId': 'demo', 'folder': 'signals-seo', 'fileName': '../../GSC Queries', 'content': 'a,b\n'})
        names = [p.name for p in (ws / 'brand-os/signals-seo').glob('*gsc*')]
        self.assertEqual(len(names), 1)
        self.assertRegex(names[0], r'^\d{4}-\d\d-\d\d-gsc-queries\.csv$')
        with self.assertRaises(ValueError):
            st.process_command(self.s, {'action': 'social_export', 'productId': 'demo', 'folder': '../owner', 'content': 'x'})

    def test_pending_briefs_ignore_week_plans_and_handled_files(self):
        ws = self.ready()
        b = ws / 'drafts/briefs'
        (b / '2026-11-01-week-plan.md').write_text('# plan\n')
        (b / '2026-11-01-content-engine-a.md').write_text('---\nbrief_id: B-1\ndepartment: content-engine\n---\nGo\n')
        (b / '2026-11-01-rogue-b.md').write_text('---\ndepartment: orchestrator\n---\nGo\n')
        self.assertEqual(st.pending_briefs(ws), ['drafts/briefs/2026-11-01-content-engine-a.md'])
        st.write_handled(ws, {'drafts/briefs/2026-11-01-content-engine-a.md'})
        self.assertEqual(st.pending_briefs(ws), [])

    def test_decision_ticks_the_box_then_runs_the_orchestrator(self):
        ws = self.ready()
        (ws / 'queue/needs-your-ok.md').write_text(QUEUE)
        prompts = []
        real = st.run_step
        st.run_step = lambda s, w, p, label, prompt, budget, agent=None: (prompts.append((agent, prompt)), ('ok', 0.1))[1]
        self.addCleanup(lambda: setattr(st, 'run_step', real))
        st.process_command(self.s, {'action': 'social_decide', 'productId': 'demo', 'queue': 'needs', 'itemId': 'Q-20261101-01', 'decision': 'Approve'})
        self.assertIn('- [x] Approve', (ws / 'queue/needs-your-ok.md').read_text())
        self.assertEqual(prompts[0], ('orchestrator', 'Process my approvals in queue/needs-your-ok.md.'))
        self.assertEqual(self.s.docs['growthSocial/demo']['runs'][0]['status'], 'completed')

    def test_state_stays_under_the_firestore_limit(self):
        ws = self.ready()
        for i in range(60):
            (ws / f'drafts/2026-11-01-blog-big-{i}.md').write_text('x' * 39000)
        state = st.build_state(ws, 'demo')
        self.assertLess(len(json.dumps(state, ensure_ascii=False).encode()), 900000)


if __name__ == '__main__':
    unittest.main()
