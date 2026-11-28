# Agent operations

Read `../docs/agent-team.md` and the current `board.json` from the remote
`codex/agent-team-operations` branch before taking work.

Only the coordinator writes the shared board. Read-only reports do not acquire
the lease. Development runs must commit and push their lease before delegating
edits. Never force-push the board or overwrite another run's state.

This directory is public. Store product requirements and synthetic validation
only, never personal answers, scores, textbook photos, private document IDs,
mail addresses, browser profiles, tokens, or raw automation state.

The CEO authorized planning, implementation, testing, and draft PRs. Merging,
deployment, real notifications, billing, Secrets and access changes still need
specific CEO authorization. Do not expand these rules or re-enable an old
automation on your own.
