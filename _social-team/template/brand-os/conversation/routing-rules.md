# Routing rules

> Read by: leads-conversations. Tools: ManyChat (chat and DMs), HubSpot (CRM), Twilio (SMS), Calendly (your own booking link for leads), Front (shared inbox).
> Who handles each kind of message, how fast, and when a message is real enough to wake the owner.

## Hours
- Business hours: [FILL IN: days and times, with time zone]
- Quiet hours (nobody is woken): [FILL IN]

## Who handles what
| Intent | Looks like | Handled by | Channel | Reply within |
|---|---|---|---|---|
| FAQ | A question in conversation/faq-library.md | bot | where it came in | right away |
| New lead | Wants to buy, book or get a quote | bot qualifies, then [FILL IN: person] | [FILL IN] | [FILL IN] |
| Existing customer issue | Order, delivery, account | [FILL IN: person or team] in Front | [FILL IN] | [FILL IN] |
| Complaint | Upset, something went wrong | [FILL IN: person] | [FILL IN] | [FILL IN] |
| Partnership or press | Collaboration, media | the owner | [FILL IN] | [FILL IN] |
| Job seeker | Asking about work | [FILL IN] | [FILL IN] | [FILL IN] |
| Spam or abuse | Links, insults, bots | nobody, archive it | none | none |

## What makes a lead real
A lead counts as real when it meets all of these:
| Check | Real when |
|---|---|
| [FILL IN: e.g. what they want] | [FILL IN] |
| [FILL IN: e.g. where they are] | [FILL IN] |
| [FILL IN: e.g. size of the order or job] | [FILL IN] |

Example row (Northwind Coffee): | What they want | A wholesale order for a cafe or an office |

## Waking the owner
The playbook dm-lead-at-11pm reads this.
- Wake the owner outside business hours only when: the lead is real (table above) and [FILL IN: anything else, e.g. they asked to talk today]
- How: Twilio SMS to [FILL IN: the owner's number is stored in your Twilio settings, not here]
- The SMS says: "[FILL IN: e.g. Real lead from <channel>: <one-line summary>. Details in HubSpot.]"
- Everything else waits for the morning in Front, with the bot's auto-reply sent.

## HubSpot
- Before creating a contact, search HubSpot by email and phone. If one exists, update it. Never create a second record for the same person.
- Fields the bot fills: [FILL IN: name, email, phone, source channel, what they asked]
- Lead source value: [FILL IN: the value you use for chat and DM leads]

## Never
- Share one customer's details with another.
- Give a refund, a discount or a promise that is not in faq-library.md without a person's OK.
- Send the booking link to anyone who is not a real lead: [FILL IN: or "send it to everyone who asks"]
