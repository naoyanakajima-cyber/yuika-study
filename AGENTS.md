# Cloud development

Read `README.md`, `docs/codex-cloud.md`, and instructions in affected subdirectories.
Use Codex Cloud; development must not depend on a local PC remaining online.

## Setup and verification

- Saved environment Install: use the standalone, commit-pinned configuration
  rendered by `scripts/cloud/render_config.py`; it prepares a separate checkout
  without requiring setup files on the platform's initial main checkout.
- Saved Start skill: `.agents/skills/yuika-cloud-start/SKILL.md`. Preserve existing
  branches/changes; verify startup evidence before manual recovery. Receipts,
  an empty skill list, and revision numbers alone do not prove auto-application.
- Setup: `bash scripts/cloud/setup.sh` from the repository root.
- Each new shell: `source scripts/cloud/activate.sh`.
- All required checks, including suites added by later PRs:
  `bash scripts/check_all.sh`. It activates the existing cloud venv, fixes browser
  test RNG seed to 20261110, and reports HEAD, dirty state, exit codes and timings.
  Every suite runs even after a failure; any failure makes the command fail.
  Notification tests use mock APIs only. Setup remains a separate prerequisite.
- Preview: `python scripts/cloud/serve.py --port 8000`; use the cloud browser at
  `http://127.0.0.1:8000/`. It blocks notification APIs through CSP.
- Browser tests need loopback sockets and browser process execution. Use only
  permission mechanisms explicitly supported by the current execution tools.
  Keep enforced network restrictions. If unavailable, stop and report unverified;
  never copy permission arguments from another environment or bypass restrictions.
- Never weaken assertions, skip checks, disable TLS validation, or retry a failed
  test until it happens to pass. Diagnose failures and report remaining limitations.

## Autonomous execution rules (自律実行ルール)

- If a test or verification fails, investigate the cause, fix it, and retest
  autonomously for up to three repair-and-retest cycles after the initial failure.
  Keep assertions and safety checks intact; do not retry without diagnosis.
- Continue until the task's completion criteria are met. Progress reports must
  not pause execution. Resolve ambiguous specifications with reasonable
  assumptions and document those assumptions in the PR description. Mark
  provisional settings, including review intervals, explicitly as proposals
  (仮案), not approved or validated product decisions.
- Stop and ask a person before merging (including main), publication, deployment,
  Secrets changes, incurring charges, sending real notifications, or changing
  sharing scope, or if a failure remains after three repair-and-retest cycles.
  Honor explicit task prohibitions; this rule grants no authorization for those
  actions. Complete safe, independent work before requesting approval.
- Branch pushes and draft PR creation are allowed within the task's scope.
  Start new work from the latest draft PR's branch, stack the new draft PR on
  that branch, and state the dependency and merge order in the PR description.
- At the end of every task, run `bash scripts/check_all.sh` as described above
  and record HEAD, every suite's result, and remaining limitations in the PR
  description. Use synthetic records and mock APIs only; do not maintain a
  separate, stale list of individual test commands here.
- Cloudflare preview failures are a known issue: report them separately from
  local verification; do not weaken checks or change deployment settings to
  make the preview pass.
- iPad-equivalent WebKit tests are planned for a separate PR and must be included
  in `scripts/check_all.sh` when added. Current Chromium tests do not establish
  Safari/WebKit or real-iPad compatibility.

## Release scope

- Environment setup alone does not authorize merging or production deployment.
- Merging to main automatically publishes GitHub Pages. Cloudflare builds are
  push-triggered. Main merges, publication, and deployment therefore require
  human approval; permission to push topic branches or open draft PRs does not
  authorize a production release or a manual deployment.
- Existing user authorization allows verified educational content updates using
  existing mechanisms: questions, explanations, hints, readings, options, and
  equivalent answer spellings through implementation, verification, branch push,
  and draft PR. This does not authorize merging or publication; obtain human
  approval for a release even when the content update itself is authorized.
- Grading engines, question selection algorithms, persistence or migrations,
  authentication, notifications, external communication, visibility, billing,
  dependencies, CI, and automation infrastructure remain draft PRs until the
  user approves their adoption. Keep these PRs draft until then.
- Preserve existing IDs, keys, and histories. A change in answer meaning requires
  a new question ID or an explicit pending decision. Even equivalent spellings
  must pass compatibility checks against synthetic historical records.
- Before an authorized content merge, independently verify the exact current
  head, diff, conflicts, and required checks. Never push directly to main.
  Confirm existing Pages deployment and live content before reporting published.
- Limit ordinary content releases to one per Japan calendar day. Do not expand
  these permissions or change their boundaries autonomously.

## Notifications and private data

- Do not send real email, Chat, or Slack messages or change production Secrets.
  Preserve the existing notification workflow.
- Analysis may read only user-authorized records and explicitly registered
  textbook files through private access. Prefer raw answers over AI summaries;
  deduplicate notification IDs and distinguish hint use and session timing.
- Do not place private inputs in published environment snapshots or the public
  repository. Fetch them privately at analysis time; do not search unrelated files.
- Tests and previews use fresh browser contexts and synthetic records only.
  Never import real answer histories, exported records, browser profiles, or
  textbook photos into test fixtures or browser state.
- Do not store production tokens, recipient addresses, records, or photos in
  shared environment settings, commits, PRs, logs, or test artifacts.
- `.gitignore` is a backstop, not a privacy filter. Review every staged path and
  diff; do not use `git add .` for work containing private inputs.

## Multiple agents

- Check available child-agent tools at task start when parallel work is requested;
  report any unavailability rather than claiming delegation occurred.
- Child agents share the filesystem and working tree. Give each agent distinct
  files or read-only duties; assign commits, setup, and integration to one agent.
- For concurrent independent tasks, use separate cloud task checkouts/branches.
  Do not share a browser profile or personal storage. Tests use ephemeral ports
  and fresh contexts; manual preview ports must be distinct.
- Use topic branches and PRs with the reason and validation. Apply the release
  scope above; infrastructure changes stay draft. Do not create permission-test PRs.
- Independent verification must inspect and execute the target revision, not rely
  on the implementer's report. If the runtime is unavailable, report unverified.
