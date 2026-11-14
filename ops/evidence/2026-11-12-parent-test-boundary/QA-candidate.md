# Independent QA: deterministic parent-mode fixture

Candidate df791c07c0071921e22ae667e5230f8fd99ed782; parent042c55dd04a285277dc3dfa9dd296f161283e809. Reviewer qa_parent_test_boundary is separate from Engineer engineer_parent_test_boundary. Checkout /workspace/yuika-parent-test-fix-20261112 remained clean and HEAD unchanged before/after tests. No edits, commit, push or external message by QA.

## Result

Passed scoped review and one complete `bash scripts/check_all.sh`: exit0,21/21 suites,163seconds. Parent-mode suite25seconds. Worker9/9 and bootstrap13/13. No retry of the full suite. Log: candidate-check-all.log. Prepared prior venv/Chromium reused; no dependency installation. Fresh browser contexts and synthetic data/mocked notifications only.

## Diff and acceptance

Only tests/parent_mode.py changes. The fixture document is explicitly fulfilled at a unique same-origin URL with script-free HTML. The test asserts YuikaParent/YuikaReports are absent there, inserts synthetic configuration and pending work before app startup, checks pending status and zero observed requests, then opens the actual application directly with parent-check=1. No normal app mount can read the newly inserted fixture during this preparation.

All original zero-notification, child-storage preservation, parent sandbox answers/reload, fresh-tab isolation, mode exit, normal-mode mock-send positive control, cleanup/rollback and denied-storage assertions remain. The calls collection is not reset or filtered. Request diagnostics now retain phase and document URL. No production notification/runtime code, grading, question selection, storage schema or CSP was changed. `git diff --check` passed.

The related deterministic diagnosis used a real held Web Lock to make the old test preparation send a pending synthetic request while fetch-time active=false; inert preparation sent0 through parent entry/reload/triggers and left childraw intact. See QA-diagnosis.md, boundary_probe.py and boundary-results.json. That probe had one initial UI harness timeout on a collapsed retry control, then one corrected success; not an application failure.

## Historical distinction and limits

The old baseline8100285 full run remains20/21 with an uninstrumented mock-request assertion failure. Its exact original request phase is still not recoverable. This cycle proves and removes a concrete fixture scheduling race and confirms all21 suites pass on the fixed candidate; it does not relabel the earlier run successful or conclusively assign its event to the race. Current test repeatability evidence is one independent complete run plus separate Engineer focused run, not repeated independent runs.

Chromium only. Safari/WebKit, real iPad, CEO hands-on usability, merge/publication and real notification delivery are not verified or authorized here. Technically suitable for draft review, not production approval. During this verification, the coordinator observed PR25 externally merged at06:14:55 with head042c55d into main25cad059f73cdca4cd805825c84e6619074b37c4. That observed merge does not include candidate df791c0. The candidate remains a separate handoff pending review; a now-closed PR25 cannot be updated with it. The coordinator will preserve the topic branch and patch through the existing operations draftPR9 without creating another product PR. These remote-state/hand-off facts are coordinator observations, not independent GitHub verification by this QA. Further identical test repetition is unnecessary without new evidence.
