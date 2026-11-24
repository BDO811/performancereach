"""Build the CMO harness template from the catalogs. Safe to run again: it rebuilds template/.

Sources:
  catalog/growth-loop.json     the 36 agent marketing loop (research, content, publish, loop, sales, community)
  catalog/agency-minds.json    the 13 Minds and 49 agents shown at athemventures.com/architecture
  ../_social-team/template     the 8 social departments, 8 playbooks, 27 Brand OS templates and 4 owner files

Run:  python3 -I _cmo-harness/build.py
"""
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
T = HERE / 'template'
SOCIAL = HERE.parent / '_social-team' / 'template'
LOOP = json.loads((HERE / 'catalog/growth-loop.json').read_text())
MINDS = {m['id']: m for m in json.loads((HERE / 'catalog/agency-minds.json').read_text())}

WEB_TOOLS = 'Read, Write, Edit, Grep, Glob, WebSearch, WebFetch'
FILE_TOOLS = 'Read, Write, Edit, Grep, Glob'
SOCIAL_DEPTS = ['search-visibility', 'market-radar', 'content-engine', 'creative-studio',
                'publishing-social', 'reviews-reputation', 'leads-conversations', 'results-roi']

# Who sits under which director. Loop departments come from growth-loop.json, Minds from the site.
DIRECTORS = [
    dict(id='director-research', name='Research', loop='research', minds=['research'],
         job='Finds what the market and the audience want this week, and writes the first drafts of posts and emails from it.'),
    dict(id='director-content', name='Content and Creative', loop='content', minds=['design', 'writing-docs'],
         job='Turns drafts into finished visuals, carousels, voiceover, video, ads, pages and long form, checks every piece against the brand and packs it for approval.'),
    dict(id='director-publish', name='Publish', loop='publish', minds=[],
         job='Puts approved work on the calendar and prepares it for every channel.'),
    dict(id='director-loop', name='Loop and Analytics', loop='loop', minds=['analytics'],
         job='Measures what every post, email and dollar earned, writes the morning page and the weekly report, and feeds the results into next week.'),
    dict(id='director-sales', name='Sales and Intake', loop='sales', minds=['sales', 'intake'],
         job='Scores leads, books calls, follows up, prepares payment requests, runs outbound and takes new clients from discovery to onboarding.'),
    dict(id='director-community', name='Community and Customer Success', loop='community', minds=['success'],
         job='Answers comments and DMs, catches leads, escalates risk, asks for reviews and keeps clients supported and renewing.'),
    dict(id='director-social', name='Social', loop=None, minds=['social'], social=True,
         job='Runs the product Social team (eight departments and eight event playbooks) and the agency social agents.'),
    dict(id='director-paid', name='Paid Social', loop=None, minds=['paid-social'],
         job='Plans and watches paid campaigns on Meta and TikTok. Recommends every spend change, never executes one.'),
    dict(id='director-seo', name='SEO and GEO', loop=None, minds=['seo-geo'],
         job='Owns search and AI answer visibility: keywords, briefs, technical audits and citation tests.'),
    dict(id='director-lifecycle', name='Lifecycle', loop=None, minds=['lifecycle'],
         job='Owns email and messaging segments, automated flows and deliverability.'),
    dict(id='director-finance', name='Finance', loop=None, minds=['finance'],
         job='Keeps the books, prepares invoices, reports marketing spend and return, and forecasts.'),
    dict(id='director-legal', name='Legal and Compliance', loop=None, minds=['legal'],
         job='Checks contracts, claims, policies and trademarks before anything is signed or goes live.'),
]

LOOP_BY_ID = {d['id']: d for d in LOOP['departments']}
CONTRACTS = json.loads((HERE / 'catalog/contracts.json').read_text())
for _m in MINDS.values():
    for _a in _m['agents']:
        _c = CONTRACTS['agents'].get(_a['id'])
        if _c is not None and 'output' not in _c and 'outputs' not in _c:
            _c['output'] = f"drafts/{_m['id']}/{{date}}-{_a['id']}-{{slug}}.md"

sys.path.insert(0, str(HERE / 'extras/tools'))
import contracts_check  # noqa: E402


def output_format(agent_id):
    c = CONTRACTS['agents'][agent_id]
    return ('## Output format\n' + contracts_check.output_template(agent_id, c, CONTRACTS['rules_text']) +
            '\n\nThe runner checks your file with `python3 -I tools/check.py output --brief <your B brief id>`.'
            '\nIf it prints problems, fix those and nothing else.')


def uses_loop_data(agent_id):
    c = CONTRACTS['agents'][agent_id]
    return any('loop_data' in s.get('rules', []) for s in (c.get('outputs') or [c]))

MIND_NEVER = {
    'paid-social': ['Change a budget, bid, audience or campaign status. You recommend. The owner decides.'],
    'finance': ['Move money, pay a bill, send an invoice or change a bank detail. Drafts only.',
                'Type a card, bank or account number into any file.'],
    'legal': ['Sign, accept or send anything. Every opinion goes to the owner, who decides when a lawyer reviews it.'],
    'sales': ['Send a message. Outreach is drafted and queued.'],
    'intake': ['Quote a price or send a contract. Pricing and contracts always wait for the owner.'],
    'success': ['Promise a refund, credit or fix date.'],
    'lifecycle': ['Send or schedule a send. Flows are built as drafts for the owner.'],
    'social': ['Post anything. Posting goes through Publish and the owner.'],
}
WEB_MINDS = {'research', 'seo-geo', 'paid-social', 'sales', 'legal', 'social', 'design', 'writing-docs'}


def fm(name, description, tools):
    return f'---\nname: {name}\ndescription: {description}\ntools: {tools}\nmodel: sonnet\n---\n\n'


def bullets(items):
    return '\n'.join(f'- {i}' for i in items)


def numbered(items, start=1):
    return '\n'.join(f'{n}. {i}' for n, i in enumerate(items, start))


COMMON_NEVER = ['Edit, rename or delete anything in owner/.',
                'Brief another agent or department. Hand offs go through your director.',
                'Publish, send, schedule live, spend or sign. Those wait for the owner.']


def loop_read(agent_id):
    return ('- loop/YYYY-MM-DD-data.md, the newest one: the week\'s numbers from tools/loop_data.py. Quote them.\n'
            if uses_loop_data(agent_id) else '')


def loop_agent(a, dept, director):
    tools = WEB_TOOLS if a.get('web') else FILE_TOOLS
    desc = (f"{dept['name']} department, {a['name']}. {a['role']} Reports to {director['id']}. "
            f"Use when a brief from {director['id']} names this agent.")
    lane = f"\n\n## Your lane\n{a['lane']}" if a.get('lane') else ''
    return fm(a['id'], desc, tools) + f"""You are {a['name']}, in the {dept['name']} department of the CMO harness. You report to
{director['id']}, who reports to the CMO. {a['role']}{lane}

## Read before every job
- The brief from your director in drafts/briefs/
{loop_read(a['id'])}{bullets(a['reads'])}

## Steps
1. Stop check. If owner/STOP exists, do nothing and return "stopped".
{numbered(a['steps'], 2)}
{len(a['steps']) + 2}. Write your output in the format below, then log one line in logs/activity.md for every file you write.

{output_format(a['id'])}

## Return to your director
The file path, what you did, your check results, and anything you could not finish or any export
that was missing.

## Never
{bullets(COMMON_NEVER + a.get('never', []))}
"""


def mind_agent(a, mind, director):
    tools = WEB_TOOLS if mind['id'] in WEB_MINDS else FILE_TOOLS
    desc = (f"{mind['name']} Mind, {a['name']}. {a['role']} Reports to {director['id']}. "
            f"Use when a brief from {director['id']} names this agent.")
    detail = f"\n\n{a['detail']}" if a.get('detail') else ''
    needs = a.get('needs') or []
    needs_block = (f"\n\n## What this role needs to run fully\n{bullets(needs)}\n\n"
                   "If a need is not in place in this workspace, do the part you can from files, exports and public\n"
                   "sources, mark the rest [NEEDS: <the need>] and say so in your return. Never pretend a connection ran."
                   if needs else '')
    newer = ("\n\nThis role is new in the harness. Keep every output a draft for your director and the owner."
             if a.get('status') == 'not' else '')
    folder = mind['id']
    return fm(a['id'], desc, tools) + f"""You are {a['name']}, in the {mind['name']} Mind of the CMO harness. You report to
{director['id']}, who reports to the CMO. This is the same role as `{a['id']}` on the agency
architecture page.

## Your job
{a['role']}{detail}{needs_block}{newer}

## Read before every job
- The brief from your director in drafts/briefs/
- owner/positioning.md and owner/brand-voice.md
- Any brand-os/ or exports/ file the brief names
{loop_read(a['id'])}
## Steps
1. Stop check. If owner/STOP exists, do nothing and return "stopped".
2. Read the brief. If it asks for work outside your job, return it to your director unchanged.
3. Do the job. Every fact, number and quote has a source. Anything you could not source is [VERIFY].
4. Write your output in the format below.
5. Anything that would spend, go live, send, sign or name a real person goes to queue/needs-your-ok.md
   in the format at the top of that file.
6. Log one line in logs/activity.md for every file you write.

{output_format(a['id'])}

## Return to your director
The file path, what you did, what is waiting for the owner, and what you could not finish.

## Never
{bullets(COMMON_NEVER + MIND_NEVER.get(mind['id'], []))}
"""


def team_list(d):
    rows = []
    if d.get('loop'):
        dept = LOOP_BY_ID[d['loop']]
        rows += [f"| `{a['id']}` | {a['name']} | {a['role']} |" for a in dept['agents']]
    for mid in d['minds']:
        m = MINDS[mid]
        rows += [f"| `{a['id']}` | {a['name']} ({m['name']} Mind) | {a['role']} |" for a in m['agents']]
    if d.get('social'):
        for s in SOCIAL_DEPTS:
            rows.append(f"| `{s}` | Social team department | See .claude/agents/{s}.md |")
    return '| Agent | Name | Job |\n|---|---|---|\n' + '\n'.join(rows)


def director_common(d):
    common = (HERE / 'specs/_director-common.md').read_text().rstrip()
    return common.replace('{{DIRECTOR}}', d['id']).replace('{{DEPT}}', d['id'].replace('director-', ''))


def director(d):
    desc = (f"Director of {d['name']}. {d['job']} Reports to the CMO. Use after the CMO writes a brief for "
            f"{d['name']}, and when its agents return work.")
    social = ''
    if d.get('social'):
        social = """

## The product Social team
You also hold the role the Social team's orchestrator had. Its eight department agents, eight event
playbooks (the slash commands such as /one-star-review-lands) and 27 Brand OS templates live in this
harness unchanged. Their instructions say "the Social director" or "director-social": that is you. Follow the scoring and
briefing rules in the Social team section of CLAUDE.md for their work."""
    job = d['job'][0].lower() + d['job'][1:]
    return fm(d['id'], desc, FILE_TOOLS) + f"""You are the {d['name']} director. You report to the CMO. Your department {job}

## Your team
{team_list(d)}{social}

## How to staff a brief
Brief the agents on your team whose job matches what the CMO brief asks for, using each agent's own
output pattern from its file. Agents that gather or analyse run first; agents that write, build or
package from their work run after them and depend on them. Anything public facing must pass
content-brand-check before it reaches the owner: ask the CMO to route it there in your return.

{director_common(d)}
"""


def directors_table():
    rows = '\n'.join(f"| `{d['id']}` | {d['name']} | {d['job']} |" for d in DIRECTORS)
    return '| Director | Department | Job |\n|---|---|---|\n' + rows


def cmo():
    desc = ('The CMO. Owns the marketing plan and the targets, runs the weekly loop and the daily sweep, briefs '
            'the twelve directors, settles overlaps between them, keeps the owner queue honest and writes the '
            'owner\'s morning page. Use at the start of every session, after directors return work, and after the '
            'owner ticks approvals. Never drafts, publishes, sends or spends.')
    rows = '\n'.join(f"| `{d['id']}` | {d['name']} | {d['job']} |" for d in DIRECTORS)
    return fm('cmo', desc, FILE_TOOLS) + f"""You are the CMO of this workspace. You report to the owner, who decides the brand and the
budget. You decide what the team works on, in what order, and what the owner needs to see. You never
draft content, publish, send or spend.

## Your directors
| Director | Department | Job |
|---|---|---|
{rows}

## Read at the start of every run
- owner/STOP. If it exists, stop and say so.
- All six owner files: targets, positioning, brand-voice, approval-bar, budget-cap, sales-rules.
  If any still has a [FILL IN: prompt, stop and tell the owner which file.
- loop/next-week-inputs.md, the newest reports/weekly/ and reports/morning/ files.
- The open items in queue/needs-your-ok.md and queue/held-for-voice-review.md.
- The last 30 lines of logs/activity.md.

## The weekly loop (run with /run-week)
1. Plan. Write reports/plans/YYYY-Www.md: this week's goal from owner/targets.md, three to five
   priorities, what loop/next-week-inputs.md says to double down on, drop and test, and the spend plan
   inside owner/budget-cap.md (every spend still waits for the owner).
2. Research. Brief director-research (trends, audience voice, comments, competitors, then posts and
   emails) and, when the plan needs it, director-seo.
3. Content. Brief director-content to design, voice, edit and brand check the drafts, then pack the
   week for approval. Paid creative goes through director-paid with director-content.
4. Owner approval. Tell the owner the week is ready in queue/needs-your-ok.md. Nothing moves until
   the owner ticks, except what owner/approval-bar.md lets auto ship.
5. Publish. After the owner ticks, brief director-publish (and director-social for the Social team's
   calendar).
6. Every day. Run the daily sweep: director-community, then director-sales, then the morning page.
7. Close the week. Brief director-loop: post, revenue, call and email results, the weekly report,
   and loop/next-week-inputs.md. That file opens next week's plan.

## The daily sweep (run with /daily-sweep and /morning-page)
- director-community: comments, DMs, escalations, caught leads.
- director-sales: score new leads, booking replies, reminders, follow ups, CRM updates.
- director-loop: loop-weekly-report writes reports/morning/YYYY-MM-DD.md. One page: what worked, who
  booked a call, what is going out next, what is waiting for the owner.

## Settling overlaps
When two agents could do a job, the lane lines in their files decide. Weekly and tactical work goes to
the loop departments. Deep, strategic or client facing work goes to the Minds. Finance and Legal are
called by any plan that spends money, signs anything, makes a regulated claim or uses a trademark.

## Briefs
Write one brief per director per job to drafts/briefs/cmo/C-YYYYMMDD-NN-<director>.md: goal, inputs,
outputs, deadline, checks, and what needs the owner. List the briefs in your return in run order.

## Return to the owner
What shipped, what waits for you and where, what was held and why, what is blocked and which export
or connection would unblock it.

## Never
- Draft, design, publish, schedule live, send, spend or sign.
- Edit owner/, tick a box or delete a log line.
- Pass work to an agent directly. Directors brief their own agents.
"""


def adapt_social(text):
    """Point the Social team's files at director-social and strip the shell tool."""
    text = text.replace('the orchestrator agent', 'the director-social agent')
    text = text.replace('Use the orchestrator agent', 'Use the director-social agent')
    text = re.sub(r'\bThe [Oo]rchestrator\b', 'The Social director', text)
    text = re.sub(r'\bthe [Oo]rchestrator\b', 'the Social director', text)
    text = re.sub(r'\borchestrator\b', 'director-social', text)
    text = re.sub(r'\bOrchestrator\b', 'director-social', text)
    text = re.sub(r'^(tools:.*?)(, Bash)', r'\1', text, flags=re.M)
    if not re.search(r'^model:', text, re.M):
        text = re.sub(r'^(tools:.*)$', r'\1\nmodel: sonnet', text, count=1, flags=re.M)
    return text


def write(path, text):
    p = T / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def main():
    if T.exists():
        shutil.rmtree(T)
    T.mkdir()

    # Brand OS and owner files come from the Social team, so its agents work unchanged.
    shutil.copytree(SOCIAL / 'brand-os', T / 'brand-os')
    shutil.copytree(SOCIAL / 'owner', T / 'owner')
    for f in (T / 'owner').glob('STOP'):
        f.unlink()
    for name in ('needs-your-ok', 'held-for-voice-review'):
        s = (SOCIAL / 'queue' / f'{name}.md').read_text()
        s = re.sub(r'(## Open\n).*?(\n## Done)', r'\1\2', s, flags=re.S)
        write(f'queue/{name}.md', adapt_social(s).replace('director-social', 'CMO'))
    log = (SOCIAL / 'logs/activity.md').read_text()
    write('logs/activity.md', ''.join(l for l in log.splitlines(True) if 'EXAMPLE' not in l))

    for extra in sorted((HERE / 'extras').rglob('*')):
        if extra.is_file() and '__pycache__' not in extra.parts:
            rel = extra.relative_to(HERE / 'extras')
            target = T / rel
            if target.exists() and rel.parts[0] == 'owner':
                target.write_text(target.read_text().rstrip() + '\n\n' + extra.read_text())
            else:
                write(str(rel), extra.read_text())

    agents = T / '.claude/agents'
    write('.claude/agents/cmo.md', cmo())
    for d in DIRECTORS:
        write(f".claude/agents/{d['id']}.md", director(d))
        if d.get('loop'):
            dept = LOOP_BY_ID[d['loop']]
            for a in dept['agents']:
                write(f".claude/agents/{a['id']}.md", loop_agent(a, dept, d))
        for mid in d['minds']:
            for a in MINDS[mid]['agents']:
                write(f".claude/agents/{a['id']}.md", mind_agent(a, MINDS[mid], d))
    reports_to = ('In the CMO harness you sit in the Social department and report to director-social (the Social\n'
                  'director), who reports to the CMO.\n\n')
    for s in SOCIAL_DEPTS:
        head, sep, body = adapt_social((SOCIAL / f'.claude/agents/{s}.md').read_text()).partition('---\n\n')
        head, sep2, body2 = (head + sep + body).partition('\n---\n')
        write(f'.claude/agents/{s}.md', head + sep2 + '\n' + reports_to + body2.lstrip('\n'))
    # The Social orchestrator's own rules become a reference for director-social.
    write('docs/social-orchestrator-rules.md',
          adapt_social((SOCIAL / '.claude/agents/orchestrator.md').read_text()).split('---', 2)[2].lstrip())
    for f in (SOCIAL / '.claude/commands').glob('*.md'):
        write(f'.claude/commands/{f.name}', adapt_social(f.read_text()))

    for folder in ('drafts/briefs/cmo', 'research', 'loop/history', 'reports/morning', 'reports/weekly',
                   'reports/plans', 'exports/analytics', 'exports/crm', 'exports/calendar', 'exports/comments',
                   'exports/dms', 'exports/email', 'exports/payments', 'exports/ads', 'exports/seo',
                   'exports/finance'):
        (T / folder).mkdir(parents=True, exist_ok=True)
        (T / folder / '.gitkeep').write_text('')

    # Agents we have built out by hand replace their generated file.
    by_id = {d['id']: d for d in DIRECTORS}
    for spec in sorted((HERE / 'specs').glob('*.md')):
        if spec.name.startswith('_'):
            continue
        text = spec.read_text().replace('{{DIRECTORS_TABLE}}', directors_table())
        d = by_id.get(spec.stem)
        if d:
            text = text.replace('{{TEAM}}', team_list(d)).replace('{{COMMON}}', director_common(d))
        write(f'.claude/agents/{spec.name}', text)

    write('tools/contracts.json', json.dumps(CONTRACTS, indent=1) + '\n')
    write_page_data()
    count = len(list(agents.glob('*.md')))
    print(f'built {T} with {count} agents')


def write_page_data():
    """The architecture page renders its CMO section from this file, so the page and the harness agree."""
    social_names = {'search-visibility': 'Search visibility', 'market-radar': 'Market radar',
                    'content-engine': 'Content engine', 'creative-studio': 'Creative studio',
                    'publishing-social': 'Publishing & social', 'reviews-reputation': 'Reviews & reputation',
                    'leads-conversations': 'Leads & conversations', 'results-roi': 'Results & ROI'}
    directors = []
    for d in DIRECTORS:
        agents = []
        if d.get('loop'):
            agents += [dict(id=a['id'], name=a['name'], source='loop', role=a['role'])
                       for a in LOOP_BY_ID[d['loop']]['agents']]
        for mid in d['minds']:
            agents += [dict(id=a['id'], name=a['name'], source='mind', mind=MINDS[mid]['name'], role=a['role'])
                       for a in MINDS[mid]['agents']]
        if d.get('social'):
            agents += [dict(id=s, name=social_names[s], source='social', role='Social team department.')
                       for s in SOCIAL_DEPTS]
        directors.append(dict(id=d['id'], name=d['name'], job=d['job'], agents=agents))
    data = dict(
        source_video='https://www.tiktok.com/@hannesrkuhn/video/7709003343489682721',
        counts=dict(directors=len(directors), agents=sum(len(d['agents']) for d in directors),
                    loop=sum(len(d['agents']) for d in LOOP['departments']),
                    minds=sum(len(m['agents']) for m in MINDS.values()), social=len(SOCIAL_DEPTS)),
        loop=[dict(id=d['id'], name=d['name'], director=d['director'],
                   agents=[a['name'] for a in d['agents']]) for d in LOOP['departments']],
        directors=directors,
    )
    (HERE.parent / 'architecture/cmo-harness.json').write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
