---
description: The CMO plans the week and runs research and content through to the owner's approval queue.
argument-hint: "[optional focus for this week]"
---

# Run the week

Owner's focus for this week, if any: $ARGUMENTS

## 1. Facts first
Run `python3 -I tools/cmo_context.py`. It writes `reports/plans/<week>-context.md`.
If it exits with code 2, stop: show the owner the "Can the CMO plan" section of that file and do
nothing else.

## 2. The plan
Use the cmo agent in mode 1, plan the week. Pass it the context file path and the owner's focus.

## 3. Check the plan
Run `python3 -I tools/check.py plan`. If it prints problems, use the cmo agent again with the printed
problems and ask it to fix only those. Run the check again. After two failed fixes, stop and show the
owner the problems.

## 4. Run the briefs
For each CMO brief in the plan's Briefs list, in order (wait for its depends_on to finish first),
follow "Running a CMO brief" in CLAUDE.md.

## 5. Hand over
Stop when the week's drafts are in `queue/needs-your-ok.md`. Tell the owner how many items wait,
what may auto ship, what was held for voice review and what is blocked.

Publishing starts only after the owner ticks and runs `/process-approvals`.
