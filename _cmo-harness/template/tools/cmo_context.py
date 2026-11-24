"""Gather the facts the CMO plans from, so it never has to guess them.

    python3 -I tools/cmo_context.py [--date YYYY-MM-DD]

Writes reports/plans/<week>-context.md and prints its path. Exit code 2 means the CMO must not plan:
owner/STOP exists or an owner file is unfilled.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as h  # noqa: E402


def export_status(ws, day):
    rows = []
    for folder in h.EXPORT_FOLDERS:
        files = [p for p in (ws / 'exports' / folder).glob('*') if p.is_file() and h.file_date(p.name)]
        if not files:
            rows.append((folder, '-', '-', 'missing'))
            continue
        newest = max(files, key=lambda p: h.file_date(p.name))
        age = (day - h.file_date(newest.name)).days
        rows.append((folder, newest.name, str(age), 'fresh' if age <= h.FRESH_DAYS else 'stale'))
    return rows


def queue_status(ws, day):
    out = {}
    for name in ('needs-your-ok', 'held-for-voice-review'):
        p = ws / 'queue' / f'{name}.md'
        items = [i for i in h.parse_queue(p.read_text()) if i['section'] == 'open'] if p.exists() else []
        undecided = [i for i in items if not i['ticked']]
        ticked = [i for i in items if i['ticked']]
        oldest = max(((day - h.item_date(i['id'])).days for i in undecided), default=0)
        out[name] = dict(open=len(items), undecided=len(undecided), ticked=len(ticked),
                         urgent=sum(i['urgent'] for i in undecided), over_cap=sum(i['over_cap'] for i in undecided),
                         oldest_days=oldest)
    return out


def loop_inputs(ws):
    p = ws / 'loop/next-week-inputs.md'
    if not p.exists():
        return {}
    this_week = p.read_text().partition('## This week')[2].partition('\n## History')[0]
    out = {}
    for name, body in re.findall(r'^### +(.+?)\s*\n(.*?)(?=^### |\Z)', this_week, re.M | re.S):
        out[name.strip()] = [l[2:].strip() for l in body.splitlines() if l.startswith('- ')]
    return out


def newest(folder, pattern='*.md'):
    files = sorted(p for p in folder.glob(pattern) if h.file_date(p.name) or re.match(r'\d{4}-W\d{2}\.md$', p.name))
    return files[-1] if files else None


def build(ws, day):
    wid = h.week_id(day)
    start, end = h.week_dates(wid)
    stop = (ws / 'owner/STOP').exists()
    unfilled = h.unfilled_owner_files(ws)
    exports = export_status(ws, day)
    queues = queue_status(ws, day)
    inputs = loop_inputs(ws)
    report = newest(ws / 'reports/weekly')
    last_plan = None
    plans = sorted(p for p in (ws / 'reports/plans').glob('*-W*.md') if re.fullmatch(r'\d{4}-W\d{2}\.md', p.name)
                   and p.stem < wid)
    if plans:
        last_plan = plans[-1]
    log_tail = (ws / 'logs/activity.md').read_text().splitlines()[-30:] if (ws / 'logs/activity.md').exists() else []
    can_plan = not stop and not unfilled

    lines = [f'# CMO context for {wid}', '',
             'Written by tools/cmo_context.py. These are facts: use them as written, do not recompute them.', '',
             '## Week',
             f'- Week: {wid}',
             f'- Starts: {start.isoformat()} (Monday)',
             f'- Ends: {end.isoformat()} (Sunday)',
             f'- Context date: {day.isoformat()}', '',
             '## Can the CMO plan',
             f"- owner/STOP present: {'yes' if stop else 'no'}",
             f"- Unfilled owner files: {', '.join(unfilled) if unfilled else 'none'}",
             f"- Result: {'yes' if can_plan else 'NO. Stop and tell the owner.'}", '',
             '## Exports',
             '| Folder | Newest file | Age in days | Status |', '|---|---|---|---|']
    lines += [f'| {a} | {b} | {c} | {d} |' for a, b, c, d in exports]
    lines += ['', '## Queues', '| Queue | Undecided | Ticked, not processed | URGENT | OVER CAP | Oldest undecided, days |',
              '|---|---|---|---|---|---|']
    for name, q in queues.items():
        lines.append(f"| queue/{name}.md | {q['undecided']} | {q['ticked']} | {q['urgent']} | {q['over_cap']} | {q['oldest_days']} |")
    lines += ['', '## Last week']
    lines.append(f"- Weekly report: {report.relative_to(ws).as_posix() if report else 'none yet'}")
    lines.append(f"- Last plan: {last_plan.relative_to(ws).as_posix() if last_plan else 'none yet'}")
    lines += ['', '## Loop inputs (from loop/next-week-inputs.md)']
    for name in ('Double down', 'Drop', 'Test'):
        items = inputs.get(name, [])
        lines.append(f'### {name}')
        lines += [f'- {i}' for i in items] or ['- none']
    lines += ['', '## Directors available'] + [f'- {d}' for d in h.directors(ws)]
    lines += ['', '## Last 30 log lines', '```'] + log_tail + ['```', '']

    out = ws / 'reports/plans' / f'{wid}-context.md'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines))
    return out, can_plan


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--date')
    ap.add_argument('--workspace', default='.')
    a = ap.parse_args(argv)
    ws = h.root(a.workspace)
    out, can_plan = build(ws, h.today(a.date))
    print(out.relative_to(ws).as_posix())
    return 0 if can_plan else 2


if __name__ == '__main__':
    sys.exit(main())
