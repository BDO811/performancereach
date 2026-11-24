"""Compute the week's loop numbers from the exports, so no agent does arithmetic.

    python3 -I tools/loop_data.py [--date YYYY-MM-DD] [--days 7]

Reads the CSV files in exports/ (columns in exports/README.md) for the days ending on --date, and
writes loop/<date>-data.md: posts, revenue by campaign, calls, email, spend and cost per call.
Every number in it is a count or a sum of export rows. Nothing is estimated.
"""
import argparse
import csv
import datetime as dt
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as h  # noqa: E402

NONE = '(none)'


def rows(ws, folder, start, end, notes):
    out = []
    for f in sorted((ws / 'exports' / folder).glob('*.csv')):
        with open(f, newline='') as fh:
            for r in csv.DictReader(fh):
                r = {(k or '').strip(): (v or '').strip() for k, v in r.items()}
                try:
                    d = dt.date.fromisoformat(r.get('date', ''))
                except ValueError:
                    notes.add(f'exports/{folder}/{f.name}: a row has no valid date and was skipped')
                    continue
                if start <= d <= end:
                    r['_file'] = f'exports/{folder}/{f.name}'
                    out.append(r)
    return out


def num(r, col, notes, folder):
    if col not in r:
        notes.add(f'exports/{folder}: column "{col}" is missing, so it counts as 0')
        return 0.0
    try:
        return float(r[col] or 0)
    except ValueError:
        notes.add(f'{r["_file"]}: "{r[col]}" in column "{col}" is not a number, counted as 0')
        return 0.0


def fmt(x):
    return f'{x:.2f}' if isinstance(x, float) and x != int(x) else str(int(x))


def md_table(head, body):
    lines = ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    lines += ['| ' + ' | '.join(fmt(c) if isinstance(c, (int, float)) else str(c) for c in r) + ' |' for r in body]
    return lines if body else lines + ['| ' + ' | '.join(['none'] + [''] * (len(head) - 1)) + ' |']


def build(ws, day, days=7):
    start = day - dt.timedelta(days=days - 1)
    notes = set()
    data = {f: rows(ws, f, start, day, notes) for f in ('analytics', 'crm', 'calendar', 'email', 'payments', 'ads')}
    missing = [f for f, r in data.items() if not r]

    posts = defaultdict(lambda: defaultdict(float))
    meta = {}
    cols = ['views', 'saves', 'shares', 'comments', 'link_clicks']
    for r in data['analytics']:
        key = (r.get('post', NONE), r.get('channel', NONE))
        meta[key] = r.get('utm_campaign') or NONE
        for c in cols:
            posts[key][c] += num(r, c, notes, 'analytics')
    post_rows = sorted(([p, ch, meta[(p, ch)]] + [v[c] for c in cols] for (p, ch), v in posts.items()),
                       key=lambda x: -x[7])

    crm_by_id = {r.get('record_id'): r for r in data['crm'] if r.get('record_id')}
    revenue = defaultdict(lambda: {'deals': 0, 'amount': 0.0, 'how': set()})
    for r in data['crm']:
        if r.get('stage', '').lower() == 'won':
            camp = r.get('utm_campaign') or NONE
            revenue[camp]['deals'] += 1
            revenue[camp]['amount'] += num(r, 'amount', notes, 'crm')
            revenue[camp]['how'].add('utm' if r.get('utm_campaign') else ('source' if r.get('source') else 'none'))
    for r in data['payments']:
        crm = crm_by_id.get(r.get('record_id'))
        if crm and crm.get('stage', '').lower() == 'won':
            continue
        camp = (crm or {}).get('utm_campaign') or NONE
        revenue[camp]['amount'] += num(r, 'amount', notes, 'payments')
        revenue[camp]['how'].add('payment joined to crm' if crm else 'payment, no crm record')
    rev_rows = sorted(([c, v['deals'], v['amount'], ', '.join(sorted(v['how']))] for c, v in revenue.items()),
                      key=lambda x: (x[0] == NONE, -x[2]))
    attributed = sum(v['amount'] for c, v in revenue.items() if c != NONE)
    unattributed = revenue[NONE]['amount'] if NONE in revenue else 0.0

    calls = defaultdict(lambda: defaultdict(int))
    for r in data['calendar']:
        camp = r.get('utm_campaign') or r.get('source') or NONE
        calls[camp][r.get('status', 'booked').lower() or 'booked'] += 1
    call_rows = sorted(([c, sum(v.values()), v['showed'], v['no-show'], v['cancelled']] for c, v in calls.items()),
                       key=lambda x: -x[1])
    booked = sum(r[1] for r in call_rows)

    email_rows = []
    for r in data['email']:
        delivered = num(r, 'delivered', notes, 'email')
        clicks = num(r, 'clicks', notes, 'email')
        email_rows.append([r.get('send', NONE), r.get('utm_campaign') or NONE, delivered, num(r, 'opens', notes, 'email'),
                           clicks, num(r, 'replies', notes, 'email'), num(r, 'unsubscribes', notes, 'email'),
                           f'{100 * clicks / delivered:.1f}%' if delivered else 'n/a'])

    spend = defaultdict(float)
    for r in data['ads']:
        spend[(r.get('channel', NONE), r.get('currency', ''))] += num(r, 'spend', notes, 'ads')
    spend_rows = [[ch, cur, v] for (ch, cur), v in sorted(spend.items())]
    total_spend = sum(spend.values())

    lines = [f'# Loop data, {start} to {day}', '',
             'Written by tools/loop_data.py from exports/. Counts and sums of export rows only. Quote these numbers;',
             'do not recompute them.', '',
             '## Window', f'- From: {start}', f'- To: {day}', f'- Exports with no rows in the window: {", ".join(missing) or "none"}', '',
             '## Posts']
    lines += md_table(['Post', 'Channel', 'Campaign', 'Views', 'Saves', 'Shares', 'Comments', 'Link clicks'], post_rows)
    lines += ['', '## Revenue by campaign']
    lines += md_table(['Campaign', 'Won deals', 'Amount', 'How it was linked'], rev_rows)
    lines += [f'- Attributed revenue: {fmt(attributed)}', f'- Unattributed revenue: {fmt(unattributed)}', '',
              '## Calls by campaign']
    lines += md_table(['Campaign or source', 'Booked', 'Showed', 'No show', 'Cancelled'], call_rows)
    lines += [f'- Calls booked in the window: {booked}', '', '## Email']
    lines += md_table(['Send', 'Campaign', 'Delivered', 'Opens', 'Clicks', 'Replies', 'Unsubscribes', 'Click rate'], email_rows)
    lines += ['', '## Spend']
    lines += md_table(['Channel', 'Currency', 'Spend'], spend_rows)
    currencies = {cur for _, cur in spend}
    if len(currencies) > 1:
        lines += ['- Total spend: n/a, mixed currencies (see the table)', '- Cost per booked call: n/a, mixed currencies', '',]
    else:
        lines += [f'- Total spend: {fmt(total_spend)}',
                  f'- Cost per booked call: {fmt(total_spend / booked) if booked and total_spend else "n/a"}', '']
    lines += [
              '## Notes'] + ([f'- {n}' for n in sorted(notes)] or ['- none']) + ['']
    out = ws / 'loop' / f'{day}-data.md'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--date')
    ap.add_argument('--days', type=int, default=7)
    ap.add_argument('--workspace', default='.')
    a = ap.parse_args(argv)
    ws = h.root(a.workspace)
    if (ws / 'owner/STOP').exists():
        print('stopped: owner/STOP present')
        return 2
    print(build(ws, h.today(a.date), a.days).relative_to(ws).as_posix())
    return 0


if __name__ == '__main__':
    sys.exit(main())
