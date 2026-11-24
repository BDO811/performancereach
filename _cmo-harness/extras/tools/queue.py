"""Process the owner's ticked boxes in queue/needs-your-ok.md.

    python3 -I tools/queue.py process     move decided items to Done, log them, print what to route
    python3 -I tools/queue.py status      print open item counts

Only the owner ticks a box. This tool never ticks one: it only moves items the owner already decided.
An item with both boxes ticked is left open and reported, so the owner can fix it.
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as h  # noqa: E402

QUEUE = 'queue/needs-your-ok.md'


def decision(item):
    ticks = {t.split()[0].lower() for t in item['ticked'] if t.split()}
    if ticks == {'approve'}:
        return 'approved'
    if ticks == {'reject'}:
        return 'rejected'
    if ticks:
        return 'conflict'
    return None


def process(ws, when=None):
    path = ws / QUEUE
    text = path.read_text()
    head, sep, done = text.partition('\n## Done')
    if not sep:
        raise SystemExit(f'{QUEUE} has no "## Done" section')
    decided, conflicts = [], []
    for item in h.parse_queue(text):
        if item['section'] != 'open':
            continue
        d = decision(item)
        if d == 'conflict':
            conflicts.append(item)
        elif d:
            decided.append((item, d))
    for item, _ in decided:
        head = head.replace(item['text'], '', 1)
    moved = ''.join(item['text'].rstrip('\n') + '\n\n' for item, _ in decided)
    head = head.rstrip('\n') + '\n'
    done = done.lstrip('\n')
    path.write_text(head + sep + '\n\n' + moved + done)
    for item, d in decided:
        h.log(ws, 'cmo', f"owner {d} {item['id']}", QUEUE, when)
    return decided, conflicts


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('action', choices=['process', 'status'])
    ap.add_argument('--workspace', default='.')
    a = ap.parse_args(argv)
    ws = h.root(a.workspace)
    if (ws / 'owner/STOP').exists():
        print('stopped: owner/STOP present')
        return 2
    if a.action == 'status':
        items = [i for i in h.parse_queue((ws / QUEUE).read_text()) if i['section'] == 'open']
        print(f"open {len(items)}, ticked {sum(bool(i['ticked']) for i in items)}, "
              f"urgent {sum(i['urgent'] for i in items)}")
        return 0
    decided, conflicts = process(ws, dt.datetime.now())
    for item, d in decided:
        f = item['fields']
        note = f.get('Owner note', '')
        print(f"{d.upper()} {item['id']}: {item['title']} | file {f.get('File', '-')} | "
              f"requested by {f.get('Requested by', '-')}" + (f' | owner note: {note}' if note else ''))
    for item in conflicts:
        print(f"BOTH BOXES {item['id']}: {item['title']} (left open for the owner)")
    if not decided and not conflicts:
        print('nothing ticked')
    return 0


if __name__ == '__main__':
    sys.exit(main())
