---
description: Playbook. A post is taking off. Confirms it, repurposes it for the other channels and prepares a Meta boost with a margin check. The boost never runs without the owner.
argument-hint: "<link to the post, the channel, and what Meta insights show>"
---

# Playbook: a post goes viral

The event: $ARGUMENTS

## Before anything
1. If the file owner/STOP exists, stop. Append
   `YYYY-MM-DD HH:MM | orchestrator | stopped: owner/STOP present | -` to logs/activity.md
   and do nothing else.
2. Read owner/budget-cap.md, owner/approval-bar.md, owner/brand-voice.md and owner/positioning.md.
   They are read-only. If any still contains `[FILL IN:`, stop and tell the owner which file.

## Step 1. The orchestrator goes first
Use the orchestrator agent on this event as a playbook event
(priority: event, playbook: a-post-goes-viral). It decides whether the post is really
taking off, then briefs Publishing & social and Results & ROI.

## Worth acting on
The orchestrator checks the post against:
- brand-os/reporting/kpi-model.md: what counts as a post far above normal for its channel
- brand-os/reporting/attribution.md: whether the reach comes from the audience you want
- the latest Meta insights export for the post, with its date

It acts only if both are true:
1. The post passes the rule in kpi-model.md.
2. The reach comes from the people described in owner/positioning.md under "Who we are for".
If kpi-model.md sets no such rule, do not guess one. The orchestrator adds an item to
queue/needs-your-ok.md asking the owner to set it, logs it and stops.
If the post is not taking off, it logs the reason and stops.

## Steps
1. Publishing & social repurposes it. Use the publishing-social agent on its brief.
   From brand-os/social/channel-playbooks.md it picks the other channels and formats, and
   Claude writes a version for each from the same post: the same idea, fitted to the channel,
   no new claims. Each version goes through the approval check and, if it passes, into the
   next open slot in brand-os/social/posting-schedule.md. Output:
   drafts/YYYY-MM-DD-schedule-<slug>.md.
2. Publishing & social prepares the boost. A Meta boost is spend, so it is never scheduled.
   It goes to queue/needs-your-ok.md with the post, the audience and how long to run it,
   and the amount left blank for the owner.
3. Results & ROI checks it is worth paying for. Use the results-roi agent on its brief.
   It runs the margin watch from brand-os/reporting/margin-rules.md for the channel, compares
   this month's spend with owner/budget-cap.md, and writes drafts/YYYY-MM-DD-report-<slug>.md.
   Its result is added to the boost item: within limit, near limit or over limit.
4. Run the orchestrator again on the returns. It applies the owner gate below.

## Who approves
A boost is spend, so it always waits for the owner. No exceptions.
- The boost item goes to queue/needs-your-ok.md in the format at the top of that file.
  If it would pass owner/budget-cap.md, the title says OVER CAP and it never auto-ships.
- Repurposed versions also wait if they name a real person, mention a price or an offer,
  carry a [VERIFY] mark, or are not clearly listed under "Auto-ships" in owner/approval-bar.md.
Once the owner ticks Approve and fills the amount, the orchestrator briefs Publishing & social
to set the boost up in Meta exactly as approved.

## Log
Every agent appends one line per action to logs/activity.md:
`YYYY-MM-DD HH:MM | <agent> | <action> | <file>`
Example: `YYYY-MM-DD HH:MM | results-roi | margin check for Meta boost | drafts/YYYY-MM-DD-report-<slug>.md`

## What the owner sees at the end
- Taking off or not, and the rule it was checked against
- The repurposed versions and the slot each one got
- The boost item: post, audience, length, margin check, amount left for you to fill
- The items in queue/needs-your-ok.md to tick

## Never
- Start, raise or extend a boost from this command.
- Edit the original post while it is performing.
- Quote reach or engagement numbers that are not in the insights export.
