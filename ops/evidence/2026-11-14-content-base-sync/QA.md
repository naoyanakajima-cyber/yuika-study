# Independent QA: CONTENT-MVP PR11 base compatibility repair

Disposition: **U1–U5 accepted on final commit; U6 external handoff pending coordinator.** No remaining blocking finding in the reviewed local candidate. This approves draft review readiness, not merge, deployment, publication, real data, or real notification use.

Final product HEAD: `f1e84a7b998dfbcd71c6692974015bdd08e1877e`.
Fixed main: `86514eda054a5a2e09204df3a0668e40624c16de`.
Original PR11: `3d2ed2f9a62673d2fb086a360ae841096f35b63e`.
Checkout: `/workspace/yuika-content-base-20261114`.
Reviewer: independent `qa_content_base_sync`, read-only product access; no product edits, push, PR mutation, deployment, permission changes, or new agents.

Read PdM U1–U6, Engineer report, product AGENTS/README/cloud documentation, operations AGENTS/team instructions, and the PrM-approved PdM parent-boundary addendum. Root confirmed fresh canonical remote operations HEAD/lease verification. The addendum expands the original 13-path limit to exactly 15 paths, adding only `tests/parent_mode.py` and `scripts/parent/embed.py`.

## Acceptance findings

| Condition | Disposition | Independent evidence |
| --- | --- | --- |
| U1 history/diff | Accepted | Both fixed original heads are ancestors. Final main-relative diff is exactly the approved 15 paths; all eight original CONTENT added blobs retain original PR11 object IDs. README preserves main plus original CONTENT explanation. |
| U2 preview | Accepted | serve.py is main plus one allowlist entry. Fullsuite directly checks seven HTML and three asset responses against file bytes, no-store, connect/form/object CSP, HEAD 405, private/directory/unknown/traversal paths blocked, and browser CSP rejection with POST arrivals zero. Loopback bind remains unchanged. |
| U3 CONTENT behavior | Accepted | Both unchanged CONTENT suites pass synthetic text/image, validation/repair, unresolved withholding, revision increment/all-confirmation invalidation, imported confirmation invalidation, per-question confirmation, whole-proposal cancellation, draft/confirmed JSON, guidance and keyboard/focus at 768×1024. No new scoring or trial-answer state exists. “個別確認/取消” means individual confirmation plus whole-proposal cancellation under original C7; no per-question cancellation feature is claimed. |
| U4 current main preserved | Accepted | Every tracked path outside the approved 15 is identical to fixed main, including all six current app HTML, assets, runtime, grading, selection, IDs, storage/history and notification implementations. All original CONTENT eight files are unchanged. No parent runtime/UI is added to CONTENT. Parent browser-test body after class Quiet is byte-identical to main; original static app assertions remain and marker count/order checks strengthen malformed-entry failures. |
| U5 executed proof | Accepted | Final fixed clean HEAD independently passes all 24 suites, exit 0; original 22 runner calls/order/seed/aggregation/failure propagation remain with only two CONTENT calls added. Additional isolated negative/idempotence probes pass. Complete per-suite log and metadata retained. |
| U6 handoff | Pending; not locally accepted | Coordinator owns fresh remote HEAD/lease checks, normal branch push, same PR11 draft/base/body readback, conflict/diff reconciliation and ceo_wait. No such external write was performed by QA. D04 direction does not authorize merge/deploy. |

## Blocking finding resolved, initial evidence preserved

Initial invocation started at `2f5cb14fd8ab3711752e725536288da47bf0d90e`, clean. It reported 23/24 pass, exit 1, runner 252s (wall 251.864s), 2026-11-14T17:11:54.793535+00:00 to 17:16:06.657826+00:00. `tests/parent_mode.py:11` failed with IndexError because its root `*.html` glob treated preserved memory-only CONTENT as a learning app with parent boundary markers. This was a deterministic integration contract mismatch, not flaky behavior. The suite continued and both CONTENT suites passed.

Coordination limitation: the Engineer committed the two-file repair at 17:16:05 before the first invocation finished. Initial post-HEAD was final `f1e84a7...`, clean. Therefore attempt 1 is a **mixed-HEAD diagnostic run, not fixed-revision acceptance evidence**. Its failure source and unchanged remaining scripts are identifiable, but its success rows were not used to accept the final commit. Root acknowledged this sequencing error. The final second invocation ran after the code freeze with identical clean pre/post HEAD.

The reviewed correction limits the exception to exact `content-review.html` plus original reviewed SHA256 `586e626a6759a3c1000f2ec50785627081569df75a71178e6d17482f948b030d`. All six learning apps remain required; unknown markerless HTML fails. CONTENT additionally has static memory-state/no-storage/no-parent/no-external-script/CSP checks. The generator validates the CONTENT digest before any HTML write and excludes only that known file; other generation behavior remains unchanged. A future CONTENT change must re-review the pinned exception.

Independent probe used a fresh temporary copy, never the product checkout, and verified:

- Final source identity and unchanged main parent-browser body.
- All seven tracked HTML files byte-identical after one generator execution.
- Unknown markerless HTML rejected by the actual static test prefix.
- Tampered CONTENT rejected by both static test and generator; generator rejection occurs before any HTML byte changes.
- Final product HEAD and clean state preserved.

Probe source: `/tmp/yuika-content-base-qa-probe.py`; results/source hashes: `/tmp/yuika-content-base-qa-probe.json`. These are supplemental correctness probes, not fullsuite reruns. There were exactly two fullsuite attempts, with cause diagnosis and approved repair between them; no third attempt.

## Final execution

Command: `bash scripts/check_all.sh`.
Start: 2026-11-14T17:17:17.175128+00:00.
End: 2026-11-14T17:22:08.794453+00:00.
Runner total: 291 seconds; wall time: 291.619 seconds; exit: 0; 24/24 suites passed.
Pre/post HEAD: `f1e84a7b998dfbcd71c6692974015bdd08e1877e`; both `git status --short --untracked-files=all` empty.
Browser RNG seed: 20261110; PYTHONHASHSEED: 0.

| Suite | Exit | Seconds |
| --- | ---: | ---: |
| tests/onin_review.py | 0 | 5 |
| tests/kamakura_review.py | 0 | 4 |
| tests/cloud_preview.py | 0 | 2 |
| notifications/test/worker.test.mjs | 0 | 0 |
| notifications/test/browser.py | 0 | 12 |
| tests/cloud_bootstrap.py | 0 | 2 |
| tests/adaptive_practice.py | 0 | 2 |
| tests/adaptive_daily.py | 0 | 4 |
| tests/adaptive_quality.py | 0 | 5 |
| tests/flash_grading.py | 0 | 8 |
| tests/spaced_daily.py | 0 | 5 |
| tests/history_compat.py | 0 | 4 |
| tests/science_adaptive.py | 0 | 8 |
| tests/registered_answers.py | 0 | 3 |
| tests/history_review_regression.py | 0 | 3 |
| tests/state_review_regression.py | 0 | 6 |
| tests/prototype_storage.py | 0 | 8 |
| tests/focus_data.py | 0 | 0 |
| tests/focus_practice.py | 0 | 14 |
| tests/parent_mode.py | 0 | 22 |
| tests/design_c.py | 0 | 22 |
| tests/responsive_subjects.py | 0 | 145 |
| tests/content_review.py | 0 | 4 |
| tests/content_guidance.py | 0 | 3 |

Final complete stdout/stderr: `/tmp/yuika-content-base-qa-test-attempt2.log`.
Final timing/HEAD/dirty metadata: `/tmp/yuika-content-base-qa-meta-attempt2.json`.
Initial complete stdout/stderr and metadata preserved at `/tmp/yuika-content-base-qa-test.log` and `/tmp/yuika-content-base-qa-meta.json`.
Initial static evidence: `/tmp/yuika-content-base-qa-static.json`; final scope/ancestry/blob/source identity proof: `/tmp/yuika-content-base-qa-probe.json`.
Final log SHA256: `748038b557989a47ea8f0aa1e5e162c41e10ec5759afc1c4bcdba69809692739`.

## Measurement limits

- Chromium automation only. CONTENT uses fresh browser contexts, synthetic fixtures and 768×1024 viewport checks, including overflow/focus. This is not Safari/WebKit, actual iPad, human/child trial, full visual inspection, or public production verification.
- CONTENT route guards allow only its loopback document GET; unexpected requests are recorded and aborted, with zero observed requests and zero probe POST arrivals. Storage zero means instrumented Storage.setItem/removeItem/clear calls during tested CONTENT interactions, excluding fixture seeding. Static source checks support the narrower no-learning-storage contract; they are not a universal proof for arbitrary future JavaScript. Reload fixture setup re-seeds sentinel keys, so preservation after reload alone does not establish storage isolation.
- Fullsuite notification behavior uses intercepted synthetic browser endpoints or injected/stubbed Worker fetch, never real notification delivery. Existing suites fetch public CDN JavaScript using verified HTTPS GET. Accordingly no all-suite “external traffic zero” or “all storage writes zero” claim is made; synthetic learning/persistence tests intentionally write isolated browser storage.
- The ignored `.venv` symlink reuses `/workspace/yuika-pr26-fix-20261112/.venv`, activated by the runner. This is manually prepared runtime reuse, not evidence of automatic Install/Start success.
- Original content-spec historical observations remain original PR11 content. Do not present those old observations as a current-main survey. Public release remains outside this QA.
