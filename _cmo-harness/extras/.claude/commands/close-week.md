---
description: Close the week. Measure what made money and feed it into next week's plan.
---

# Close the week

1. If `owner/STOP` exists, stop, log it and say so.
2. Run `python3 -I tools/loop_data.py`. It writes `loop/YYYY-MM-DD-data.md` from this week's exports.
   Read its Notes and its "Exports with no rows" line, and tell the owner which exports are missing.
3. Use the cmo agent to write the close of week briefs: director-loop, director-finance
   (finance-reporting), and director-paid and director-social when they ran this week.
4. Run each brief as in "Running a CMO brief" in CLAUDE.md. director-loop goes first.
5. Use the cmo agent in mode 2 on the returns. Check `loop/next-week-inputs.md` was rewritten by
   loop-feeder, then tell the owner the week against `owner/targets.md`.
