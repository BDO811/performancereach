# Content calendar

> Read by: content-engine (takes the next row marked `ready`), the orchestrator, and the playbook content-calendar-looks-thin.
> If your calendar lives in Airtable, keep these exact column names there and export it to this file each week,
> or connect it later. The agents read the same columns either way.
> Agents may add rows, always with the status `idea`.

## Status values
| Status | Means | Set by |
|---|---|---|
| idea | Worth doing, nothing written yet | you or any agent |
| briefed | The orchestrator wrote the brief | orchestrator |
| ready | Approved to draft. The content engine takes the next one | you, or the orchestrator when owner/approval-bar.md allows |
| drafted | A draft is saved in drafts/ | content-engine |
| held | Failed the voice check, waiting in queue/held-for-voice-review.md | content-engine |
| approved | Passed your review | you, or the orchestrator when owner/approval-bar.md allows |
| scheduled | In Metricool with a date and time | publishing-social |
| published | Live | publishing-social |
| dropped | Not doing it, kept for the record | you |

## The calendar
| ID | Publish date | Channel | Topic | Pillar | Goal | Keyword | Status | Brief | Draft file | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 001 | [FILL IN: YYYY-MM-DD] | [FILL IN: article, linkedin, instagram, facebook, tiktok, newsletter, gbp] | [FILL IN] | [FILL IN: from messaging-bank.md] | [FILL IN: reach, clicks, leads, sales] | [FILL IN: articles only] | ready | [FILL IN: one line, or a link to the brief] | | |
| 002 | [FILL IN] | [FILL IN] | [FILL IN] | [FILL IN] | [FILL IN] | | idea | | | |

Example row (Northwind Coffee): | 003 | [date] | linkedin | Why we print the roast date | Freshness | reach | | ready | Three things the roast date tells you | | |

## When the calendar counts as thin
- Thin means fewer than [FILL IN: how many ready or scheduled items a week before it counts as thin] items in the next [FILL IN: how far ahead you look]
- What happens: the orchestrator runs /content-calendar-looks-thin. New rows arrive as `idea`. They become `ready` only when you, or owner/approval-bar.md, say so.

## How often each channel posts
See social/posting-schedule.md. The calendar fills those slots; it does not set them.
