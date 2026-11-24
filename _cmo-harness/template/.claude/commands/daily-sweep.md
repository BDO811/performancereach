---
description: The daily pass over comments, DMs and leads, ending with the morning page.
---

# Daily sweep

1. If `owner/STOP` exists, stop, log it and say so.
2. Run `python3 -I tools/cmo_context.py`. Exit code 2: stop and show the owner why.
3. Use the cmo agent to write today's daily briefs: one for director-community, then one for
   director-sales that depends on it (so leads community caught get scored the same day). Use brief
   priority `routine`.
4. Run each brief, in that order, as in "Running a CMO brief" in CLAUDE.md.
5. Run `/morning-page`.
