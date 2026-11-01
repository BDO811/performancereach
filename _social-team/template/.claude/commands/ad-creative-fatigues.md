---
description: Playbook. An ad's creative is wearing out. Confirms the fatigue, rebuilds fresh creative in Canva and prepares the rotation in Metricool. The swap always waits for the owner.
argument-hint: "<which ad, which channel, and what the numbers show>"
---

# Playbook: ad creative fatigues

The event: $ARGUMENTS

## Before anything
1. If the file owner/STOP exists, stop. Append
   `YYYY-MM-DD HH:MM | orchestrator | stopped: owner/STOP present | -` to logs/activity.md
   and do nothing else.
2. Read owner/budget-cap.md, owner/approval-bar.md, owner/brand-voice.md and owner/positioning.md.
   They are read-only. If any still contains `[FILL IN:`, stop and tell the owner which file.

## Step 1. The orchestrator goes first
Use the orchestrator agent on this event as a playbook event
(priority: event, playbook: ad-creative-fatigues). It decides whether this is really
fatigue, then briefs Creative studio and Publishing & social.

## Worth acting on
It acts only if both are true:
1. The ad passes the fatigue rule in brand-os/reporting/kpi-model.md.
2. Nothing else changed on the ad in the same period (budget, audience, offer or landing
   page), according to logs/activity.md. If something did, the numbers are not about the
   creative.
If kpi-model.md sets no fatigue rule, do not guess one. The orchestrator adds an item to
queue/needs-your-ok.md asking the owner to set it, logs it and stops.
If it is not fatigue, it logs the reason and stops.

## Steps
1. Creative studio rebuilds the creative. Use the creative-studio agent on its brief. It reads
   brand-os/creative/visual-specs.md, asset-library.md and video-scripts.md (for a video ad),
   plus brand-os/brand-brain/voice-guide.md and tone-rules.md. It keeps the offer and the
   message, and builds the number of new versions the brief asks for in Canva, changing one
   thing per version (image, headline or layout) so Results & ROI can tell which one worked.
   It runs the spec check and saves drafts/YYYY-MM-DD-<channel>-<slug>-creative.md.
2. Run the orchestrator again on the return. It briefs Publishing & social with the versions.
3. Publishing & social prepares the rotation. Use the publishing-social agent on its brief.
   It writes which version replaces which, on which placement, from when, to
   drafts/YYYY-MM-DD-schedule-<slug>.md, and sets the rotation up in Metricool as a draft
   only. Until Metricool is connected, the plan is written ready to paste, marked [PASTE].
4. Run the orchestrator again. It queues the swap for the owner.

## Who approves
A running ad is paid spend, so the swap always waits for the owner. No exceptions.
- One item in queue/needs-your-ok.md, in the format at the top of that file, with the new
  versions and the rotation plan in the File line.
- If the swap would change the budget, the Spend line says so. If it would pass
  owner/budget-cap.md, the title says OVER CAP.
- The item also says if a version shows a real person, changes a claim or mentions a price
  or an offer.
Once the owner ticks Approve, the orchestrator briefs Publishing & social to switch the
rotation on in Metricool exactly as approved.

## Log
Every agent appends one line per action to logs/activity.md:
`YYYY-MM-DD HH:MM | <agent> | <action> | <file>`
Example: `YYYY-MM-DD HH:MM | creative-studio | rebuilt ad versions in Canva, spec check pass | drafts/YYYY-MM-DD-<channel>-<slug>-creative.md`

## What the owner sees at the end
- Fatigue or not, and the rule it was checked against
- The new versions and the one thing that changed in each
- The rotation plan
- The item in queue/needs-your-ok.md to tick

## Never
- Pause, swap or edit a live ad from this command.
- Change the budget, audience or offer. This playbook only replaces the creative.
- Use a photo, font or logo that is not in asset-library.md, or generate a real person's face.
