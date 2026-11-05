# Cloud development

Read `README.md`, `docs/codex-cloud.md`, and instructions in affected subdirectories.
Use Codex Cloud; development must not depend on a local PC remaining online.

## Setup and verification

- Setup: `bash scripts/cloud/setup.sh` from the repository root.
- Each new shell: `source scripts/cloud/activate.sh`.
- Required checks: `python tests/onin_review.py` and `python tests/kamakura_review.py`.
- Preview safety: `python tests/cloud_preview.py`.
- Notification changes: `node --test notifications/test/worker.test.mjs` and
  `python notifications/test/browser.py` (mock API only).
- Preview: `python scripts/cloud/serve.py --port 8000`; use the cloud browser at
  `http://127.0.0.1:8000/`. It blocks notification APIs through CSP.
- Browser tests need loopback sockets and browser process execution. If the
  execution sandbox blocks sockets, use the supported additional network
  permission. Keep the environment's enforced outbound allowlist.
- Never weaken assertions, skip checks, disable TLS validation, or retry a failed
  test until it happens to pass. Diagnose failures and report remaining limitations.

## Notifications and private data

- Do not deploy, merge, publish, change production Secrets, or send real email/Chat
  notifications unless a subsequent task explicitly authorizes that action.
- Use fresh browser contexts and synthetic records only. Never import personal
  answer histories, exported JSON/TXT, browser profiles, or textbook photos.
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
- Keep meaningful code/dependency/CI changes on a topic branch and open a draft
  PR with the reason and validation. Do not create a PR solely to test permissions.
