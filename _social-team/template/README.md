# AI Social Media Team

An AI social media team that runs inside Claude Code. An orchestrator agent reads your signals,
decides what matters this week and briefs eight department agents. They draft, design, schedule,
answer and report in your voice. You set four things (voice, budget, approval bar, positioning) and
approve anything above your approval bar. Routine content ships end to end.

## What is in the folder

    ai-social-media-team/
    ├── CLAUDE.md                  the rules every agent follows
    ├── README.md                  this file
    ├── .claude/
    │   ├── agents/                orchestrator.md + the 8 department agents
    │   └── commands/              the 8 playbooks, run as slash commands
    ├── brand-os/                  README.md + 8 folders, 27 brand templates
    ├── owner/                     brand-voice.md, budget-cap.md, approval-bar.md, positioning.md
    ├── queue/                     needs-your-ok.md, held-for-voice-review.md
    ├── drafts/                    department output lands here (briefs in drafts/briefs/)
    └── logs/                      activity.md

## Quick start
1. Open this folder in Claude Code. It reads `CLAUDE.md` automatically.
2. Fill the four files in `owner/`. Replace every `[FILL IN: ...]` prompt.
   Agents stop if any prompt is left.
3. Fill the templates in `brand-os/`, starting with `brand-os/brand-brain/`.
4. Drop this week's exports from your signal tools into `brand-os/signals-seo/`.
5. In Claude Code, type: "Use the orchestrator agent to run this week's loop."
6. Open `queue/needs-your-ok.md`, tick what you approve, then tell the orchestrator:
   "Process my approvals in queue/needs-your-ok.md."

## Stop everything
Create an empty file called `owner/STOP`. Every agent checks for it before acting and stops.
Delete it to resume.

## Read more in the guide
- How the system works: the 7 zones
- CLAUDE.md: the rules every agent follows
- The Orchestrator agent
- Owner inputs: voice, budget, approval bar, positioning
- Approvals, queues and the kill switch
- The weekly loop
