# REV-COMPAT-FIX independent QA

Reviewer: `/root/qa_isolation_fix` (separate from Engineer). Observed 2026-11-10 15:18–15:22 UTC. Product HEAD `408805b06092b9eec5971426a8a1c2cb45194620`, based on PR20 `c5c6c15c4968ee3d04f8a43f273f12bbb3b9b81e`. Product checkout `/workspace/yuika-review-storage-isolation-20261111`. QA made no product edits, commits, pushes, or external posts.

Verdict: the preventive storage-isolation candidate passes the scoped H1–H7 checks for the four detailed-history pages and the index previous-unit entry. This is synthetic draft evaluation, not a production approval, historical-data repair, product integration, or proof of real learning effectiveness.

## Execution evidence

- `bash scripts/check_all.sh`: exit 0, 17/17 suites, 106 seconds. Worker 9/9 and bootstrap 13/13. All existing 16 suites plus `prototype_storage.py` ran once at this final HEAD; no skip introduced.
- `source scripts/cloud/activate.sh; python /workspace/work/isolation-qa-20261111/probe.py`: exit 0, independent four-page probe. Fresh 768×1024 Chromium contexts and loopback preview with CSP preserved. POST attempts 0, POST arrivals 0, external requests 0, page errors 0.
- `source scripts/cloud/activate.sh; python /workspace/work/isolation-qa-20261111/access_recovery_probe.py`: exit 0, observation-only baseline comparison; it records the existing read-access recovery limitation below rather than asserting successful recovery.
- Post-run HEAD unchanged, `git status --short` empty, `git diff --check` exit 0. Existing history generation during mandatory tests left no product changes.

The Engineer reported an earlier new-test harness failure (restoring a native Storage function as a Playwright evaluate return value caused Illegal invocation), corrected by a void wrapper. It preceded this frozen candidate. Both independent QA test commands passed on their first runtime attempt; no assertion was weakened to get a pass.

## Contract checks

| Condition | Evidence |
|---|---|
| H1 old raw/other units preserved | Mandatory actual UI answering/grading/save/reload suites plus independent original bytes sentinels across all four pages. Original per-unit keys, other-unit keys, old aggregate, old preferences and last-unit remain unchanged. |
| H2 same-origin older reader roundtrip | Independent exact old PR10 `ba829a1176ff1ead7d312526890afe8792178c99` → candidate → old PR10 → candidate at the same URL/origin. Old original-only history remains readable; trial answer remains after returning to candidate. Science old fixture includes its original aggregate to avoid triggering the old app's own unrelated auto-copy. |
| H3 old/trial corruption separation | Independent malformed old raw leaves trial usable; malformed trial raw blocks saving and is preserved. New suite additionally verifies empty-string invalid raw blocks saving and downloads as exactly zero bytes, plus original raw download and quota failure. |
| H4 explicit envelope and atomic import | Real browser JSON download → remove only trial KEY/reload to zero → upload exact bytes → exact event equality including questionVersion → duplicate import remains one. Unknown envelope/event field/questionVersion rejected without changing saved raw; rejected raw actually downloaded intact. New suite adds unknown ID/mode, same-ID conflict and strict science aggregate envelope rejection. |
| H5 all write paths/entry/retry | Existing normal/adaptive/daily/science suites, actual file import, quota retry, index previous-unit entry; independent cross-tab valid merge and invalid-raw blocking. Static writer inventory confirms four-page answer/settings writes use prototype KEY/PREF namespace; notification workflow is unchanged and measured separately. |
| H6 viewport/communications/clarity | Fresh 768×1024 contexts, CSP maintained, normal probe zero POST or external requests; mandatory notification suite uses only a mocked endpoint. Screenshot manually inspected: synthetic-only/old-vs-trial history notice is visible in the home page capture. |
| H7 exact final SHA/regression integrity | All 17 suites and independent probe at final SHA. Archive immutability and historical grading/version cases passed. Existing test deltas switch storage names or envelope payload and remove invalid extra reflection fields only for schemas that never define them; existing assertions remain and no skip was added. |

## Existing limitation discovered independently

Science initial `localStorage.getItem` access refusal sets `blocked=true, rawBroken=null`. After access is restored, `persist()` remains false because its existing guard rejects any blocked state. This occurs identically in base PR20 and final candidate. It did not overwrite storage, is not a new isolation regression, and does not invalidate the successful quota-after-write retry tests. Record a separate follow-up for recovery UX; do not claim every transient storage-access scenario is repaired by this draft. `access-recovery-result.json` contains both observations. Reproduction: serve the science HTML for each compared SHA with the same CSP; in a fresh context, inject a getItem wrapper that throws only for the science detailed-history KEY; navigate and observe blocked=true/rawBroken=null; restore the original getItem; call persist(), which returns false and leaves stored=null. No product patch was made for this separate issue.

## Limits

No real answers/photos, Evernote, email/Drive content, real notification endpoint, Safari/iPad hardware, production merge, deployment, or settings/permissions change. Existing mixed old-history data is deliberately neither migrated nor repaired. Old readers do not display prototype answers. The existing venv was reused; this is not an automatic environment-bootstrap validation.

## Artifacts

- `check_all.log`: SHA256 `4de4b7293100d6aee084cc11568f8bb30c215e46489657e9013cda9a8b83b8f3`
- `probe-result.json`: SHA256 `4311b783080513bf4a80b7054ac3c33816f4c524728eb74b856c544656bc173c`
- `onin-prototype-home.png`: SHA256 `08207aae52adf390855245ea302ce0583bbdfb6a11c3f59b417df860ba31011c`
- `probe.py`, `probe.log`, `access_recovery_probe.py`, `access-recovery.log`, `access-recovery-result.json` contain synthetic-only reproduction evidence.

Next: coordinator rechecks lease and remote PR20 head before integrating this candidate and evidence into the existing draft; track the existing science access-recovery limitation separately. No CEO production approval is inferred.
