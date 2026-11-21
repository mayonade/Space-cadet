---
description: Run the marketing director's cycle - read results, call tests, plan and prepare the next launches
argument-hint: "[optional focus, e.g. 'direct mail' or 'tier A only']"
---

Run one full director cycle. Focus, if given: $ARGUMENTS

1. **Orient.** Read `experiments/learnings.md`, `experiments/backlog.md`, `playbook/stack.md`,
   and any `experiments/EXP-*.md` marked running. Check `data/` for a lead file.
   - No lead file: ask the owner for a CRM export (or try the CRM connector) and stop there.
   - New or changed export: have `lead-segmenter` ingest it and report tiers and reach.
2. **Close the loop.** For each running test past its end date, get the result counts (ask the
   owner if no connected tool has them) and have `experiment-analyst` read it out. Promote
   winners to control. Record every result.
3. **Decide.** Pick the next tests from the backlog: highest-ranked ones the list can power and
   the connected stack can deliver, at most one per channel, no collisions on the same leads.
   Say in two lines why these.
4. **Build.** In parallel, brief the specialists: `offer-strategist` first if the angle is new,
   then the channel strategists for copy and plans, `experiment-analyst` for the test design,
   `lead-segmenter` for arms and lists. Everything lands in `campaigns/<name>/` and
   `experiments/EXP-NNN-<slug>.md`.
5. **Gate.** Send every lead-facing item to `compliance-reviewer`. Fix and re-review until PASS.
6. **Bring it for approval.** Give the owner one short launch brief: what will go out, to how
   many leads, on which channels, when, what it costs, what we expect to learn, and exactly
   what they need to do or approve. Then stop. Do not send, post, order or spend.
7. **Housekeeping.** Update the backlog and stack status. Commit non-PII files only.
