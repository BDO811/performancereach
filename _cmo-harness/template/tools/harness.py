"""Shared helpers for the CMO harness tools. Standard library only.

Every tool runs from the workspace root:  python3 -I tools/<tool>.py
"""
import datetime as dt
import re
from pathlib import Path

OWNER_FILES = ['owner/targets.md', 'owner/positioning.md', 'owner/brand-voice.md',
               'owner/approval-bar.md', 'owner/budget-cap.md', 'owner/sales-rules.md']
EXPORT_FOLDERS = ['analytics', 'crm', 'calendar', 'comments', 'dms', 'email', 'payments', 'ads', 'seo', 'finance']
FRESH_DAYS = 7
DASHES = ('—', '–')


def root(path=None):
    return Path(path or '.').resolve()


def today(value=None):
    return dt.date.fromisoformat(value) if value else dt.date.today()


def week_id(day):
    year, week, _ = day.isocalendar()
    return f'{year}-W{week:02d}'


def week_start(day):
    return day - dt.timedelta(days=day.weekday())


def week_dates(wid):
    m = re.fullmatch(r'(\d{4})-W(\d{2})', wid)
    if not m:
        raise ValueError(f'not a week id: {wid}')
    start = dt.date.fromisocalendar(int(m.group(1)), int(m.group(2)), 1)
    return start, start + dt.timedelta(days=6)


def fill_prompts(text):
    return re.findall(r'\[FILL IN: *([^\]]*)\]', text or '')


def unfilled_owner_files(ws):
    out = []
    for rel in OWNER_FILES:
        p = ws / rel
        if not p.exists() or not p.read_text().strip() or fill_prompts(p.read_text()):
            out.append(rel)
    return out


def front_matter(text):
    """Flat key: value front matter. Lists are written as [a, b]."""
    m = re.match(r'^---\n(.*?)\n---\n?', text, re.S)
    if not m:
        return None, text
    meta = {}
    for line in m.group(1).splitlines():
        if ':' in line and not line.startswith(' '):
            k, v = line.split(':', 1)
            v = v.strip()
            if v.startswith('[') and v.endswith(']'):
                v = [x.strip() for x in v[1:-1].split(',') if x.strip()]
            meta[k.strip()] = v
    return meta, text[m.end():]


def sections(body):
    """Ordered list of (heading, text) for level two headings."""
    parts = re.split(r'^## +(.+?)\s*$', body, flags=re.M)
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]


def table(text):
    """Rows of the first markdown table in text, as dicts keyed by header."""
    lines = [l.strip() for l in text.splitlines() if l.strip().startswith('|')]
    if len(lines) < 2:
        return []
    cells = lambda l: [c.strip() for c in l.strip('|').split('|')]
    head = cells(lines[0])
    return [dict(zip(head, cells(l))) for l in lines[2:]]


# Queue files: same format as the Social team, so both read the same file.
ITEM = re.compile(r'^### ((?:Q|H)-\d{8}-\d+): *(.*)$', re.M)


def parse_queue(text):
    open_part, _, done_part = text.partition('\n## Done')
    open_part = open_part.partition('\n## Open')[2]

    def items(part, section):
        marks = list(ITEM.finditer(part))
        out = []
        for i, m in enumerate(marks):
            end = marks[i + 1].start() if i + 1 < len(marks) else len(part)
            body = part[m.end():end]
            fields = {k.strip(): v.strip() for k, v in re.findall(r'^- (?!\[)([^:\n]+):[ \t]*(.*)$', body, re.M)}
            ticks = re.findall(r'^- \[[xX]\] *([^\n]*)$', body, re.M)
            out.append({'id': m.group(1), 'title': m.group(2).strip(), 'section': section, 'fields': fields,
                        'ticked': ticks, 'urgent': 'URGENT' in m.group(2), 'over_cap': 'OVER CAP' in m.group(2),
                        'text': part[m.start():end]})
        return out

    return items(open_part, 'open') + items(done_part, 'done')


def item_date(item_id):
    return dt.date(int(item_id[2:6]), int(item_id[6:8]), int(item_id[8:10]))


def file_date(name):
    m = re.match(r'(\d{4}-\d{2}-\d{2})', name)
    return dt.date.fromisoformat(m.group(1)) if m else None


def log(ws, agent, action, file='-', when=None):
    when = when or dt.datetime.now()
    with open(ws / 'logs/activity.md', 'a') as f:
        f.write(f"{when:%Y-%m-%d %H:%M} | {agent} | {action} | {file}\n")


def directors(ws):
    return sorted(p.stem for p in (ws / '.claude/agents').glob('director-*.md'))
