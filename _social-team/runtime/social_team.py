"""AI social media team for Growth Studio.

Runs the guide's file-based project once per product. The Mac workspace holds the files the agents
read and write. Firestore mirrors them for the dashboard:
  growthSocialInputs/<product>  owner side: owner files, Brand OS, kill switch, tool status
  growthSocial/<product>        worker side: queues, drafts, briefs, log, run status

Only this code ticks a queue box, and only because the owner clicked in the dashboard. Agents get file
tools and web search, with no shell, no MCP and no way to publish, send or spend.
"""
import datetime as dt, json, os, re, shutil, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'social-team' / 'template'
WORK = ROOT / 'social-team' / 'workspaces'
MODEL = 'claude-sonnet-4-6'
DEPARTMENTS = ('search-visibility', 'market-radar', 'content-engine', 'creative-studio', 'publishing-social',
               'reviews-reputation', 'leads-conversations', 'results-roi')
PLAYBOOKS = ('search-demand-spikes', 'competitor-drops-a-promo', 'one-star-review-lands', 'content-calendar-looks-thin',
             'a-post-goes-viral', 'ranking-drops-a-page', 'ad-creative-fatigues', 'dm-lead-at-11pm')
OWNER_FILES = ('owner/brand-voice.md', 'owner/budget-cap.md', 'owner/approval-bar.md', 'owner/positioning.md')
FIRST_FILES = ('brand-os/brand-brain/voice-guide.md', 'brand-os/brand-brain/tone-rules.md', 'brand-os/content/content-calendar.md')
EXPORT_FOLDERS = ('signals-seo', 'reputation', 'conversation', 'reporting')
TOOLS = 'Read,Write,Edit,Glob,Grep,WebSearch,WebFetch,Agent'
STEP_BUDGET, RUN_BUDGET, STEP_TIMEOUT, MAX_BRIEFS = 2.0, 8.0, 900, 8
MAX_STATE_BYTES = 850000


class Stopped(RuntimeError):
    pass


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')


def stamp():
    return dt.datetime.now().strftime('%Y-%m-%d %H:%M')


def workspace(product):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', product or ''):
        raise ValueError('Invalid product ID')
    path = WORK / product
    if not path.exists():
        shutil.copytree(TEMPLATE, path)
    return path


def log_line(ws, action, file='-', agent='worker'):
    with (ws / 'logs/activity.md').open('a') as f:
        f.write(f'{stamp()} | {agent} | {action} | {file}\n')


def safe_input_path(rel):
    """Owner edits may only land on Markdown files under owner/ or brand-os/."""
    if not isinstance(rel, str) or '..' in rel.split('/') or rel.startswith('/') or not rel.endswith('.md'):
        return False
    return rel in OWNER_FILES or rel.startswith('brand-os/')


def input_files(ws):
    out = {rel: (ws / rel).read_text() for rel in OWNER_FILES}
    for f in sorted((ws / 'brand-os').rglob('*.md')):
        out[f.relative_to(ws).as_posix()] = f.read_text()
    return out


def fill_prompts(text):
    return re.findall(r'\[FILL IN: *([^\]]*)\]', text or '')


def unfilled_owner_files(ws):
    return [rel for rel in OWNER_FILES if fill_prompts((ws / rel).read_text())]


# Queue files: the format is the guide's, so a run in a plain terminal reads the same file.
ITEM = re.compile(r'^### ((?:Q|H)-\d{8}-\d+): *(.*)$', re.M)


def parse_queue(text):
    open_part, _, done_part = text.partition('\n## Done')
    open_part = open_part.partition('\n## Open')[2]

    def items(part, section):
        marks = list(ITEM.finditer(part))
        out = []
        for i, m in enumerate(marks):
            body = part[m.end():marks[i + 1].start() if i + 1 < len(marks) else len(part)]
            fields = {k.strip(): v.strip() for k, v in re.findall(r'^- (?!\[)([^:\n]+):[ \t]*(.*)$', body, re.M)}
            ticks = re.findall(r'^- \[[xX]\] *([^\n]*)$', body, re.M)
            out.append({'id': m.group(1), 'title': m.group(2).strip(), 'section': section, 'fields': fields, 'ticked': ticks,
                        'urgent': 'URGENT' in m.group(2), 'overCap': 'OVER CAP' in m.group(2)})
        return out

    return items(open_part, 'open') + items(done_part, 'done')


def tick(text, item_id, decision, note=''):
    """Tick one box on one open item. Only ever called for an owner click."""
    head, sep, done = text.partition('\n## Done')
    m = re.search(r'^### ' + re.escape(item_id) + r':.*$', head, re.M)
    if not m:
        raise ValueError(f'{item_id} is not open in this queue')
    nxt = ITEM.search(head, m.end())
    end = nxt.start() if nxt else len(head)
    body = head[m.end():end]
    new, count = re.subn(r'^- \[ \] ' + re.escape(decision) + r'[ \t]*$', f'- [x] {decision}', body, count=1, flags=re.M)
    if not count:
        raise ValueError(f'{item_id} has no open "{decision}" box')
    if note:
        clean = ' '.join(str(note).split())[:1000]
        new, n = re.subn(r'^- Owner note:.*$', lambda _: f'- Owner note: {clean}', new, count=1, flags=re.M)
        if not n:
            new = new.rstrip('\n') + f'\n- Owner note: {clean}\n'
    return head[:m.end()] + new + head[end:] + sep + done


def front_matter(text):
    m = re.match(r'^---\n(.*?)\n---\n?', text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ':' in line and not line.startswith(' '):
            k, v = line.split(':', 1)
            meta[k.strip()] = v.strip()
    return meta, text[m.end():]


def collect_files(folder, ws, limit):
    files = sorted((p for p in folder.glob('*.md')), key=lambda p: (p.stat().st_mtime, p.name), reverse=True)[:limit]
    out = []
    for f in files:
        text = f.read_text()
        meta, _ = front_matter(text)
        out.append({'path': f.relative_to(ws).as_posix(), 'name': f.name, 'meta': meta, 'content': text[:40000],
                    'modifiedAt': dt.datetime.fromtimestamp(f.stat().st_mtime, dt.timezone.utc).isoformat(timespec='seconds')})
    return out


def read_handled(ws):
    p = ws / '.handled-briefs.json'
    return set(json.loads(p.read_text())) if p.exists() else set()


def write_handled(ws, handled):
    (ws / '.handled-briefs.json').write_text(json.dumps(sorted(handled)))


def pending_briefs(ws):
    handled, out = read_handled(ws), []
    for f in sorted((ws / 'drafts/briefs').glob('*.md'), key=lambda p: (p.stat().st_mtime, p.name)):
        rel = f.relative_to(ws).as_posix()
        if rel not in handled and front_matter(f.read_text())[0].get('department') in DEPARTMENTS:
            out.append(rel)
    return out


def build_state(ws, product, run=None, history=None):
    log = [l.rstrip('\n') for l in (ws / 'logs/activity.md').read_text().splitlines() if re.match(r'^\d{4}-\d\d-\d\d \d\d:\d\d \|', l)]
    state = {'productId': product, 'updatedAt': now(), 'stopped': (ws / 'owner/STOP').exists(), 'unfilled': unfilled_owner_files(ws),
             'queue': parse_queue((ws / 'queue/needs-your-ok.md').read_text()), 'held': parse_queue((ws / 'queue/held-for-voice-review.md').read_text()),
             'drafts': collect_files(ws / 'drafts', ws, 60), 'briefs': collect_files(ws / 'drafts/briefs', ws, 40),
             'pendingBriefs': pending_briefs(ws), 'log': log[-300:], 'run': run, 'runs': (history or [])[:25]}
    # Keep the newest text. Older files stay on the Mac and show as "open locally" in the dashboard.
    for key in ('briefs', 'drafts'):
        for entry in reversed(state[key]):
            if len(json.dumps(state, ensure_ascii=False).encode()) < MAX_STATE_BYTES:
                break
            entry['content'], entry['truncated'] = entry['content'][:400], True
    return state


def push_state(s, ws, product, run=None):
    prior = (s.get('growthSocial/' + product)[0] or {}).get('runs', [])
    s.put('growthSocial/' + product, build_state(ws, product, run, prior))


def save_run(s, ws, product, record):
    prior = (s.get('growthSocial/' + product)[0] or {}).get('runs', [])
    s.put('growthSocial/' + product, build_state(ws, product, None, [record] + prior))


def init_product(s, product):
    ws = workspace(product)
    if not s.get('growthSocialInputs/' + product)[0]:
        s.put('growthSocialInputs/' + product, {'productId': product, 'stopped': False, 'files': input_files(ws), 'tools': {}, 'updatedAt': now()}, create=True)
    pull_inputs(s, product, ws)
    if not s.get('growthSocial/' + product)[0]:
        push_state(s, ws, product)
    return ws


def pull_inputs(s, product, ws=None):
    """Dashboard to Mac. The owner's copy wins, and the kill switch follows the owner's flag."""
    ws = ws or workspace(product)
    inputs, _ = s.get('growthSocialInputs/' + product)
    if not inputs:
        raise ValueError('Run the social team installer for this product first.')
    for rel, text in (inputs.get('files') or {}).items():
        if safe_input_path(rel) and isinstance(text, str):
            target = ws / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() or target.read_text() != text:
                target.write_text(text)
    stop = ws / 'owner/STOP'
    if inputs.get('stopped'):
        stop.touch()
    elif stop.exists():
        stop.unlink()
    return inputs


def snapshot(ws):
    return input_files(ws)


def guard_owner_files(ws, before):
    """Agents never keep a change to owner/, however it was made."""
    for rel in OWNER_FILES:
        if (ws / rel).read_text() != before[rel]:
            (ws / rel).write_text(before[rel])
            log_line(ws, 'blocked: restored owner file changed during a run', rel)


def push_brand_changes(s, product, ws, before):
    """Mac to dashboard for Brand OS files the agents changed, such as the calendar."""
    after = input_files(ws)
    changed = {r: t for r, t in after.items() if r.startswith('brand-os/') and t != before.get(r)}
    if not changed:
        return
    for attempt in range(3):
        inputs, version = s.get('growthSocialInputs/' + product)
        for rel, text in changed.items():
            if (inputs['files'].get(rel) or '') != (before.get(rel) or ''):
                log_line(ws, 'kept owner edit over agent edit', rel)
                (ws / rel).write_text(inputs['files'][rel])
                continue
            inputs['files'][rel] = text
        inputs['updatedAt'] = now()
        try:
            s.put('growthSocialInputs/' + product, inputs, version)
            return
        except RuntimeError:
            if attempt == 2:
                raise
            time.sleep(1)


def claude_args(budget, agent=None):
    cli = shutil.which('claude') or '/Users/amitmehta/.local/bin/claude'
    args = [cli, '-p', '--model', MODEL, '--effort', 'low', '--tools', TOOLS, '--allowedTools', TOOLS,
            '--disallowedTools', 'Bash,Edit(owner/**),Write(owner/**),Edit(.claude/**),Write(.claude/**),Edit(CLAUDE.md),Write(CLAUDE.md)', '--permission-mode', 'acceptEdits',
            '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--setting-sources', 'project', '--settings', '{"disableAllHooks":true}',
            '--no-session-persistence', '--output-format', 'json', '--max-budget-usd', str(round(budget, 2))]
    if agent:
        args += ['--agent', agent]
    return args


def stop_requested(s, product):
    try:
        return bool((s.get('growthSocialInputs/' + product)[0] or {}).get('stopped'))
    except Exception:
        return False


def run_step(s, ws, product, label, prompt, budget, agent=None, popen=subprocess.Popen):
    """One Claude Code run in the workspace. The kill switch ends it within seconds."""
    if stop_requested(s, product):
        (ws / 'owner/STOP').touch()
    if (ws / 'owner/STOP').exists():
        log_line(ws, 'stopped: owner/STOP present')
        raise Stopped('System paused by the owner.')
    before = snapshot(ws)
    env = os.environ.copy()
    env.pop('CLAUDECODE', None)
    proc = popen(claude_args(budget, agent), cwd=ws, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    from threading import Thread
    result = {}
    t = Thread(target=lambda: result.update(zip(('out', 'err'), proc.communicate(f'Current local time: {stamp()}. Use it in log lines.\n\n{prompt}'))), daemon=True)
    t.start()
    started, killed = time.time(), None
    while t.is_alive():
        t.join(5)
        if t.is_alive() and stop_requested(s, product):
            killed = 'stop'
        elif t.is_alive() and time.time() - started > STEP_TIMEOUT:
            killed = 'timeout'
        if killed:
            proc.kill()
            t.join(10)
            break
    guard_owner_files(ws, before)
    push_brand_changes(s, product, ws, before)
    if killed == 'stop':
        (ws / 'owner/STOP').touch()
        log_line(ws, 'stopped: owner/STOP present')
        raise Stopped(f'Kill switch ended {label}. Whatever it wrote is still in the workspace.')
    if killed == 'timeout':
        log_line(ws, f'failed: {label} timed out')
        raise RuntimeError(f'{label} did not finish within {STEP_TIMEOUT // 60} minutes.')
    if proc.returncode:
        raise RuntimeError(f'{label} failed. Check local Claude authentication and quota. ' + (result.get('err') or '')[-300:])
    try:
        data = json.loads(result.get('out') or '')
    except ValueError:
        raise RuntimeError(f'{label} returned invalid output.') from None
    if data.get('is_error'):
        raise RuntimeError(str(data.get('result', 'Model request failed'))[:500])
    for model in data.get('modelUsage', {}):
        if not model.startswith(MODEL):
            raise ValueError(f'{label} reported a model outside the permitted Sonnet configuration: {model}')
    return str(data.get('result', '')), float(data.get('total_cost_usd', 0))


class Run:
    def __init__(self, s, ws, product, label):
        self.s, self.ws, self.product = s, ws, product
        self.record = {'id': now(), 'label': label, 'startedAt': now(), 'status': 'running', 'steps': [], 'costUsd': 0.0}

    def step(self, label, prompt, agent=None):
        left = RUN_BUDGET - self.record['costUsd']
        if left <= 0.05:
            raise RuntimeError(f'This run reached its ${RUN_BUDGET:.0f} limit. Remaining work stays pending.')
        entry = {'label': label, 'status': 'running', 'startedAt': now()}
        self.record['steps'].append(entry)
        push_state(self.s, self.ws, self.product, self.record)
        try:
            text, cost = run_step(self.s, self.ws, self.product, label, prompt, min(STEP_BUDGET, left), agent)
        except Exception as e:
            entry.update(status='stopped' if isinstance(e, Stopped) else 'failed', error=str(e)[:400])
            raise
        self.record['costUsd'] = round(self.record['costUsd'] + cost, 4)
        entry.update(status='done', costUsd=round(cost, 4), result=text[:4000])
        push_state(self.s, self.ws, self.product, self.record)
        return text

    def handoffs(self):
        """The main session's job in the guide: give each brief to the department it names."""
        done = 0
        for rel in pending_briefs(self.ws):
            if done >= MAX_BRIEFS:
                break
            dept = front_matter((self.ws / rel).read_text())[0]['department']
            self.step(f'{dept} on {Path(rel).name}', f'Do the job in {rel}. Follow CLAUDE.md. Return the file path, check results and any [VERIFY] marks.', dept)
            handled = read_handled(self.ws) | {rel}
            write_handled(self.ws, handled)
            done += 1
        return done

    def settle(self, rounds=2):
        for _ in range(rounds):
            if not self.handoffs():
                return
            self.step('orchestrator processes returns', 'Process the work the departments just returned. Apply the owner gate. List any new briefs and what waits for the owner.', 'orchestrator')
        self.handoffs()


def playbook_prompt(ws, name, event):
    if name not in PLAYBOOKS:
        raise ValueError('Unknown playbook')
    _, body = front_matter((ws / '.claude/commands' / (name + '.md')).read_text())
    return body.replace('$ARGUMENTS', ' '.join(str(event or '').split())[:6000])


def execute(s, ws, product, label, work):
    inputs = pull_inputs(s, product, ws)
    if inputs.get('stopped'):
        log_line(ws, 'stopped: owner/STOP present')
        push_state(s, ws, product)
        raise Stopped('System paused by the owner. Release the kill switch to run this.')
    missing = unfilled_owner_files(ws)
    if missing:
        push_state(s, ws, product)
        raise ValueError('Fill these owner files first: ' + ', '.join(missing))
    # A voice check against an empty rule file passes everything, so these block too.
    missing = [rel for rel in FIRST_FILES if fill_prompts((ws / rel).read_text())]
    if missing:
        push_state(s, ws, product)
        raise ValueError('Fill these Brand OS files first: ' + ', '.join(missing))
    run = Run(s, ws, product, label)
    try:
        work(run)
        run.record['status'] = 'completed'
    except Stopped as e:
        run.record.update(status='stopped', error=str(e))
        raise
    except Exception as e:
        run.record.update(status='failed', error=str(e)[:500])
        raise
    finally:
        run.record['completedAt'] = now()
        save_run(s, ws, product, run.record)


def week(run):
    run.step('orchestrator runs the week', "Run this week's loop.", 'orchestrator')
    run.settle()


def process_command(s, c):
    action, product = c['action'], c['productId']
    ws = workspace(product)
    if action == 'social_init':
        init_product(s, product)
    elif action == 'social_week':
        execute(s, ws, product, "This week's loop", week)
    elif action == 'social_playbook':
        name = c.get('playbook')
        prompt = playbook_prompt(ws, name, c.get('event'))

        def work(run):
            run.step(f'/{name}', prompt)
            run.settle()
        execute(s, ws, product, f'Playbook: {name}', work)
    elif action == 'social_decide':
        decide(s, ws, product, c)
    elif action == 'social_report':
        execute(s, ws, product, 'Weekly results note', lambda run: run.step('results-roi writes the note', 'Write the weekly report for this week.', 'results-roi'))
    elif action == 'social_handoffs':
        execute(s, ws, product, 'Pending briefs', lambda run: run.settle())
    elif action == 'social_learn':
        prompt = ("Read this week's report in drafts/, the drafts the owner approved and rejected, and queue/held-for-voice-review.md. Suggest additions and "
                  'removals for brand-os/content/hook-bank.md, brand-os/brand-brain/messaging-bank.md and brand-os/brand-brain/tone-rules.md, with the reason for each. '
                  f'Save the list as drafts/{dt.date.today().isoformat()}-report-brand-suggestions.md. Do not edit any file in brand-os/.')
        execute(s, ws, product, 'What to teach the brand files', lambda run: run.step('brand file suggestions', prompt))
    elif action == 'social_export':
        save_export(s, ws, product, c)
    else:
        raise ValueError('Unsupported social team command')


def decide(s, ws, product, c):
    item, decision, kind = c.get('itemId'), c.get('decision'), c.get('queue')
    allowed = {'needs': ('queue/needs-your-ok.md', ('Approve', 'Reject')), 'held': ('queue/held-for-voice-review.md', ('Fixed: send it on', 'Drop it'))}
    if kind not in allowed or decision not in allowed[kind][1]:
        raise ValueError('Unsupported queue decision')
    rel = allowed[kind][0]
    pull_inputs(s, product, ws)
    path = ws / rel
    path.write_text(tick(path.read_text(), item, decision, c.get('note', '')))
    log_line(ws, f'owner ticked {decision} on {item} in the dashboard', rel, 'owner')
    prompt = f'Process my approvals in {rel}.' if kind == 'needs' else f'Process the held items in {rel}.'

    def work(run):
        run.step('orchestrator processes the decision', prompt, 'orchestrator')
        run.settle()
    execute(s, ws, product, f'{decision}: {item}', work)


def save_export(s, ws, product, c):
    """Weekly exports go in the folder the agents already read. Saving one runs no model."""
    folder = c.get('folder')
    if folder not in EXPORT_FOLDERS:
        raise ValueError('Exports go in signals-seo, reputation, conversation or reporting.')
    stem = re.sub(r'[^a-z0-9.-]+', '-', str(c.get('fileName', 'export')).lower()).strip('-.') or 'export'
    if not re.search(r'\.(csv|tsv|txt|json|md)$', stem):
        stem += '.csv'
    text = str(c.get('content', ''))
    if not text.strip():
        raise ValueError('The export is empty.')
    name = f'{dt.date.today().isoformat()}-{stem}'
    (ws / 'brand-os' / folder / name).write_text(text)
    log_line(ws, 'owner added an export', f'brand-os/{folder}/{name}', 'owner')
    push_state(s, ws, product)
