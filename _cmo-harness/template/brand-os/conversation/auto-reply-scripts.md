# Auto-reply scripts

> Read by: leads-conversations. These are the exact messages ManyChat (and Twilio for SMS) may send without a person.
> Write them in your voice. The bot sends them word for word, filling only the parts in angle brackets.
> Anything outside these scripts and conversation/faq-library.md goes to a person.

## How the bot introduces itself
[FILL IN: e.g. say it is an automated assistant for <brand>]

## Scripts
| ID | When it is sent | Message | Next step |
|---|---|---|---|
| R01 Hello, business hours | First message in business hours | [FILL IN] | answer from faq-library.md or route |
| R02 Hello, after hours | First message outside business hours | [FILL IN: say when a person will reply] | log in Front, check routing-rules.md for waking the owner |
| R03 FAQ answer | The question matches faq-library.md | <approved answer> + [FILL IN: e.g. "Did that answer it?"] | if no, hand over |
| R04 Lead questions | Someone wants to buy, book or get a quote | [FILL IN: the questions that test routing-rules.md, one at a time] | create or update the contact in HubSpot |
| R05 Booking link | A real lead wants to talk | [FILL IN: your line] + <your Calendly link> | log the booking in HubSpot |
| R06 Hand over | The bot cannot help | [FILL IN: tell them a person will reply and roughly when] | assign in Front |
| R07 Complaint | Someone is upset | [FILL IN: sorry, a person will pick this up] | route to the complaint owner, no promises |
| R08 Stop | They ask to stop messages | [FILL IN: confirm they will get no more messages] | mark as opted out in HubSpot and ManyChat |
| R09 Not understood | The bot cannot tell what they want | [FILL IN] | after [FILL IN: how many tries], hand over |

Example (Northwind Coffee), R02: "Thanks for the message. We're roasting, not reading, right now. A person will reply after we open at [your opening time]."

## Rules
- Never more than [FILL IN: how many] automated messages before a person takes over.
- Never send a price, a date or a policy that is not in faq-library.md.
- A stop request is honoured at once, on every channel.
