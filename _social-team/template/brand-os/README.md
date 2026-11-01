# Brand OS

Brand OS is the folder every agent reads before it works. It holds what the team needs to know about your brand:
how you sound, what you may claim, what to watch, how to reply and what counts as a result.
Change a file here and every agent works differently on its next run. You never edit a prompt.

## The rules of this folder
1. **Agents read, you write.** Agents never change a rule in this folder. The only edits an agent may make are new rows
   in tables marked "Agents may add rows", and every such row starts with the status `idea` or `proposed` until you approve it.
2. **owner/ wins.** If anything here disagrees with owner/brand-voice.md, owner/budget-cap.md, owner/approval-bar.md
   or owner/positioning.md, the owner file wins. The agent that spots the conflict writes it to queue/needs-your-ok.md.
3. **[FILL IN] means unknown.** An agent that needs a value still marked [FILL IN] does not guess. It stops and asks
   in queue/needs-your-ok.md.
4. **Exports land in the folder that reads them.** Weekly exports from your tools go in brand-os/signals-seo/ unless
   tracking-setup.md says otherwise, named <tool>-<what>-YYYY-MM-DD.csv.
5. **No keys, no passwords.** Nothing secret goes in this folder.

## The folders
brand-os/
├── README.md              this file
├── brand-brain/           voice-guide.md, positioning.md, messaging-bank.md, tone-rules.md
├── signals-seo/           keyword-map.md, serp-rules.md, ranking-targets.md, tracking-setup.md
├── content/               content-calendar.md, brief-templates.md, hook-bank.md, seo-checklist.md
├── creative/              visual-specs.md, asset-library.md, video-scripts.md
├── social/                channel-playbooks.md, posting-schedule.md, hashtag-rules.md
├── reputation/            gbp-response.md, review-flow.md, mentions-rules.md
├── conversation/          faq-library.md, routing-rules.md, auto-reply-scripts.md
└── reporting/             kpi-model.md, margin-rules.md, attribution.md

## Who reads what
| Agent | Reads |
|---|---|
| orchestrator | every folder |
| search-visibility | signals-seo/ |
| market-radar | signals-seo/, brand-brain/ |
| content-engine | content/, brand-brain/ |
| creative-studio | creative/, brand-brain/ |
| publishing-social | social/ |
| reviews-reputation | reputation/, brand-brain/ |
| leads-conversations | conversation/ |
| results-roi | reporting/ |

## Fill these five first
1. brand-brain/voice-guide.md
2. brand-brain/tone-rules.md
3. brand-brain/positioning.md
4. brand-brain/messaging-bank.md
5. content/content-calendar.md (one row with the status `ready`)
In content/brief-templates.md, fill the length line for the one channel you start with.
That is enough for a first draft. Fill the other folders as you switch on each department.

## Keeping it current
- Once a week: drop the new exports in, read queue/needs-your-ok.md, approve or delete rows marked `idea` or `proposed`.
- Once a month: re-read tone-rules.md and messaging-bank.md. Retire any claim that is no longer true.
- Whenever you change your mind: edit the file. The next run uses it.
- Last reviewed: [FILL IN: date you last read this whole folder]
