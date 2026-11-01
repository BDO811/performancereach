# Social team

Social media management for Growth Studio at athemventures.com/admin, under **Social team** in the sidebar. Every product workspace gets its own team, files and queue.

Built from the guide "AI Native Social Media Agent Team" by Megha Sharma of OneGTMLab: https://dandy-bug-77c.notion.site/AI-Native-Social-Media-Agent-Team-402a1f98521280859feede9319ce1aa0

## What is here

| Path | What it is |
|---|---|
| `template/` | The guide's project: `CLAUDE.md`, 9 agents, 8 playbooks, 27 Brand OS templates, 4 owner files, 2 queues, the log |
| `adapt_template.py` | Applies Athem's standing rules to the template (no email, no live posting, Sonnet only, writing rules) |
| `runtime/social_team.py` | Runs the team on the Mac worker and mirrors its files to Firestore |
| `install.py` | Copies the runtime and template into the worker folder and seeds one workspace per product |
| `tests/` | Unit tests. They run with no model and no network |
| `preview.html` | The view with fictional data, for local checks |
| `../admin/social.js` | The dashboard view |

Jekyll skips folders that start with an underscore, so this folder is not served by the site. The repo itself is public, so **real brand data never goes here**. It lives in Firestore (owner only) and in the Mac workspace.

## How it runs

```
Dashboard  ->  growthCommands           ->  Mac worker  ->  claude -p in the workspace
Dashboard  ->  growthSocialInputs       ->  owner files, Brand OS, kill switch, tool plan
Dashboard  <-  growthSocial             <-  queues, drafts, briefs, log, run status (worker only)
```

Workspaces: `/Users/amitmehta/Downloads/Serasona-Growth-Harness/social-team/workspaces/<product>/`. You can also run `claude` in one directly, and the guide's prompts work as written.

## What is enforced in code

- **Only the owner ticks a box.** `tick()` runs only for a dashboard click. Agents never decide a queue item.
- **Kill switch.** The dashboard flag becomes `owner/STOP`. A running agent is ended within seconds, and no new step starts. It covers the social team only, not the rest of Growth Studio.
- **Owner files are read only.** Permission rules deny the edit, and the worker restores the file if one changes anyway.
- **No shell, no MCP.** Agents get file tools and web search. They cannot publish, send or spend, because nothing they have can do it.
- **Sonnet only.** A run that reports any other model fails.
- **Spend limits.** $2 per step and $8 per run.
- **Unfilled files block the run** before any model is called: the 4 owner files plus voice-guide, tone-rules and content-calendar. A live test showed a voice check passes everything when the rule file is empty.

## Not connected yet

No tool from the guide's board is connected, so the team runs on weekly exports pasted into the dashboard. Publishing & social writes paste-ready posts marked `[PASTE]`. To go live through Growth Studio's existing channel adapters, send a draft to Content studio, which requires approval of the exact revision.

The existing `social-*` agents in `Claude-Outputs/.claude/agents` serve PerformanceReach's sealed clients through the Chief of Staff. They are separate and unchanged.

## Update it

```bash
python3 -I _social-team/tests/test_social_team.py
python3 -I _social-team/install.py
launchctl kickstart -k gui/$(id -u)/com.athem.growth-studio.worker
```

`install.py` replaces the template in the worker folder. Existing workspaces and dashboard edits stay as they are.
