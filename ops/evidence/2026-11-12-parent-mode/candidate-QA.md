# PR24 independent QA — candidate

Reviewer: qa_parent_mode, independent from Engineer engineer_parent_mode_fix.
Candidate: `314aa13216b8bce5fee65959b9fa51d925575234`.
Baseline: `0d6827962b35ed24ccdbdd8f56e8dafca06f240a`.

The baseline passed 20 suites but three independent failure probes required changes: sessionStorage denial aborting the boundary, partial cleanup failure, and a manual mailto handoff in parent mode. The candidate diff was reviewed directly, including the shared boundary and generated copies, both mailto handlers, app navigation, recovery export, tests, and README limitations.

## Independent additional evidence

`probe.py <checkout>`: 9 cases passed on first execution.

- Session read denial on normal and parent URLs, and session flag-write denial on a parent URL: boundary remains defined, parent mode and notice remain visible, cleanup stays disabled; five actual UI answers stay in isolated memory, child raw value unchanged, no page error or external request.
- The same three first-load denial cases with storage recovered on reload: parent intent persists, subsequent writes stay isolated from child storage.
- Cleanup second-key failure with successful rollback: all original bytes restored and no false success.
- Cleanup rollback itself fails: honest partial-recovery warning, additional deletion blocked, downloaded original JSON exactly matches pre-cleanup bytes.
- Concurrent-write simulation during rollback: newer value is preserved rather than overwritten; original backup remains available and additional deletion blocked.

`mailto-navigation.py <checkout>`: 6 cases passed on first execution.

- Quiz and flash parent mode: no mailto handoff. Normal mode: exactly one expected handoff each, intercepted by an in-page spy. No actual mail program launch or sending.
- First-load temporary storage denial then navigation through an existing home anchor and the daily-five button: destination recovers working sessionStorage but remains in parent mode, with child raw unchanged.
- Flash uses a one-card synthetic deck routed in-memory to keep the test scoped to the actual result-screen/email handler; the full suite separately checks original deck/grading behavior.

All tests use fresh Chromium contexts and synthetic data. QA edited no product code and performed no push, merge, real notification, deployment, settings or permission change. The worktree's dependencies were prepared manually, not proof of automatic snapshot inheritance.

## Limits

Storage operations across several keys are not transactional. Rollback can fail and requires keeping the page open to export the original bytes; the UI now says so instead of reporting completion. The backup format is an original-byte recovery artifact, not an automatically applied migration. The selected timestamp cleanup still needs separate product-adoption/user-use judgment. Safari/WebKit/iPad hardware and real personal histories remain untested. No release or adoption approval is inferred.

## Final result

**PASS for the scoped draft repair** at `314aa13216b8bce5fee65959b9fa51d925575234`.
`bash scripts/check_all.sh` completed once on the candidate: **20/20 suites exit 0, 209 seconds**, Worker 9/9, bootstrap 13/13. `git diff --check` passed and the worktree remains clean. Full results are in `check-all.log`.

The additional 15 independent cases also passed on their first candidate executions. No remaining blocking defect was found in this scoped repair. This technical result is not CEO adoption, permission to delete real records, merge, publication, or Safari certification.

## Viewport / controls

The three initial storage-denial cases above used **768×1024** and completed five actual responses each. An additional focused 768×1024 Chromium check (`viewport.py`) passed: expanded parent banner is 768×362, exit/date/count/delete controls all remain within the viewport, no horizontal overflow, zero-record count disables deletion, and keyboard Enter on Exit clears the parent banner and returns to normal mode. Exit/count/delete control heights are 48px; timestamp input is 50px. This is geometric visibility and basic keyboard operation, not a full accessibility or iPad hardware audit. Total independent additional checks: **16**, all first execution pass.
