"""Check one agent output file against that agent's contract in tools/contracts.json."""
import csv
import io
import json
import re
from pathlib import Path

import harness as h

CHANNELS = ['linkedin', 'x', 'instagram', 'facebook', 'tiktok', 'youtube', 'blog', 'gbp', 'email', 'chat', 'report']
BASE_FRONT = ['agent', 'brief', 'sources']
URL = re.compile(r'https?://[^\s)>\]`|]+')
EMAIL = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
PHONE = re.compile(r'(?<![\w-])(?:\+\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?![\w-])')
CARD = re.compile(r'(?<![\d-])(?:\d[ -]?){13,19}(?![\d-])')


def load(ws):
    return json.loads((ws / 'tools/contracts.json').read_text())


def pattern(p):
    rx = re.escape(p)
    rx = rx.replace(re.escape('{date}'), r'\d{4}-\d{2}-\d{2}')
    rx = rx.replace(re.escape('{slug}'), r'[a-z0-9]+(?:-[a-z0-9]+){0,9}')
    rx = rx.replace(re.escape('{channel}'), '(?:' + '|'.join(CHANNELS) + ')')
    return re.compile('^' + rx + '$')


def specs(contract):
    return contract.get('outputs') or [contract]


def match_spec(contract, rel):
    for s in specs(contract):
        if pattern(s['output']).match(rel):
            return s
    return None


def cells(rows, col):
    return [(i, r.get(col, '')) for i, r in enumerate(rows, 1)]


def check_table(rel, spec, secs):
    t = spec.get('table')
    if not t:
        return []
    text = secs.get(t['in'], '')
    rows = h.table(text)
    first = next((l.strip() for l in text.splitlines() if l.strip().startswith('|')), '')
    head = [c.strip() for c in first.strip('|').split('|')] if first else []
    probs = []
    if not head:
        return [f'{rel}: "## {t["in"]}" needs a table with columns {" | ".join(t["cols"])}']
    missing = [c for c in t['cols'] if c not in head]
    if missing:
        return [f'{rel}: the {t["in"]} table is missing columns: {", ".join(missing)}']
    rows = [r for r in rows if any(v for v in r.values()) and r.get(t['cols'][0], '').lower() != 'none']
    lo, hi = t.get('min', 1), t.get('max')
    if len(rows) < lo:
        probs.append(f'{rel}: the {t["in"]} table needs at least {lo} rows (has {len(rows)})')
    if hi and len(rows) > hi:
        probs.append(f'{rel}: the {t["in"]} table allows at most {hi} rows (has {len(rows)})')
    for col, (a, b) in t.get('ints', {}).items():
        for i, v in cells(rows, col):
            if not re.fullmatch(r'\d+', v) or not a <= int(v) <= b:
                probs.append(f'{rel}: {t["in"]} row {i}: {col} must be a whole number from {a} to {b}, got "{v}"')
    for col, allowed in t.get('enums', {}).items():
        for i, v in cells(rows, col):
            if v.lower() not in allowed:
                probs.append(f'{rel}: {t["in"]} row {i}: {col} must be one of {", ".join(allowed)}, got "{v}"')
    return probs, rows


def table_rows(spec, secs):
    t = spec.get('table')
    return h.table(secs.get(t['in'], '')) if t else []


def check_rules(ws, rel, spec, meta, body, secs, text):
    probs = []
    no_sources = '\n'.join(v for k, v in secs.items() if k != 'Sources') if secs else body
    for rule in spec.get('rules', []):
        name, _, arg = rule.partition(':')
        if name == 'links':
            for i, v in cells(table_rows(spec, secs), arg):
                v = v.strip('` ')
                if not (URL.search(v) or (v and (ws / v).exists())):
                    probs.append(f'{rel}: row {i}: {arg} must be a web link or a file in this workspace, got "{v}"')
        elif name == 'utm':
            for u in URL.findall(no_sources):
                if 'utm_campaign=' not in u:
                    probs.append(f'{rel}: link {u} has no utm_campaign tag')
        elif name == 'no_pii':
            if EMAIL.search(text):
                probs.append(f'{rel}: contains an email address. Use the CRM record id.')
            if PHONE.search(text):
                probs.append(f'{rel}: contains a phone number. Use the CRM record id.')
        elif name == 'no_card':
            if CARD.search(text):
                probs.append(f'{rel}: contains a long number that could be a card or account number')
        elif name == 'loop_data':
            refs = re.findall(r'loop/\d{4}-\d{2}-\d{2}-data\.md', text)
            if not refs:
                probs.append(f'{rel}: does not cite a loop data file (loop/YYYY-MM-DD-data.md)')
            for r in refs:
                if not (ws / r).exists():
                    probs.append(f'{rel}: cites {r}, which does not exist. Run python3 -I tools/loop_data.py')
        elif name == 'queue_ids':
            q = (ws / 'queue/needs-your-ok.md').read_text() if (ws / 'queue/needs-your-ok.md').exists() else ''
            for qid in sorted(set(re.findall(r'Q-\d{8}-\d+', text))):
                if f'### {qid}:' not in q:
                    probs.append(f'{rel}: {qid} is not an item in queue/needs-your-ok.md')
        elif name == 'paste':
            if meta.get('status') == 'posted':
                if not meta.get('confirmation'):
                    probs.append(f'{rel}: status is posted, so the front matter needs a confirmation: line')
            elif '[PASTE]' not in text:
                probs.append(f'{rel}: must carry [PASTE] until the platform confirms it posted')
        elif name == 'send':
            if '[SEND]' not in text:
                probs.append(f'{rel}: must carry [SEND]. Nothing here sends it.')
        elif name == 'render':
            if meta.get('render') != 'done' and '[RENDER]' not in text:
                probs.append(f'{rel}: must carry [RENDER] until render is done')
        elif name == 'hex':
            for i, v in cells(table_rows(spec, secs), 'Hex'):
                if not re.fullmatch(r'#[0-9A-Fa-f]{6}', v.strip('` ')):
                    probs.append(f'{rel}: row {i}: Hex must look like #1A2B3C, got "{v}"')
        elif name == 'owner_link':
            rules = (ws / 'owner/sales-rules.md').read_text() if (ws / 'owner/sales-rules.md').exists() else ''
            for u in URL.findall(text):
                if u.rstrip('.,') not in rules:
                    probs.append(f'{rel}: link {u} is not in owner/sales-rules.md')
        elif name == 'cite_paths':
            week = secs.get('This week', '')
            for line in week.splitlines():
                if line.startswith('- '):
                    m = re.search(r'\(([\w./-]+\.\w+)\)', line)
                    if not m:
                        probs.append(f'{rel}: "{line[:60]}" needs its source file in brackets')
                    elif not (ws / m.group(1)).exists():
                        probs.append(f'{rel}: cites {m.group(1)}, which does not exist')
            for sub in ('Double down', 'Drop', 'Test'):
                if f'### {sub}' not in week:
                    probs.append(f'{rel}: This week needs a "### {sub}" list')
    return probs


def check_file(ws, agent, rel, contracts=None):
    contracts = contracts or load(ws)
    contract = contracts['agents'].get(agent)
    if not contract:
        return []
    spec = match_spec(contract, rel)
    if not spec:
        want = ' or '.join(s['output'] for s in specs(contract))
        return [f'{rel}: {agent} writes {want}, so this path is wrong']
    p = ws / rel
    if not p.exists():
        return [f'{rel}: the file does not exist']
    text = p.read_text()
    if 'csv' in spec:
        head = next(csv.reader(io.StringIO(text)), [])
        missing = [c for c in spec['csv'] if c not in head]
        probs = [f'{rel}: missing csv columns: {", ".join(missing)}'] if missing else []
        if len(text.strip().splitlines()) < 2:
            probs.append(f'{rel}: has no rows')
        return probs
    probs = []
    meta, body = h.front_matter(text)
    if spec.get('front_free'):
        meta = meta or {}
        body = text if not meta else body
    else:
        if meta is None:
            return [f'{rel}: no front matter. Start with ---, then {", ".join(BASE_FRONT + spec.get("front", []))}']
        for k in BASE_FRONT + spec.get('front', []):
            if k not in meta or meta[k] in ('', []):
                probs.append(f'{rel}: front matter needs "{k}"')
        if meta.get('agent') and meta.get('agent') != agent:
            probs.append(f'{rel}: agent is {meta.get("agent")}, expected {agent}')
        for k, allowed in spec.get('values', {}).items():
            if k in meta and str(meta[k]) not in allowed:
                probs.append(f'{rel}: {k} must be one of {", ".join(allowed)}, got "{meta[k]}"')
    probs += check_sections_simple(rel, body, spec['sections'])
    secs = dict(h.sections(body))
    t = check_table(rel, spec, secs)
    if isinstance(t, tuple):
        probs += t[0]
    else:
        probs += t
    probs += check_rules(ws, rel, spec, meta or {}, body, secs, text)
    probs += [f'{rel}: uses a dash character ({d!r}). The writing rules allow none.' for d in h.DASHES if d in text]
    if re.search(r'\bexactly\b', text, re.I):
        probs.append(f'{rel}: uses the word "exactly", which the writing rules ban')
    return probs


def check_sections_simple(rel, body, required):
    found = [name for name, _ in h.sections(body)]
    missing = [s for s in required if s not in found]
    probs = [f'{rel}: missing section "## {s}"' for s in missing]
    if not missing and [s for s in found if s in required] != required:
        probs.append(f'{rel}: sections must come in this order: {", ".join(required)}')
    return probs


def output_template(agent, contract, rules_text):
    """Plain words for the agent file, made from the same contract the check uses."""
    out = []
    for s in specs(contract):
        lines = [f"Write `{s['output']}`." if 'csv' not in s else f"Write `{s['output']}` as a CSV file."]
        if 'csv' in s:
            lines.append(f"Columns, in this order: {', '.join(s['csv'])}. One row per change.")
        else:
            front = BASE_FRONT + s.get('front', [])
            if s.get('front_free'):
                lines.append('This file has no front matter. Keep its existing layout.')
            else:
                lines.append('Start it with this front matter:')
                lines.append('')
                lines.append('    ---')
                for k in front:
                    v = {'agent': agent, 'brief': '<your B brief id>', 'sources': '[<files and links you used>]'}.get(k)
                    if v is None:
                        allowed = s.get('values', {}).get(k)
                        v = ' or '.join(allowed) if allowed else f'<{k.replace("_", " ")}>'
                    lines.append(f'    {k}: {v}')
                lines.append('    ---')
                lines.append('')
            lines.append('Then these sections, in this order: ' + ', '.join(f'"## {x}"' for x in s['sections']) + '.')
            t = s.get('table')
            if t:
                if t.get('min', 1) == 0:
                    rng = 'one row per item; it may have no rows, then write a single row starting with none'
                else:
                    rng = f"at least {t.get('min', 1)}" + (f" and at most {t['max']}" if t.get('max') else '') + ' rows'
                lines.append(f"Under \"## {t['in']}\", a table with the columns {' | '.join(t['cols'])}, {rng}.")
                for col, (a, b) in t.get('ints', {}).items():
                    lines.append(f'{col} is a whole number from {a} to {b}.')
                for col, allowed in t.get('enums', {}).items():
                    lines.append(f"{col} is one of: {', '.join(allowed)}.")
        for rule in s.get('rules', []):
            name, _, arg = rule.partition(':')
            lines.append(rules_text[name].replace('{col}', arg))
        out.append('\n'.join(lines))
    key = ('In paths, {date} is today as YYYY-MM-DD, {slug} is 3 to 6 lowercase words joined by hyphens'
           ' and {channel} is one of: ' + ', '.join(CHANNELS) + '.')
    return '\n\n'.join(out) + '\n\n' + key
