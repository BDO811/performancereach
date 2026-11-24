---
description: Act on the boxes the owner ticked, then hand approved work to Publish.
---

# Process approvals

1. If `owner/STOP` exists, stop, log it and say so.
2. Use the cmo agent to read `queue/needs-your-ok.md`. For each ticked item it moves the item to
   Done and logs the decision. Rejected items go back to their director with the owner's note.
3. Use director-publish on the CMO's brief. It runs publish-scheduler, then the poster for each
   channel and publish-newsletter. Every package is marked [PASTE] or [SEND] for the owner.
4. If approved items include Social team work, use director-social for its calendar.
5. If approved items include a payment request, a contract or an invoice, remind the owner that they
   create or send it themselves.
6. Tell the owner what is ready to paste or send, and in which slot.
