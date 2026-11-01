---
description: Playbook. A competitor just launched a promo. Confirms it, re-briefs this week's plan and refreshes the creative. Never matches a price or an offer on its own.
argument-hint: "<competitor name, what the promo is, and the Brand24 mention or link>"
---

# Playbook: competitor drops a promo

The event: $ARGUMENTS

## Before anything
1. If the file owner/STOP exists, stop. Append
   `YYYY-MM-DD HH:MM | orchestrator | stopped: owner/STOP present | -` to logs/activity.md
   and do nothing else.
2. Read owner/positioning.md, owner/approval-bar.md, owner/brand-voice.md and owner/budget-cap.md.
   They are read-only. If any still contains `[FILL IN:`, stop and tell the owner which file.

## Step 1. The orchestrator goes first
Use the orchestrator agent on this event as a playbook event
(priority: event, playbook: competitor-drops-a-promo). It briefs Market radar first,
decides from the radar note whether to act, then writes the next briefs.

## Worth acting on
The promo is worth acting on only if all three are true:
1. The brand is listed under "Competitors we watch" in brand-os/brand-brain/positioning.md.
2. The promo is confirmed by the Brand24 mention plus one more source with a link
   (their own site, page or post).
3. It reaches an audience or a topic you own, from owner/positioning.md and
   brand-os/signals-seo/keyword-map.md.

If "Competitors we watch" is empty, do not guess a list. The orchestrator adds an item to
queue/needs-your-ok.md asking the owner to fill it, logs it and stops.
If the promo is not worth acting on, it logs the reason and stops.

## Steps
1. Market radar confirms it. Use the market-radar agent on its brief in drafts/briefs/.
   It reads the Brand24 mentions export, checks the second source, and writes
   drafts/YYYY-MM-DD-radar-<slug>.md with the promo at the top under "Promo watch":
   who, what, where seen, link, date. Facts with links only. No guesses about their results.
2. Run the orchestrator again on the radar note. If the three tests pass, it writes the
   next two briefs.
3. Content engine re-briefs the plan. Use the content-engine agent on its brief. It reads
   brand-os/brand-brain/positioning.md and messaging-bank.md and
   brand-os/content/content-calendar.md, then proposes, item by item, what to keep this week,
   what to reframe around your own proof points, and what to add. It answers the promo with
   your positioning, never by copying it. New pieces are drafted with Claude to
   drafts/YYYY-MM-DD-<channel>-<slug>.md with the voice check as usual.
4. Creative studio refreshes the creative. Use the creative-studio agent on its brief. It
   rebuilds the visuals for the changed items in Canva, from brand-os/creative/visual-specs.md
   and asset-library.md, and saves drafts/YYYY-MM-DD-<channel>-<slug>-creative.md with the
   spec check.
5. Run the orchestrator again on the returns. It applies the owner gate below.

## Who approves
These wait in queue/needs-your-ok.md, in the format at the top of that file:
- Anything that responds to a competitor. This playbook is one, so its changed items wait
  unless owner/approval-bar.md clearly lets them auto-ship.
- Any price change, discount, offer, match or giveaway. Pricing is always the owner's call.
- Any spend. If it would pass owner/budget-cap.md, the item title says OVER CAP.
- Anything that names the competitor or a real person, and anything with a [VERIFY] mark.

## Log
Every agent appends one line per action to logs/activity.md:
`YYYY-MM-DD HH:MM | <agent> | <action> | <file>`
Example: `YYYY-MM-DD HH:MM | market-radar | confirmed promo from <competitor> | drafts/YYYY-MM-DD-radar-<slug>.md`

## What the owner sees at the end
- Real or not, and the two sources that confirmed it
- The calendar changes proposed, item by item
- The refreshed creative files and their spec checks
- The items added to queue/needs-your-ok.md

## Never
- Match, undercut or announce a price or an offer without a ticked box.
- Name or mock the competitor in public copy.
- Copy their wording, or invent anything about their promo, sales or customers.
