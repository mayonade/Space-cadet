# Franchise lead marketing team

A marketing department built from Claude Code agents. One director that cares only about booked
intro calls, and seven specialists it delegates to. It plans and tests omni-channel outreach
(email, LinkedIn, retargeting ads, direct mail, phone) across a large list of franchise leads.

## Start

1. Export leads from the CRM as CSV and drop the file in `data/` (ignored by git).
2. Open Claude Code in this repo and run `/cmo`.

The director ingests and tiers the list, picks the first tests from `experiments/backlog.md`,
has the specialists draft everything, runs it past compliance, and brings you a launch plan to
approve. Nothing is sent, posted, mailed or spent without your yes.

## Layout

    CLAUDE.md               the director's standing orders
    .claude/agents/         the seven specialists + compliance gate
    .claude/commands/       /cmo, /launch-test, /readout
    playbook/               strategy, compliance rules, tool stack
    experiments/            backlog, template, learnings log
    tools/mkt.py            lead scoring, test assignment, channel exports, test math
    data/                   lead files (never committed)

## The tool on its own

    python3 tools/mkt.py ingest data/crm_export.csv
    python3 tools/mkt.py assign EXP-001 --arms control,variant --tier A,B
    python3 tools/mkt.py export --exp EXP-001
    python3 tools/mkt.py size --baseline 0.02 --lift 0.5
    python3 tools/mkt.py readout --arm control:1000:12 --arm variant:1000:25
