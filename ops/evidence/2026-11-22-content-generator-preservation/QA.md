# Cycle191 independent QA — CONTENT branch generator preservation

Reviewer: `/root/qa_content_generator`, independent of implementation (`/root/engineer_content_generator`). Candidate `3920f1642692c88a8d6870480bc3f98f71558d24`, base PR11 `ee228ca0a1865d0a56f4302cd9342a4f66738561`. Detached cloud checkout `/workspace/qa-content-generator-checkout`. Existing verified `/workspace/yuika-study/.venv/bin` was manually reused through ignored `.venv/bin`; this is not evidence of automatic snapshot handoff. No product edits, push, notifications or private data.

## Outcome

**PASS — no blocking review findings.** Required `bash scripts/check_all.sh` ran once on the exact candidate: all 32 suites exited 0, total 318 seconds, overall exit 0. Checkout was clean before and after (including untracked files). `suite-result.json` records each exit/duration; `check-all-attempt1.log` is the complete fresh log. No product suite retry.

## Scope and source review

- `git diff` contains ten expected paths: branch-specific science adapter source, prototype runtime, its four non-science HTML copies, generator regression, check runner, lever roundtrip regression and compatibility documentation. No content HTML/fixture/contract changes.
- Science HTML is byte-identical to the old PR11. The new science source plus separator has the exact hash of that old embedded adapter; prototype source has the exact hash of the science embedded prototype. This preserves PR11's own `scienceDaily()` and does not import PR10's `scienceDailySources` implementation.
- Four other HTMLs each change exactly one field allowlist row, adding only `answerUnit` / `answerTag`. `scripts/prototype/runtime.js:3` sets `prototypeScience=typeof byId!=='undefined'`; lines 13–14 apply this row only in that branch. Read-only `rg byId` in those four HTMLs finds only the two `typeof` checks, no definition. Normal history fields are unchanged.
- `static-readback.json` records matching old/new SHA-256 for all sixteen CONTENT paths: HTML, six synthetic fixtures, five CONTENT suites and four specifications. The schema remains inside the unchanged HTML/fixtures/contracts. HTML fixed digest is `b978ea0ebd725cbe0b0b45275ad19d7be4ee78e64fb5c7e40947fe05475560f4`, also unchanged in parent embed/preflight guards. Science HTML and source/embedded hashes are recorded there too.
- Added generator test uses a temporary tracked-file copy and compares first pass against the original bytes, then the second against the first; source checkout is checked unchanged. Added lever regression uses an actual downloaded JSON file and file input into emptied trial storage. Documentation describes the actual implemented sequence.

## Independent generation and expected negative

`regeneration.py` ran all seven actual generators on a disposable archive of exact candidate: both first and second passes matched all original tracked bytes, all fourteen commands exit 0. The identical new regression test transplanted into a disposable old-PR11 checkout exited 1 as expected: `Generator pass 1 changed tracked files: ['yuika-review-v2.html']`. This negative confirms detection of the old regeneration loss; it is not a candidate failure. Evidence: `regeneration-result.json`, `regeneration.log`, `old-pr11-generator-negative.log`.

## Fresh synthetic UI probes

At viewport 768×1024, `content-probe.py` independently used a real synthetic science answer as the existing storage sentinel, then tested both bundled triangle-image and text flows. Unconfirmed starts were rejected; triangle transcription/resolution edits required explicit confirmation; trial answers graded without modifying proposal/confirmation/unsaved state or learning history; exit cleared trial state; actual export and file reimport reset every confirmation; subsequent edits invalidated confirmation; reload cleared ephemeral content work and preserved the science event. Instrumented CONTENT storage/cookie/history/IndexedDB/cache/service-worker writes: zero. CONTENT network requests/POST attempts and page errors: zero. Two attempted Google Fonts GETs from the science seed/readback were aborted. Evidence: `content-probe-result.json`, `content-probe.log`.

`science-probe.py` separately tested normal and parent mode. Real `lever-16` UI answer `25 cm` stored its actual unit/tag, survived reload, actual JSON download, empty trial storage, file-input import and another reload. An old event with both optional fields removed was accepted. Invalid unit, invalid tag and unknown field imports were rejected with submitted raw preserved and saved/events unchanged. Parent child storage was unchanged. POST attempts/page errors: zero; external font GETs aborted. Evidence: `science-probe-result.json`, `science-probe.log`.

Four inspected screenshots retained: normal/parent lever feedback, synthetic triangle source, triangle nonpersistent graded trial. Text graded screenshot was inspected but not retained to keep four artifacts. The image source clearly states synthetic data and no OCR; trial states no saved answers. No visual blocking issue observed within these limited flows.

## QA harness stops and limit

The independent static helper stopped twice due to QA-authored assumptions, not product failures: first expecting `allowed=` text on the changed field row; second expecting a pathname-based science predicate. Actual source was then read and all four diffs inspected. No third invocation of that static bundle. The failed helper is retained as `static-attempt2-stopped.py`; detailed reachability/reason is in `static-harness-stops.md` and `static-readback.json`. Still-unexecuted generator/negative checks were executed separately without weakening product assertions. The required product full suite was run separately once.

## Limits and next step

Synthetic review only; no real materials, real child answers, OCR, notifications or production deployment. This result supports the existing draft PR11 update and CEO decision; it is not CEO approval. Final integration/push/ledger and lease release belong to the coordinator.
