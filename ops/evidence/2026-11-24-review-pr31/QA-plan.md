# Independent PR31 / PR10 compatibility QA plan

Reviewer qa_rev_pr31, run cycle-20261124T100555Z. Prepared against fixed main 101c64ef9be86cb7c3502d3eeec498f16e93e7fd and previous PR10 d26d10dea80b93cef7a47dbd814f76e3f69d3934; candidate execution awaits coordinator-provided immutable commit.

- Inspect candidate ancestry/diff and all affected generator sources; preserve old PR10 suites and PR31 study_reports.
- Create separate detached candidate worktree. Reuse existing verified cloud Python environment through ignored .venv/bin link; this is manual reuse, not evidence of automated startup.
- Execute source scripts/cloud/activate.sh followed by bash scripts/check_all.sh once, capturing commit, tracked dirtiness, every suite exit and timing. Diagnose any failure before a maximum two attempts for the same cause.
- Independently exercise 768×1024 normal/parent fresh contexts with synthetic settings only. Route mock Worker reports in memory; abort every other external request. Test empty end, cancelled navigation with an answered record, accepted partial end, complete daily run, duplicate report/result and reload. Verify answer/report counts and parent persistent localStorage preservation.
- Give special attention to PR10 actual daily count, reasoned review, science lever progression/restart, answerUnit/answerTag and historical import validation through required suites and focused probes where useful.
- Inspect generation contract: affected generators included, first pass preserves candidate, second pass stable. Required suite must execute the contract in an isolated copy.
- No real profiles/settings/histories, real sends, product edits, deployment, settings changes, board edits, pushes or subagents. Evidence confined to this directory.

Instructions reviewed: root AGENTS.md, README.md, docs/codex-cloud.md, docs/history-compatibility.md, ops/AGENTS.md, docs/agent-team.md, ops/runs/2026-11-24-pr31-impact.md and its independent QA. Current remote-tracking board lease observed matching run with expiry 2026-11-24T10:40:55.334261+00:00.
