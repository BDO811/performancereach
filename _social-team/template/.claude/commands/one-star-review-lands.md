---
description: Playbook. A one-star review just landed on Google Business Profile. Drafts a calm public reply and holds it for the owner. Never posts a reply on its own.
argument-hint: "<paste the review: reviewer name, date, stars and full text>"
---

# Playbook: one-star review lands

The event: $ARGUMENTS

## Before anything
1. If the file owner/STOP exists, stop. Append
   `YYYY-MM-DD HH:MM | orchestrator | stopped: owner/STOP present | -` to logs/activity.md
   and do nothing else.
2. Read owner/brand-voice.md, owner/approval-bar.md, owner/positioning.md and owner/budget-cap.md.
   They are read-only. If any still contains `[FILL IN:`, stop and tell the owner which file.

## Step 1. The orchestrator goes first
Use the orchestrator agent on this review as a playbook event
(priority: event, playbook: one-star-review-lands). It writes one brief for
Reviews & reputation to drafts/briefs/ with the review pasted in full.

## Worth acting on
Every one-star review gets a drafted answer. What changes is how it is handled.
Reviews & reputation sorts it, using brand-os/reputation/gbp-response.md and review-flow.md:
1. Complaint: a real customer with a real problem.
2. Question or mix-up: something the brand can answer or put right.
3. False claim: not a customer, spam, abuse, or anything that may be legal.
If the review mentions health, safety, a legal threat or a named member of staff,
it is URGENT whatever its sort.

## Steps
1. Reviews & reputation drafts the reply. Use the reviews-reputation agent on its brief.
   It reads brand-os/reputation/gbp-response.md (how to reply by star rating),
   review-flow.md, mentions-rules.md, and brand-os/brand-brain/voice-guide.md and
   tone-rules.md. It drafts the reply with Claude:
   - thank them and answer the actual point they made, in their words
   - offer the next step named in gbp-response.md, such as a private contact route
   - no arguing, no blame, no customer details, no refund or freebie promised
   It runs the voice check and saves drafts/YYYY-MM-DD-reviews-<slug>.md.
   For a false claim it drafts nothing public: it writes a note for the owner instead.
2. Pattern check. In the same file it notes whether the same complaint already appears in
   the Brand24 mentions export or in earlier review files in drafts/. If yes: "Seen before"
   with the file paths.
3. Run the orchestrator again on the return. It queues the reply for the owner.

## Who approves
Every reply to a negative review waits for the owner. No exceptions, whatever the bar says.
The orchestrator adds one item to queue/needs-your-ok.md in the format at the top of that file:
- Title: `Reply to a one-star review on Google Business Profile`, with URGENT in front if the
  review is urgent or listed under "Alert me right away" in owner/approval-bar.md.
- Why it waits: any reply to a negative review always waits.
- Spend: none. If the reply offers anything that costs money, it says so here.
Once the owner ticks Approve, the orchestrator briefs Publishing & social to post the reply.

## Log
Every agent appends one line per action to logs/activity.md:
`YYYY-MM-DD HH:MM | <agent> | <action> | <file>`
Example: `YYYY-MM-DD HH:MM | reviews-reputation | drafted reply to one-star review | drafts/YYYY-MM-DD-reviews-<slug>.md`

## What the owner sees at the end
- The sort, and whether it is URGENT
- The drafted reply, ready to read, and its voice-check result
- Whether the complaint has been seen before
- The item in queue/needs-your-ok.md to tick

## Never
- Post, edit or delete a reply from this command.
- Ask the reviewer to change or remove the review, or offer anything in exchange.
- Share any private detail about the customer in public.
- Promise a refund, discount or fix that the owner has not approved.
