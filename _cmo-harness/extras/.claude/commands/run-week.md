---
description: The CMO plans the week and runs research and content through to the owner's approval queue.
argument-hint: "[optional focus for this week]"
---

# Run the week

Owner's focus for this week, if any: $ARGUMENTS

1. If `owner/STOP` exists, stop, log it and say so.
2. Use the cmo agent to plan this week. It writes `reports/plans/YYYY-Www.md` and one brief per
   director in `drafts/briefs/cmo/`, listed in run order.
3. For each CMO brief, in order: use the director it names on that brief. The director writes one
   brief per agent and lists them. Use each agent on its brief, one at a time. Then use the director
   again with the returns.
4. Order for a normal week: director-research, director-seo if briefed, director-content, then
   director-paid and director-social if briefed.
5. Use the cmo agent again with every director's return. It routes public facing work through
   content-brand-check and content-approval-desk.
6. Stop there. Tell the owner the week is waiting in `queue/needs-your-ok.md`, with the count of
   items, what may auto ship, what was held and what is blocked.

Publishing starts only after the owner ticks and runs `/process-approvals`.
