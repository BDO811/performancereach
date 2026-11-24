---
description: Act on the boxes the owner ticked, then hand approved work to Publish.
---

# Process approvals

1. Run `python3 -I tools/queue.py process`. It moves every decided item to Done, logs each decision
   and prints one line per item: APPROVED, REJECTED, or BOTH BOXES. Exit code 2 means owner/STOP is
   set: stop and say so.
2. If it printed "nothing ticked", tell the owner and stop.
3. Use the cmo agent in mode 3, the owner's approvals, with the printed lines.
4. Run the CMO's brief for director-publish, then any other brief it wrote, as in "Running a CMO
   brief" in CLAUDE.md. Every package is marked [PASTE] or [SEND] for the owner.
5. Tell the owner what is ready to paste or send and in which slot, what went back for changes, and
   any item with both boxes ticked.
