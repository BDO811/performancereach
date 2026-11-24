# CMO harness

One Claude Code project that runs PerformanceReach's whole marketing function: a CMO agent on top,
twelve directors under it, and every marketing agent under them. Each brand (PerformanceReach
itself, or one client) gets its own sealed workspace made from `template/`.

## Who is in it

    Owner  ->  CMO  ->  12 directors  ->  93 agents

| Source | Agents | Where they sit |
|---|---|---|
| The 36 agent loop from @hannesrkuhn's TikTok (research, content, publish, the loop, sales, community) | 36 | directors research, content, publish, loop, sales, community |
| The 13 Minds on athemventures.com/architecture | 49 | spread across all 12 directors, ids unchanged |
| The product Social team (`../_social-team`) | 8 departments, 8 playbooks, 27 Brand OS templates | director-social, which takes over the orchestrator role |

| Director | Loop agents | Minds |
|---|---|---|
| director-research | Trend Scout, Audience Listener, Comment Miner, Competitor Watch, Post Writer, Email Writer | Research |
| director-content | Visual Designer, Carousel Builder, Voiceover, Video Editor, Brand Check, Approval Desk | Design, Writing/Docs |
| director-publish | Scheduler, TikTok Poster, Reels Poster, Shorts Poster, X Poster, Newsletter | |
| director-loop | Post Analyst, Revenue Tracker, Call Tracker, Email Analyst, Weekly Report, Loop Feeder | Analytics |
| director-sales | Lead Scorer, Call Booker, Reminder, Follow-up, Payment Link, CRM Sync | Sales, Intake |
| director-community | Comment Replier, DM Agent, FAQ Builder, Review Asker, Lead Catcher, Escalation | Customer Success |
| director-social | the Social team's 8 departments | Social Media |
| director-paid | | Paid Social |
| director-seo | | SEO/GEO |
| director-lifecycle | | Lifecycle |
| director-finance | | Finance |
| director-legal | | Legal/Compliance |

Where a loop agent and a Mind agent could do the same job, each file has a lane line: weekly and
tactical work goes to the loop agent, deep or client facing work goes to the Mind.

## The loop

    /run-week           CMO plans  ->  research  ->  content  ->  brand check  ->  owner queue
    /process-approvals  owner ticks  ->  publish packages marked [PASTE] or [SEND]
    /daily-sweep        community  ->  sales  ->  /morning-page (what worked, who booked, what is next)
    /close-week         post, revenue, call and email results  ->  weekly report  ->  loop/next-week-inputs.md

The Social team's eight event playbooks (`/one-star-review-lands`, `/dm-lead-at-11pm` and the rest)
work as before, through director-social.

## How every agent is built

Every agent is built out. Nothing has run against a real model yet: all checks run on fictional data.

| Layer | Agents | Where | Checked by |
|---|---|---|---|
| CMO | 1 | `specs/cmo.md`: plan, returns, approvals, daily and close of week briefs, 0 to 12 scoring | `check.py plan`, `cmo_context.py`, `queue.py` |
| Directors | 12 | `specs/director-*.md` staffing rules plus `specs/_director-common.md` (split and return) | `check.py agent-briefs`, `check.py return` |
| Loop and Mind agents | 85 | job and steps from the catalogs, output format rendered from `catalog/contracts.json` | `check.py output` |
| Social team departments | 8 | the guide's own files, rewired to director-social | their own Output sections and voice check |

`catalog/contracts.json` is the single source for each agent's output: path, front matter, sections,
table columns and limits, and rules (sources, UTM tags, no personal data, [PASTE]/[SEND]/[RENDER]
markers, loop data citations, real queue ids). The build writes it into each agent's "Output format"
section and into `tools/contracts.json`, so what an agent is told and what the check enforces cannot
drift apart.

`tools/loop_data.py` turns the week's exports (formats in `exports/README.md`) into
`loop/YYYY-MM-DD-data.md`: posts, revenue by campaign, calls, email, spend and cost per call. Loop,
analytics, paid and finance agents quote it and never do arithmetic.

Every command runs each CMO brief the same way (CLAUDE.md, "Running a CMO brief"): director splits,
check, each agent runs and its output is checked, director reviews, return is checked, CMO routes it.
A failed check goes back to the agent that wrote the file, twice at most, then to the owner.

| Test file | Covers |
|---|---|
| `tests/test_cmo_harness.py` | The build: counts, front matter, owner lock, queues, page data |
| `tests/test_cmo.py` | Context facts, the plan check (14 broken plans), approvals |
| `tests/test_director_research.py` | Agent brief and return checks on the Research reference split |
| `tests/test_agents.py` | All 85 contracts: a valid sample passes and 545 broken versions fail; every agent file carries its contract; every director staffs only its team and covers all of it; loop data numbers |

## What is here

| Path | What it is |
|---|---|
| `catalog/growth-loop.json` | The 36 loop agents: job, inputs, steps, output, lane, limits |
| `catalog/agency-minds.json` | Snapshot of the `MINDS` list in `../architecture/index.html` |
| `catalog/contracts.json` | The output contract for each of the 85 loop and Mind agents |
| `extras/` | Files written for this harness: CLAUDE.md, the CMO commands, `owner/targets.md`, `owner/sales-rules.md`, the ElevenLabs section of `owner/brand-voice.md`, `brand-os/market/`, settings |
| `build.py` | Builds `template/` from the catalogs, `extras/` and `../_social-team/template` |
| `specs/` | The CMO and the 12 directors, written by hand. Each replaces the generated file |
| `extras/tools/` | Scripts copied into every workspace: `cmo_context.py`, `loop_data.py`, `check.py`, `contracts_check.py`, `queue.py`, `harness.py` |
| `fixtures/` | Fictional Northwind Coffee workspace and reference outputs, used by the tests |
| `template/` | The built project. Do not edit it by hand: change a source and rebuild |
| `new_workspace.py` | Copies the template into a new folder for one brand |
| `tests/` | Checks the build. No model, no network |

Jekyll skips folders that start with an underscore, so none of this is served. The repo is public,
so real brand data never goes here. It lives in each workspace.

## Rules carried over from the Social team

Owner files are read only and unfilled prompts block a run. Only the owner ticks a queue box.
`owner/STOP` halts every agent. Agents have file tools (plus web search for research roles) and no
shell, so nothing they have can publish, send or spend. Every agent runs on Sonnet. Posts are
packaged as [PASTE], emails as [SEND], audio and video as [RENDER], CRM updates as [IMPORT].

## Use it

```bash
python3 -I _cmo-harness/build.py
python3 -I _cmo-harness/tests/test_cmo_harness.py
python3 -I _cmo-harness/tests/test_cmo.py
python3 -I _cmo-harness/tests/test_director_research.py
python3 -I _cmo-harness/tests/test_agents.py
python3 -I _cmo-harness/new_workspace.py ~/Downloads/Serasona-Growth-Harness/cmo/performancereach
```

Then fill the six files in `owner/`, drop this week's exports into `exports/`, run `claude` in the
workspace and type `/run-week`.

When the architecture page's catalog changes, refresh the snapshot and rebuild:

```bash
node -e 'const s=require("fs").readFileSync("architecture/index.html","utf8");const a=s.indexOf("const MINDS = [");const b=s.indexOf("  const STATUS");const M=eval(s.slice(a+14,b).trim().replace(/;$/,""));require("fs").writeFileSync("_cmo-harness/catalog/agency-minds.json",JSON.stringify(M,null,1))'
python3 -I _cmo-harness/build.py
```
