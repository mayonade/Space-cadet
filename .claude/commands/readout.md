---
description: Call a test - win, loss or no call - and record the learning
argument-hint: "<EXP-ID> [arm:n:conversions ...]"
---

Read out this test: $ARGUMENTS

1. Open the experiment file. Confirm the end date has passed or the stop rule was met; if not,
   say so and report interim numbers as interim only.
2. Get per-arm counts (leads contacted, conversions on the primary metric, booked calls, shows).
   Use the numbers supplied; otherwise ask. Never estimate them.
3. Have `experiment-analyst` run the readout and write the verdict into the experiment file.
4. Add a one- or two-line entry to `experiments/learnings.md`, update `experiments/backlog.md`,
   and if there is a winner, state what becomes the new control and what to test against it next.
