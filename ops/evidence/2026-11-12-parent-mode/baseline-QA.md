# PR24 independent QA — baseline

Reviewer: qa_parent_mode (independent from implementation).
Reviewed commit: `0d6827962b35ed24ccdbdd8f56e8dafca06f240a`.
Cloud checkout: independent worktree; clean before/after. Existing repository setup procedure was run manually by coordinator, not automatic snapshot inheritance evidence.

## Executed

- `bash scripts/check_all.sh`: all 20 suites exit 0, 145 seconds, including Worker 9/9 and bootstrap 13/13. Full log: `check-all.log`.
- `probe.py <checkout>`: fresh Chromium contexts, synthetic storage only, external requests blocked. Two failure causes reproduced (normal/parent startup denial and partial multi-key cleanup). See `probe.log` / `probe-result.json`.
- `mailto-probe.py <checkout>`: parent mode, synthetic parent address, real ten-question UI flow. `window.open` replaced with an in-page spy before app execution; no mail application opened and no real message sent. One mailto handoff attempted. See `mailto-probe.log` / `mailto-result.json`.

## Findings — changes requested

1. **P1 — storage boundary initialization can abort.** `scripts/parent/runtime.js:6` reads sessionStorage without catching SecurityError. Both normal URL and `?parent-check=1` throw, leave `YuikaParent` undefined and no parent banner. Every application persistence caller now depends on that boundary. Define a safe fail-closed boundary and explain unavailable session storage; never silently fall through to child localStorage when parent intent/previous mode cannot be established.
2. **P1 — cleanup can partially delete several collections.** `scripts/parent/runtime.js:45` commits each key independently. Injecting failure at the second key deletes the first collection, retains the second, and shows only a generic error. Preserve original bytes, preflight complete data, recover prior writes where possible, and expose honest partial-failure recovery if rollback itself cannot complete. Do not claim multi-key atomicity from localStorage.
3. **P2 — manual email handoff bypasses parent-mode guard.** `index.html` `sendEmail` / `sendFlashEmail` have no `suppress()` guard. In parent mode a synthetic quiz result still calls `window.open(mailto:...)`, contrary to the no-notification banner. This is an email composer handoff, not direct delivery. Guard both entry points and verify no handoff while preserving normal-mode behavior.

The baseline suite passing does not cover these failures. No application code was edited by QA. No real data, notification, deployment, merge, settings, permissions, or external comments were used. WebKit/Safari/iPad physical-device behavior remains unverified. These findings do not grant adoption/publication or permission to delete real records.
