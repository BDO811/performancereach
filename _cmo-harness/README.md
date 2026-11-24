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

## What is here

| Path | What it is |
|---|---|
| `catalog/growth-loop.json` | The 36 loop agents: job, inputs, steps, output, lane, limits |
| `catalog/agency-minds.json` | Snapshot of the `MINDS` list in `../architecture/index.html` |
| `extras/` | Files written for this harness: CLAUDE.md, the CMO commands, `owner/targets.md`, `owner/sales-rules.md`, the ElevenLabs section of `owner/brand-voice.md`, `brand-os/market/`, settings |
| `build.py` | Builds `template/` from the catalogs, `extras/` and `../_social-team/template` |
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
python3 -I _cmo-harness/new_workspace.py ~/Downloads/Serasona-Growth-Harness/cmo/performancereach
```

Then fill the six files in `owner/`, drop this week's exports into `exports/`, run `claude` in the
workspace and type `/run-week`.

When the architecture page's catalog changes, refresh the snapshot and rebuild:

```bash
node -e 'const s=require("fs").readFileSync("architecture/index.html","utf8");const a=s.indexOf("const MINDS = [");const b=s.indexOf("  const STATUS");const M=eval(s.slice(a+14,b).trim().replace(/;$/,""));require("fs").writeFileSync("_cmo-harness/catalog/agency-minds.json",JSON.stringify(M,null,1))'
python3 -I _cmo-harness/build.py
```
