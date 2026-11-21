# Independent QA: parent notification fixture boundary

Reviewer: qa_parent_test_boundary. Product examined: 042c55dd04a285277dc3dfa9dd296f161283e809 (existing PR25). Read-only product checkout; no product edits, commit, push, external messages, private records or real notifications. Prepared existing Chromium/venv reused after activation; no dependency installation. All browser contexts fresh and data/endpoint/token synthetic; every external request intercepted or aborted.

## Evidence and causal limit

Previous full-suite failure was at parent_mode.py `assert not calls`, with one mocked /reports URL but no timestamp or active-mode evidence. Previous isolated second attempt passed and only recorded normal-mock-report after parent exit. Those logs cannot conclusively identify the phase of the original 05:14 request.

Static code shows mount() calls flush(); flush() checks suppress(), then awaits navigator.locks.request before process() reads config and pending jobs. The test first loads a normal application, then inserts enabled configuration and a pending fixture, then navigates to parent mode. The lock callback may therefore process newly inserted fixtures while still in normal mode.

A deterministic browser probe used an actual same-origin Web Lock held by a sibling page to delay that existing mount callback. It did not replace process(), suppress() or fetch behavior. After the main page loaded normally and one pending lock request was verified, the probe inserted the same kind of synthetic fixture and released the lock. Exactly one intercepted request was observed. A fetch-time wrapper recorded `YuikaParent.active=false`, normal Onin URL and synthetic-pending report ID. Only after acceptance did the probe enter parent mode; the new parent page made zero fetches. The original test's accumulated `assert not calls` would fail despite no parent-mode request.

A separate fresh context seeded identical preexisting configuration/pending work on a script-free same-origin fixture document, then directly entered parent mode. Parent entry, online/visibility events, enqueue, connection form submission, manual retry and reload made zero intercepted requests; child localStorage remained byte-for-byte identical and parent sandbox could not read the child pending key.

This proves a concrete race in the test preparation and a deterministic way to remove that race. It does not retroactively prove the cause of the uninstrumented original event or establish absence of every possible product bug.

## Execution

- boundary_probe.py first attempt: final retry button click timed out because its enclosing details was closed; preceding normal-mode scheduling assertions had passed. This was a probe UI setup error, not a product failure.
- Second attempt: opened the enclosing details before clicking; exit0. No further retry. Both targeted scenarios passed. Artifacts: boundary_probe.py, boundary-results.json, boundary-attempt2.log; first failure retained in boundary.log.
- No full-suite repetition and no product test execution besides this targeted probe at this stage.

## Recommendation

Have a separate Engineer seed parent_mode.py fixtures in an inert same-origin document before the first app load. Keep the pending job present before entry; retain every zero-request, raw-preservation, reload, normal-mode-after-exit and cleanup assertion. Do not clear calls, ignore setup requests, disable application guards, or change product notification logic. Independently execute the resulting parent_mode test and inspect its exact diff before accepting it. Historical initial failure remains as historical evidence; current candidate results must be reported separately.
