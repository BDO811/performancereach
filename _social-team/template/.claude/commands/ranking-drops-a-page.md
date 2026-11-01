---
description: Playbook. A page lost ranking. Confirms the drop, finds the likely cause and drafts a content refresh with Surfer. Never changes a live page on its own.
argument-hint: "<page URL, keyword, and what the Semrush alert showed>"
---

# Playbook: ranking drops a page

The event: $ARGUMENTS

## Before anything
1. If the file owner/STOP exists, stop. Append
   `YYYY-MM-DD HH:MM | orchestrator | stopped: owner/STOP present | -` to logs/activity.md
   and do nothing else.
2. Read owner/positioning.md, owner/approval-bar.md, owner/brand-voice.md and owner/budget-cap.md.
   They are read-only. If any still contains `[FILL IN:`, stop and tell the owner which file.

## Step 1. The orchestrator goes first
Use the orchestrator agent on this event as a playbook event
(priority: event, playbook: ranking-drops-a-page). It briefs Search visibility first, then
decides from its report whether to brief a refresh.

## Worth acting on
The drop is worth acting on only if all three are true:
1. It counts as "dropped" under brand-os/signals-seo/serp-rules.md.
2. The page now sits below its target in brand-os/signals-seo/ranking-targets.md.
3. The keyword is the one brand-os/signals-seo/keyword-map.md assigns to this page.
If serp-rules.md does not define a drop, do not guess one. The orchestrator adds an item to
queue/needs-your-ok.md asking the owner to set it, logs it and stops.
If the drop is not worth acting on, it logs the reason and stops.

## Steps
1. Search visibility finds the likely cause. Use the search-visibility agent on its brief.
   It reads the four brand-os/signals-seo/ rule files and the latest exports, and checks,
   in this order:
   - the Semrush SEO alert and rankings: which pages moved up for the same keyword
   - Google Search Console: the page's queries, clicks and positions
   - Google Analytics 4: whether the drop cost sessions
   - Ahrefs: backlinks the page lost
   - Screaming Frog: problems on the page (broken links, missing title, blocked from search)
   It writes drafts/YYYY-MM-DD-search-<slug>.md with one action and its owner.
2. Run the orchestrator again on the report. If the cause is a technical problem, it does
   not brief a refresh: it queues the fix for the owner, because a content refresh does not
   fix a broken page. If the cause is content, it briefs the Content engine.
3. Content engine drafts the refresh. Use the content-engine agent on its brief. It builds
   the refresh brief in Surfer for the keyword, then Claude drafts the changes section by
   section (add, update, cut) to drafts/YYYY-MM-DD-blog-<slug>-refresh.md. It runs
   brand-os/content/seo-checklist.md and the voice check. The URL and the assigned keyword
   stay the same.
4. Run the orchestrator again on the draft. It applies the owner gate below and briefs
   Publishing & social to update the page in WordPress if the refresh may ship.

## Who approves
These wait in queue/needs-your-ok.md, in the format at the top of that file:
- Any technical fix to the site. The owner or their web person makes it.
- A refresh that changes a claim, a price, an offer or a promise on the page.
- Anything that names a real person, needs any spend, or carries a [VERIFY] mark.
- Anything not clearly listed under "Auto-ships" in owner/approval-bar.md.

## Log
Every agent appends one line per action to logs/activity.md:
`YYYY-MM-DD HH:MM | <agent> | <action> | <file>`
Example: `YYYY-MM-DD HH:MM | search-visibility | confirmed ranking drop, cause found | drafts/YYYY-MM-DD-search-<slug>.md`

## What the owner sees at the end
- Real or not, and the rule and target it was checked against
- The likely cause, with what each check found
- The refresh draft, section by section, or the technical fix to make
- The items added to queue/needs-your-ok.md

## Never
- Edit, unpublish or redirect a live page from this command.
- Change the page's URL or its assigned keyword.
- Quote positions or traffic that are not in the Semrush, Search Console or Analytics exports.
