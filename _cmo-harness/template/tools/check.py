"""Check an agent's output against its contract.

    python3 -I tools/check.py plan [--week 2026-W48]                the CMO's weekly plan and its director briefs
    python3 -I tools/check.py agent-briefs --brief C-YYYYMMDD-NN    a director's agent briefs for one CMO brief
    python3 -I tools/check.py return --brief C-YYYYMMDD-NN          a director's return to the CMO
    python3 -I tools/check.py output --brief B-YYYYMMDD-NN          an agent's output against its contract

Prints one line per problem and exits 1 when there is any. Give the printed problems back to the agent
that wrote the file and run it again.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as h  # noqa: E402
import contracts_check as cc  # noqa: E402

PLAN_KEYS = ['week', 'starts', 'goal', 'directors', 'spend_planned', 'status']
PLAN_SECTIONS = ['Goal', 'Last week', 'Candidates', 'Priorities', 'Channel mix', 'Spend plan', 'Blocked', 'Briefs']
SCORE_COLS = ['Urgency', 'Fit', 'Evidence', 'Value']
CANDIDATE_COLS = ['Candidate', 'Source'] + SCORE_COLS + ['Score', 'Decision']
DECISIONS = {'plan', 'drop', 'later'}
BRIEF_KEYS = ['id', 'director', 'week', 'priority', 'order', 'due', 'depends_on', 'owner_gate']
BRIEF_SECTIONS = ['Goal', 'Inputs', 'Outputs', 'Checks', 'Needs the owner']
OWNER_GATES = {'none', 'queue', 'urgent'}
BRIEF_NAME = re.compile(r'^(C-(\d{8})-(\d{2}))-(director-[a-z-]+)\.md$')


def dash_problems(rel, text):
    return [f'{rel}: uses a dash character ({d!r}). The writing rules allow none.' for d in h.DASHES if d in text]


def check_sections(rel, body, required):
    found = [name for name, _ in h.sections(body)]
    missing = [s for s in required if s not in found]
    probs = [f'{rel}: missing section "## {s}"' for s in missing]
    if not missing and [s for s in found if s in required] != required:
        probs.append(f'{rel}: sections must come in this order: {", ".join(required)}')
    return probs


def check_candidates(rel, text):
    rows = h.table(text)
    probs = []
    if not rows:
        return [f'{rel}: Candidates needs a table with columns {" | ".join(CANDIDATE_COLS)}'], {}
    missing = [c for c in CANDIDATE_COLS if c not in rows[0]]
    if missing:
        return [f'{rel}: Candidates table is missing columns: {", ".join(missing)}'], {}
    by_name = {}
    for n, r in enumerate(rows, 1):
        label = f'{rel}: Candidates row {n} ({r["Candidate"]})'
        try:
            scores = {c: int(r[c]) for c in SCORE_COLS}
            total = int(r['Score'])
        except ValueError:
            probs.append(f'{label}: scores must be whole numbers')
            continue
        for c, v in scores.items():
            if not 0 <= v <= 3:
                probs.append(f'{label}: {c} must be 0 to 3, got {v}')
        if total != sum(scores.values()):
            probs.append(f'{label}: Score {total} is not the sum of the four scores ({sum(scores.values())})')
        decision = r['Decision'].lower()
        if decision not in DECISIONS:
            probs.append(f'{label}: Decision must be plan, drop or later')
        if scores['Evidence'] == 0 and decision != 'drop':
            probs.append(f'{label}: Evidence 0 means the candidate is dropped')
        if not r['Source'] or r['Source'] == '-':
            if scores['Evidence'] > 0:
                probs.append(f'{label}: Evidence above 0 needs a Source')
        by_name[r['Candidate'].lower()] = dict(score=total, decision=decision)
    return probs, by_name


def check_priorities(rel, text, candidates):
    items = re.findall(r'^\s*\d+\.\s+(P\d+):\s*(.+?)\s*\|\s*score\s+(\d+)\s*\|\s*(director-[a-z-]+)\s*$', text, re.M | re.I)
    probs = []
    if not 3 <= len(items) <= 5:
        probs.append(f'{rel}: Priorities needs 3 to 5 lines like "1. P1: <candidate> | score 10 | director-research" '
                     f'(found {len(items)})')
    planned = {k: v for k, v in candidates.items() if v['decision'] == 'plan'}
    for pid, name, score, _ in items:
        c = candidates.get(name.lower())
        if not c:
            probs.append(f'{rel}: {pid} "{name}" is not a row in Candidates')
        elif c['decision'] != 'plan':
            probs.append(f'{rel}: {pid} "{name}" is marked {c["decision"]} in Candidates')
        elif int(score) != c['score']:
            probs.append(f'{rel}: {pid} score {score} does not match Candidates ({c["score"]})')
    scores = [int(s) for _, _, s, _ in items]
    if scores != sorted(scores, reverse=True):
        probs.append(f'{rel}: Priorities must run from the highest score to the lowest')
    if items and planned and len(items) < min(3, len(planned)):
        probs.append(f'{rel}: more candidates are marked plan than appear in Priorities')
    return probs, [(p, d) for p, _, _, d in items]


def check_spend(rel, text):
    if re.search(r'none this week', text, re.I):
        return []
    rows = h.table(text)
    if not rows:
        return [f'{rel}: Spend plan needs a table (Item | Amount | Channel | Queue) or the words "None this week."']
    return [f'{rel}: Spend plan row "{r.get("Item", "?")}" has no queue item id (Q-YYYYMMDD-NN). Every spend waits.'
            for r in rows if not re.search(r'Q-\d{8}-\d+', r.get('Queue', ''))]


def check_brief(ws, path, wid, start, end, director_names, all_ids):
    rel = path.relative_to(ws).as_posix()
    text = path.read_text()
    meta, body = h.front_matter(text)
    if meta is None:
        return [f'{rel}: no front matter'], None
    probs = [f'{rel}: front matter is missing "{k}"' for k in BRIEF_KEYS if k not in meta]
    m = BRIEF_NAME.match(path.name)
    if not m:
        probs.append(f'{rel}: file name must be C-YYYYMMDD-NN-<director>.md')
    else:
        if meta.get('id') != m.group(1):
            probs.append(f'{rel}: id {meta.get("id")} does not match the file name ({m.group(1)})')
        if meta.get('director') != m.group(4):
            probs.append(f'{rel}: director {meta.get("director")} does not match the file name ({m.group(4)})')
    if meta.get('director') not in director_names:
        probs.append(f'{rel}: {meta.get("director")} is not a director in .claude/agents/')
    if meta.get('week') != wid:
        probs.append(f'{rel}: week {meta.get("week")} is not {wid}')
    try:
        due = h.today(meta.get('due'))
        if not start <= due <= end:
            probs.append(f'{rel}: due {due} is outside {wid} ({start} to {end})')
    except (TypeError, ValueError):
        probs.append(f'{rel}: due must be a date like {start}')
    if meta.get('owner_gate') not in OWNER_GATES:
        probs.append(f'{rel}: owner_gate must be none, queue or urgent')
    if not str(meta.get('order', '')).isdigit():
        probs.append(f'{rel}: order must be a whole number')
    deps = meta.get('depends_on') or []
    deps = deps if isinstance(deps, list) else [deps]
    for d in deps:
        if d not in all_ids:
            probs.append(f'{rel}: depends_on {d} is not a brief this week')
    probs += check_sections(rel, body, BRIEF_SECTIONS)
    secs = dict(h.sections(body))
    for line in secs.get('Inputs', '').splitlines():
        m2 = re.match(r'^- `?([\w./-]+)`?', line.strip())
        if not m2 or '(after C-' in line:
            continue
        target = m2.group(1)
        if '/' in target and not (ws / target).exists():
            probs.append(f'{rel}: input {target} does not exist. Mark inputs another brief makes with "(after C-...)".')
    if not re.search(r'^- ', secs.get('Outputs', ''), re.M):
        probs.append(f'{rel}: Outputs must list at least one file')
    probs += dash_problems(rel, text)
    return probs, meta


def check_plan(ws, wid):
    start, end = h.week_dates(wid)
    path = ws / 'reports/plans' / f'{wid}.md'
    rel = path.relative_to(ws).as_posix()
    if not path.exists():
        return [f'{rel}: the plan file does not exist']
    text = path.read_text()
    meta, body = h.front_matter(text)
    if meta is None:
        return [f'{rel}: no front matter']
    probs = [f'{rel}: front matter is missing "{k}"' for k in PLAN_KEYS if k not in meta]
    if meta.get('week') != wid:
        probs.append(f'{rel}: week is {meta.get("week")}, expected {wid}')
    if meta.get('starts') != start.isoformat():
        probs.append(f'{rel}: starts is {meta.get("starts")}, expected {start}')
    if meta.get('status') not in ('planned', 'in progress', 'closed'):
        probs.append(f'{rel}: status must be planned, in progress or closed')
    director_names = set(h.directors(ws))
    listed = meta.get('directors') or []
    listed = listed if isinstance(listed, list) else [listed]
    for d in listed:
        if d not in director_names:
            probs.append(f'{rel}: {d} is not a director in .claude/agents/')
    probs += check_sections(rel, body, PLAN_SECTIONS)
    secs = dict(h.sections(body))
    cprobs, candidates = check_candidates(rel, secs.get('Candidates', ''))
    probs += cprobs
    pprobs, priorities = check_priorities(rel, secs.get('Priorities', ''), candidates)
    probs += pprobs
    probs += check_spend(rel, secs.get('Spend plan', ''))
    probs += dash_problems(rel, text)

    brief_dir = ws / 'drafts/briefs/cmo'
    named = re.findall(r'C-\d{8}-\d{2}', secs.get('Briefs', ''))
    later = re.findall(r'C-\d{8}-\d{2}', secs.get('Later briefs', ''))
    files = {BRIEF_NAME.match(p.name).group(1): p for p in brief_dir.glob('C-*.md') if BRIEF_NAME.match(p.name)}
    week_ids = {i for i in files if start <= h.today(f'{i[2:6]}-{i[6:8]}-{i[8:10]}') <= end}
    if not named:
        probs.append(f'{rel}: Briefs must list the brief ids (C-YYYYMMDD-NN) in run order')
    briefed = set()
    orders = []
    for bid in named:
        if bid not in files:
            probs.append(f'{rel}: brief {bid} is listed but drafts/briefs/cmo/{bid}-<director>.md does not exist')
            continue
        bprobs, bmeta = check_brief(ws, files[bid], wid, start, end, director_names, set(named))
        probs += bprobs
        if bmeta:
            briefed.add(bmeta.get('director'))
            orders.append(bmeta.get('order'))
            pid = bmeta.get('priority')
            if pid not in [p for p, _ in priorities] and pid != 'routine':
                probs.append(f'{files[bid].relative_to(ws).as_posix()}: priority {pid} is not in the plan '
                             f'(use a P number from Priorities, or "routine")')
    if len(orders) != len(set(orders)):
        probs.append(f'{rel}: two briefs share the same order number')
    for bid in later:
        if bid not in files:
            probs.append(f'{rel}: later brief {bid} is listed but its file does not exist')
            continue
        lprobs, lmeta = check_brief(ws, files[bid], wid, start, end, director_names, set(named) | set(later))
        probs += lprobs
    for bid in sorted(week_ids - set(named) - set(later)):
        probs.append(f'{rel}: drafts/briefs/cmo/{files[bid].name} is not listed in Briefs')
    for d in listed:
        if d in director_names and d not in briefed:
            probs.append(f'{rel}: {d} is in directors but has no brief')
    for d in briefed - set(listed):
        probs.append(f'{rel}: {d} has a brief but is not in directors')
    for pid, d in priorities:
        if d not in briefed:
            probs.append(f'{rel}: {pid} is owned by {d}, which has no brief')
    return probs


AGENT_KEYS = ['id', 'agent', 'director', 'from', 'order', 'due', 'depends_on']
AGENT_SECTIONS = ['Goal', 'Inputs', 'Output', 'Check']
AGENT_NAME = re.compile(r'^(B-\d{8}-\d{2})-([a-z0-9-]+)\.md$')
RETURN_KEYS = ['brief', 'director', 'status', 'agent_briefs']
RETURN_SECTIONS = ['Done', 'Waiting for the owner', 'Blocked', 'Needs another department']


def as_list(v):
    return v if isinstance(v, list) else ([v] if v else [])


def team(ws, director):
    p = ws / '.claude/agents' / f'{director}.md'
    if not p.exists():
        return set()
    part = p.read_text().partition('## Your team')[2].partition('\n## ')[0]
    return set(re.findall(r'^\| `([a-z0-9-]+)` \|', part, re.M))


def paths(text):
    return [m.group(1) for m in re.finditer(r'^- `([^`]+)`', text, re.M)]


def cmo_brief(ws, bid):
    hits = sorted((ws / 'drafts/briefs/cmo').glob(f'{bid}-*.md'))
    if not hits:
        return None, None, None
    meta, body = h.front_matter(hits[0].read_text())
    return hits[0], meta, dict(h.sections(body))


def agent_briefs_for(ws, bid):
    out = []
    for p in sorted((ws / 'drafts/briefs').glob('*/B-*.md')):
        meta, body = h.front_matter(p.read_text())
        if meta and meta.get('from') == bid:
            out.append((p, meta, dict(h.sections(body)), body))
    return out


def check_agent_briefs(ws, bid):
    cpath, cmeta, csecs = cmo_brief(ws, bid)
    if not cpath:
        return [f'drafts/briefs/cmo/{bid}-<director>.md does not exist']
    director = cmeta.get('director')
    dept = director.replace('director-', '')
    members = team(ws, director)
    start, _ = h.week_dates(cmeta.get('week'))
    cdue = h.today(cmeta.get('due'))
    briefs = agent_briefs_for(ws, bid)
    if not briefs:
        return [f'no agent briefs in drafts/briefs/{dept}/ have from: {bid}']
    probs = []
    all_ids = {}
    for p in (ws / 'drafts/briefs').glob('*/B-*.md'):
        m = AGENT_NAME.match(p.name)
        if m:
            all_ids.setdefault(m.group(1), []).append(p.relative_to(ws).as_posix())
    for i, files in all_ids.items():
        if len(files) > 1:
            probs.append(f'brief id {i} is used twice: {", ".join(files)}')
    ids = {meta['id']: meta for _, meta, _, _ in briefs if 'id' in meta}
    contracts = cc.load(ws)
    made = set()
    for p, meta, secs, body in briefs:
        rel = p.relative_to(ws).as_posix()
        probs += [f'{rel}: front matter is missing "{k}"' for k in AGENT_KEYS if k not in meta]
        m = AGENT_NAME.match(p.name)
        if not m:
            probs.append(f'{rel}: file name must be B-YYYYMMDD-NN-<agent>.md')
        else:
            if meta.get('id') != m.group(1):
                probs.append(f'{rel}: id {meta.get("id")} does not match the file name ({m.group(1)})')
            if meta.get('agent') != m.group(2):
                probs.append(f'{rel}: agent {meta.get("agent")} does not match the file name ({m.group(2)})')
        if p.parent.name != dept:
            probs.append(f'{rel}: briefs for {director} go in drafts/briefs/{dept}/')
        if meta.get('director') != director:
            probs.append(f'{rel}: director must be {director}, the owner of {bid}')
        if meta.get('agent') not in members:
            probs.append(f'{rel}: {meta.get("agent")} is not in the {director} team')
        try:
            due = h.today(meta.get('due'))
            if not start <= due <= cdue:
                probs.append(f'{rel}: due {due} must be between {start} and the CMO brief due date {cdue}')
        except (TypeError, ValueError):
            probs.append(f'{rel}: due must be a date')
        order = str(meta.get('order', ''))
        if not order.isdigit():
            probs.append(f'{rel}: order must be a whole number')
        for d in as_list(meta.get('depends_on')):
            dep = ids.get(d)
            if not dep:
                probs.append(f'{rel}: depends_on {d} is not an agent brief for {bid}')
            elif order.isdigit() and str(dep.get('order', '')).isdigit() and int(dep['order']) >= int(order):
                probs.append(f'{rel}: depends on {d}, so its order must come after {dep["order"]}')
        probs += check_sections(rel, body, AGENT_SECTIONS)
        for line in secs.get('Inputs', '').splitlines():
            m2 = re.match(r'^- `([^`]+)`', line.strip())
            if not m2:
                continue
            after = re.search(r'\(after (B-\d{8}-\d{2})\)', line)
            if after:
                if after.group(1) not in as_list(meta.get('depends_on')):
                    probs.append(f'{rel}: input {m2.group(1)} comes after {after.group(1)}, so depends_on must list it')
            elif '(after C-' not in line and not (ws / m2.group(1)).exists():
                probs.append(f'{rel}: input {m2.group(1)} does not exist. Mark inputs another brief makes with "(after B-...)".')
        outs = paths(secs.get('Output', ''))
        if not outs:
            probs.append(f'{rel}: Output must list the file the agent writes, as - `path`')
        contract = contracts['agents'].get(meta.get('agent'))
        for o in outs:
            if contract and not cc.match_spec(contract, o):
                want = ' or '.join(x['output'] for x in cc.specs(contract))
                probs.append(f'{rel}: Output {o} does not fit {meta.get("agent")}, which writes {want}')
        made.update(outs)
        probs += dash_problems(rel, p.read_text())
    for out in paths(csecs.get('Outputs', '')):
        if out not in made and not out.startswith('queue/'):
            probs.append(f'{bid} asks for {out}, but no agent brief has it as Output')
    return probs


def check_return(ws, bid):
    cpath, cmeta, csecs = cmo_brief(ws, bid)
    if not cpath:
        return [f'drafts/briefs/cmo/{bid}-<director>.md does not exist']
    path = ws / 'drafts/returns' / f'{bid}-return.md'
    rel = path.relative_to(ws).as_posix()
    if not path.exists():
        return [f'{rel}: the return file does not exist']
    text = path.read_text()
    meta, body = h.front_matter(text)
    if meta is None:
        return [f'{rel}: no front matter']
    probs = [f'{rel}: front matter is missing "{k}"' for k in RETURN_KEYS if k not in meta]
    if meta.get('brief') != bid:
        probs.append(f'{rel}: brief must be {bid}')
    if meta.get('director') != cmeta.get('director'):
        probs.append(f'{rel}: director must be {cmeta.get("director")}')
    if meta.get('status') not in ('done', 'partial', 'blocked'):
        probs.append(f'{rel}: status must be done, partial or blocked')
    probs += check_sections(rel, body, RETURN_SECTIONS)
    secs = dict(h.sections(body))
    written = {m['id'] for _, m, _, _ in agent_briefs_for(ws, bid) if 'id' in m}
    listed = set(as_list(meta.get('agent_briefs')))
    for b in sorted(listed - written):
        probs.append(f'{rel}: agent_briefs lists {b}, which is not an agent brief for {bid}')
    for b in sorted(written - listed):
        probs.append(f'{rel}: agent_briefs is missing {b}')
    done = paths(secs.get('Done', ''))
    for d in done:
        if not (ws / d).exists():
            probs.append(f'{rel}: Done lists {d}, which does not exist')
    for q in re.findall(r'Q-\d{8}-\d+', secs.get('Waiting for the owner', '')):
        qtext = (ws / 'queue/needs-your-ok.md').read_text() if (ws / 'queue/needs-your-ok.md').exists() else ''
        if f'### {q}:' not in qtext:
            probs.append(f'{rel}: {q} is not in queue/needs-your-ok.md')
    blocked = secs.get('Blocked', '').strip()
    if meta.get('status') == 'done':
        if blocked.lower().rstrip('.') not in ('nothing', '- nothing'):
            probs.append(f'{rel}: status is done, so Blocked must say Nothing')
        for out in paths(csecs.get('Outputs', '')):
            if out not in done and not out.startswith('queue/'):
                probs.append(f'{rel}: status is done, but {out} from {bid} is not under Done')
    probs += dash_problems(rel, text)
    return probs


def check_output(ws, bid):
    hits = sorted((ws / 'drafts/briefs').glob(f'*/{bid}-*.md'))
    if not hits:
        return [f'agent brief {bid} does not exist in drafts/briefs/']
    meta, body = h.front_matter(hits[0].read_text())
    agent = (meta or {}).get('agent')
    outs = paths(dict(h.sections(body)).get('Output', ''))
    if not outs:
        return [f'{hits[0].relative_to(ws).as_posix()}: lists no Output']
    contracts = cc.load(ws)
    probs = []
    for o in outs:
        probs += cc.check_file(ws, agent, o, contracts)
    return probs


CHECKS = {'plan': check_plan, 'agent-briefs': check_agent_briefs, 'return': check_return, 'output': check_output}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('check', choices=sorted(CHECKS))
    ap.add_argument('--week')
    ap.add_argument('--date')
    ap.add_argument('--brief', help='the CMO brief id (agent-briefs, return) or the agent brief id (output)')
    ap.add_argument('--workspace', default='.')
    a = ap.parse_args(argv)
    ws = h.root(a.workspace)
    if a.check == 'plan':
        target = a.week or h.week_id(h.today(a.date))
    elif not a.brief:
        ap.error(f'{a.check} needs --brief')
    else:
        target = a.brief
    probs = CHECKS[a.check](ws, target)
    for p in probs:
        print(p)
    if not probs:
        print(f'{a.check} {target}: ok')
    return 1 if probs else 0


if __name__ == '__main__':
    sys.exit(main())
