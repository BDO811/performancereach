---
description: Playbook. The content calendar has gaps. Finds every empty slot, fills it with on-brand drafts and books them in Metricool. Only schedules what clears the approval bar.
argument-hint: "<the date range to check, for example the next two weeks>"
---

# Playbook: content calendar looks thin

The event: $ARGUMENTS

## Before anything
1. If the file owner/STOP exists, stop. Append
   `YYYY-MM-DD HH:MM | orchestrator | stopped: owner/STOP present | -` to logs/activity.md
   and do nothing else.
2. Read owner/brand-voice.md, owner/approval-bar.md, owner/positioning.md and owner/budget-cap.md.
   They are read-only. If any still contains `[FILL IN:`, stop and tell the owner which file.

## Step 1. The orchestrator goes first
Use the orchestrator agent on this date range as a playbook event
(priority: event, playbook: content-calendar-looks-thin). It briefs Publishing & social
to find the gaps, then briefs the Content engine to fill them.

## Worth acting on
A slot counts as empty only if both are true:
1. brand-os/social/posting-schedule.md says the channel posts on that day and time.
2. brand-os/content/content-calendar.md has nothing marked `ready` or `scheduled` for it.
If posting-schedule.md sets no cadence for a channel, do not guess one. The orchestrator adds
an item to queue/needs-your-ok.md asking the owner to set it, and skips that channel.
If there are no empty slots, it logs that and stops.

## Steps
1. Publishing & social finds the gaps. Use the publishing-social agent on its brief.
   It compares content-calendar.md with posting-schedule.md and
   brand-os/social/channel-playbooks.md and writes drafts/YYYY-MM-DD-schedule-<slug>.md:
   one row per empty slot with channel, day, time and format.
2. Run the orchestrator again on the gap list. It writes one brief per slot for the
   Content engine. Topics come, in this order, from:
   items in content-calendar.md marked `idea`, proof points in
   brand-os/brand-brain/messaging-bank.md not used recently, and patterns in
   brand-os/content/hook-bank.md.
3. Content engine fills them. Use the content-engine agent on each brief. Claude drafts each
   piece to drafts/YYYY-MM-DD-<channel>-<slug>.md and runs the voice check. A fail goes to
   queue/held-for-voice-review.md and that slot stays empty.
4. Run the orchestrator again on the drafts. It adds every new item to content-calendar.md
   as `ready` and applies the owner gate below.
5. Publishing & social books what may ship. Use the publishing-social agent on its brief.
   It fits each passing draft to its channel, adds hashtags only as
   brand-os/social/hashtag-rules.md allows, and schedules it in Metricool for the slot in
   posting-schedule.md. Until Metricool is connected, it writes the ready-to-paste version
   marked [PASTE].

## Who approves
These wait in queue/needs-your-ok.md, in the format at the top of that file:
- Any filler post on a channel listed under "Channels that never auto-ship" in
  owner/approval-bar.md.
- Anything that names a real person, mentions a price or an offer, or needs any spend.
- Anything with an unresolved [VERIFY] mark.
- Anything else not clearly listed under "Auto-ships" in owner/approval-bar.md.
Only drafts that passed the voice check and sit inside the approval bar are scheduled.

## Log
Every agent appends one line per action to logs/activity.md:
`YYYY-MM-DD HH:MM | <agent> | <action> | <file>`
Example: `YYYY-MM-DD HH:MM | publishing-social | scheduled filler post in Metricool | drafts/YYYY-MM-DD-schedule-<slug>.md`

## What the owner sees at the end
- The empty slots found, per channel
- Which were filled and scheduled, which wait for the owner, which were held for voice
- Any channel skipped because it has no cadence set
- Anything marked [PASTE], and the items in queue/needs-your-ok.md

## Never
- Move, rewrite or delete an item that is already `scheduled`.
- Fill a slot just to fill it. An empty slot beats an off-brand post.
- Invent facts, numbers or customer stories to make a filler post.
