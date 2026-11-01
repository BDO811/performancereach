---
description: Playbook. Search demand for a topic just spiked. Checks the spike is real, drafts content to meet it and checks which page should own it. Never publishes.
argument-hint: "<keyword or topic that spiked, plus what Semrush showed>"
---

# Playbook: search demand spikes

The event: $ARGUMENTS

## Before anything
1. If the file owner/STOP exists, stop. Append
   `YYYY-MM-DD HH:MM | orchestrator | stopped: owner/STOP present | -` to logs/activity.md
   and do nothing else.
2. Read owner/positioning.md, owner/approval-bar.md, owner/brand-voice.md and owner/budget-cap.md.
   They are read-only. If any still contains `[FILL IN:`, stop and tell the owner which file.

## Step 1. The orchestrator goes first
Use the orchestrator agent on this event as a playbook event
(priority: event, playbook: search-demand-spikes). It decides whether the spike is worth
acting on, writes the briefs to drafts/briefs/ and lists the hand-offs.

## Worth acting on
The orchestrator checks the event against these files:
- brand-os/signals-seo/serp-rules.md: the threshold for a demand spike worth acting on
- brand-os/signals-seo/keyword-map.md: whether the keyword is ours
- brand-os/signals-seo/tracking-setup.md: where the Semrush data came from and how fresh it is
- owner/positioning.md: whether the topic is one of the "Topics we own"

It acts only if all four are true:
1. The spike passes the threshold in serp-rules.md.
2. The keyword is in keyword-map.md, or sits clearly next to one that is.
3. The data comes from a dated export or connection named in tracking-setup.md.
4. The topic fits owner/positioning.md.

If serp-rules.md sets no threshold for a spike, do not guess one. The orchestrator adds an
item to queue/needs-your-ok.md asking the owner to set it, logs it and stops.
If the spike is not worth acting on, it logs the reason and stops.

## Steps
1. Content engine drafts. Use the content-engine agent on its brief in drafts/briefs/.
   It reads brand-os/brand-brain/ and brand-os/content/ as usual (voice-guide.md,
   tone-rules.md, messaging-bank.md, brief-templates.md, hook-bank.md, seo-checklist.md),
   writes the piece with Claude, runs the SEO pass and the voice check, and saves
   drafts/YYYY-MM-DD-<channel>-<slug>.md. A voice-check fail goes to
   queue/held-for-voice-review.md, never out.
2. Search visibility checks the target page. Use the search-visibility agent on its brief.
   It checks keyword-map.md for the page that owns the keyword, Google Search Console
   queries for close variants, and ranking-targets.md for where that page should rank.
   It writes drafts/YYYY-MM-DD-search-<slug>.md saying: refresh the owning page, or publish
   the new piece, and whether the new piece would compete with a page you already have.
3. Run the orchestrator again on both returns. It applies the owner gate below, queues what
   waits, and briefs publishing-social for anything that may ship.

## Who approves
These wait in queue/needs-your-ok.md, in the format at the top of that file:
- Anything not already on brand-os/content/content-calendar.md. A spike piece is new, so it
  waits unless owner/approval-bar.md lists it under "Auto-ships".
- Anything that names a real person, mentions a price or an offer, or needs any spend.
- Anything with an unresolved [VERIFY] mark.
- Anything else above the bar in owner/approval-bar.md.

## Log
Every agent appends one line per action to logs/activity.md:
`YYYY-MM-DD HH:MM | <agent> | <action> | <file>`
Example: `YYYY-MM-DD HH:MM | orchestrator | spike passed serp-rules.md, briefed content-engine | drafts/briefs/YYYY-MM-DD-content-engine-<slug>.md`

## What the owner sees at the end
- Worth acting on or not, and the rule it was checked against
- The draft path and its voice-check result
- Which page should carry the keyword, from Search visibility
- Any item added to queue/needs-your-ok.md, and any [VERIFY] mark

## Never
- Publish or schedule from this command. Only Publishing & social schedules, after the gate.
- Quote search volumes or positions that are not in the Semrush or Search Console data.
- Chase a topic outside owner/positioning.md, however big the spike.
