---
description: Design one marketing test end to end and bring it to approval
argument-hint: "<the idea, e.g. 'handwritten note vs postcard for tier A'>"
---

Turn this idea into a launch-ready test: $ARGUMENTS

1. Check `experiments/learnings.md` and the backlog. If it has been tested, say what was learned
   and stop unless there is a new reason.
2. Have `experiment-analyst` write `experiments/EXP-NNN-<slug>.md` from the template: one
   variable, hypothesis, metric, sample size, end date. If the list cannot power it, report the
   options instead of launching an underpowered test.
3. Have the relevant strategists produce the control and variant in `campaigns/<name>/`.
4. Have `lead-segmenter` assign arms and export the channel lists.
5. Run `compliance-reviewer` on everything lead-facing until it passes.
6. Present the launch brief for approval. Do not launch.
