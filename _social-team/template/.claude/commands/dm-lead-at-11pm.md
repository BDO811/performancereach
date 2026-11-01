---
description: Playbook. A DM or lead comes in out of hours. Answers with approved words through ManyChat, logs the lead in HubSpot, and wakes the owner only if it is real.
argument-hint: "<paste the message: channel, sender name or handle, time and full text>"
---

# Playbook: DM or lead at 11pm

The event: $ARGUMENTS

## Before anything
1. If the file owner/STOP exists, stop. Append
   `YYYY-MM-DD HH:MM | orchestrator | stopped: owner/STOP present | -` to logs/activity.md
   and do nothing else.
2. Read owner/approval-bar.md, owner/brand-voice.md, owner/positioning.md and owner/budget-cap.md.
   They are read-only. If any still contains `[FILL IN:`, stop and tell the owner which file.

## Step 1. The orchestrator goes first
Use the orchestrator agent on this message as a playbook event
(priority: event, playbook: dm-lead-at-11pm). It writes one brief for
Leads & conversations to drafts/briefs/ with the message pasted in full and the time it arrived.

## Worth acting on
Every message gets an answer. Only some wake the owner.
Leads & conversations sorts it using the definitions in brand-os/conversation/routing-rules.md:
1. Real lead: someone asking to buy, book or get a quote.
2. Problem: a support problem, a complaint, anything about money, anything legal.
3. Question: answered word for word in brand-os/conversation/faq-library.md.
4. Spam: bots and noise.
When it is unclear, it is treated as a lead. If routing-rules.md defines none of these, do not
guess: treat every message as a lead, and the orchestrator adds an item to
queue/needs-your-ok.md asking the owner to fill routing-rules.md.

## Steps
1. Leads & conversations answers. Use the leads-conversations agent on its brief. It reads
   faq-library.md, routing-rules.md and brand-os/conversation/auto-reply-scripts.md, then:
   - Question: replies with the approved answer from faq-library.md, in the channel's
     script from auto-reply-scripts.md.
   - Real lead or problem: replies with the out-of-hours holding line from
     auto-reply-scripts.md.
   - Ready to talk, if routing-rules.md says so: adds the brand's Calendly booking link
     with the wording from auto-reply-scripts.md.
   - Spam: no reply.
   The reply goes out through ManyChat for Instagram and Facebook DMs. Until ManyChat is
   connected, the reply is written ready to paste. Every reply passes the voice check first;
   a fail means the person gets the holding line instead.
2. Leads & conversations records it. For a real lead, it looks the person up in HubSpot by
   email or phone first. If they exist, it adds a note. If not, it creates one contact with
   only what they wrote. Never a second record for the same person. Output:
   drafts/YYYY-MM-DD-inbox-<slug>.md.
3. Run the orchestrator again on the return. It applies the wake rule and the owner gate below.

## Wake the owner only if it is real
- Real lead or problem: the orchestrator puts an item at the top of the Open list in
  queue/needs-your-ok.md with URGENT in the title, in the format at the top of that file.
  This is the alert. The person already has the holding reply, so nothing else is sent.
- Question or spam: no alert. It shows up in the next session's summary.

## Who approves
These wait in queue/needs-your-ok.md:
- Any reply beyond the approved answer or holding line. New words never go out from here.
- Anything about a price, a discount, a refund or a date that is not word for word in
  faq-library.md.
- A complaint that may need a public reply. That goes to Reviews & reputation through the
  orchestrator.

## Log
Every agent appends one line per action to logs/activity.md:
`YYYY-MM-DD HH:MM | <agent> | <action> | <file>`
Example: `YYYY-MM-DD HH:MM | leads-conversations | holding reply sent, real lead logged in HubSpot | drafts/YYYY-MM-DD-inbox-<slug>.md`

## What the owner sees at the end
- Real lead or problem: an URGENT item at the top of the queue saying who wrote, what they
  asked, what was sent back and the HubSpot record
- Question or spam: one line in the next summary
- Any FAQ gap, so the owner can add the answer to faq-library.md

## Never
- Write new reply text and send it. Only approved answers and scripts go out.
- Quote, promise or hint at a price, discount, refund or delivery date.
- Wake the owner for spam or for a question the FAQ already answers.
