# Cycle34 Engineer: readable synthetic triangle image trial

- Frozen commit: `1678519f916471ba6e38044855de240bd6c4a807`.
- Parent: `d75a5469fbf1e8c5011a6307308546e5ec669ceb`; current main retained from that merge is `60d1a946cc02ed8acea54c0d7af7d6451fcc30ec`.
- Checkout `/workspace/yuika-content-image-trial-20261115`, branch `codex/content-image-trial-20261115`.
- Commit time 2026-11-15T10:09:36Z; clean status observed immediately after commit. Freeze notified root and independent QA; no further product editing.
- All accepted scope is from `/tmp/yuika-cycle34-PdM.md`, PrM adoption and canonical product spec at ops commit bdceb98. Product spec includes the seven acceptance requirements and PrM adoption; independent final acceptance is recorded separately by root.

## Changes and value

Added one synthetic, hand-authored explanatory triangle SVG and one draft short-answer question. The readable source says 三角形の辺は3本です。; its intentionally unresolved transcription uses ［確認待ち］ and resolution=null. The UI explicitly explains this is a manual reconciliation exercise, not OCR output. A parent-role tester can inspect the source, edit transcription/resolution, explicitly confirm the proposal and check answers in the existing memory-only trial.

New button `sample-triangle` uses existing unsaved-discard handling. Source lookup changed from the single image value to a compile-time ASSETS array with exact kind/sourceId/locator matches. Rendering uses only the matched trusted content, never imported SVG, URL or arbitrary locator. Old text/image samples and fixtures retain their exact data; unknown references remain editable proposals but cannot display a trusted source, confirm or start trial.

New fixture source triple: image / synthetic-triangle-source / synthetic-triangle-source.svg. Source region: page:1;region:100,60,400,220, surrounding the complete triangle and explanatory sentence. Draft package/question/unit IDs are isolated from learning IDs. Generated fields remain prompt/explanation/hint; quote and candidates remain after resolution.

README explains the manual flow. Product spec documents accepted scope and independent QA requirements. New `tests/content_image_trial.py` is added to check_all (30 unique suites). Existing content_review assertions were extended to compare all three full sample objects and exact trusted source triples/content; no prior negative assertion was removed. Parent embed/test hash changed only to the new HTML hash:
`b978ea0ebd725cbe0b0b45275ad19d7be4ee78e64fb5c7e40947fe05475560f4`.

## Engineer checks completed

- `source scripts/cloud/activate.sh; python tests/content_image_trial.py`: first attempt exit0. Evidence image-trial.log.
- New UI regression covers 768x1024 fresh context; keyboard entry and confirm/focus; unsaved discard dismissal; unresolved/unchecked gates; revision changes; manual transcription+resolution; retained quote/candidates; answer3 match and answer4 mismatch; editor hidden/inert and runtime edit/export blocking; exit clears trial but preserves proposal/confirmation/unsaved; draft and confirmed JSON roundtrip keeps schema1 and clears confirmation; edit revokes confirmation; old/new image and old text switches/imports; all source triple mismatch cases including URL reject; no storage/history/cookie/indexedDB writes or unexpected network/page errors.
- `source scripts/cloud/activate.sh; python tests/content_review.py`: first attempt exit0; C1-C11 existing synthetic workflow, external requests0/POST0/storage writes0. Evidence content-review.log.
- `/tmp/yuika-cycle34-engineer/static-check.py`: exit0. JSON evidence static-check.json. All97 existing files outside the six intended tracked modifications exactly match base, including current-main seven learning HTML/assets/recall/history/runtimes, old fixture files and other tests.
- CSP meta, entire shape validator, and all code from setImportPending through complete trial engine exactly match base. No new persistence/network calls. New SVG contains no script/image/href/foreignObject/external resource. Parent embed/test modifications are hash value only. Runner retains prior29 and adds exactly one suite.
- Isolated temporary-copy parent generator replay leaves all8 HTML unchanged; unprotected synthetic unknown HTML rejected by parent preflight, then protected by existing generator and accepted; mutated content hash rejected before any HTML writes and by preflight. Product checkout was not regenerated.
- Visual inspection using trusted loopback preview at768x1024: triangle, three side numbers, explanatory sentence and synthetic/OCR warning readable and inside viewport. Evidence triangle-preview.png and triangle-768.png under temporary evidence directory only.
- `git diff --check` and staged diff check passed. Final clean HEAD/status evidence included.

## Preparation, failed attempt and limits

AGENTS.md, README.md and docs/codex-cloud.md read. Existing requirements matched `/workspace/yuika-pr26-fix-20261112/requirements-dev.txt`; manually reused verified venv via ignored `.venv/bin` link and activated each test shell. This is manual reuse, not automatic snapshot handoff proof.

One optional screenshot navigation to file:// was rejected with ERR_BLOCKED_BY_ADMINISTRATOR. Cause was unsupported direct local-file browser navigation. No policy/settings changed or escalation attempted; used the documented loopback PreviewHandler instead and successfully captured/inspected the image. Product tests did not fail; no blind retries.

Full mandatory30 suites and independent fixed-HEAD visual/trust-boundary review are owned by separate QA, not claimed here. Engineer checks are Chromium-only and do not establish Safari/WebKit/real-iPad compatibility, learning efficacy, production adoption or deployment. No auto semantic matching/new grading/schema/storage rule. No real inputs, OCR service, private data, main modification, push, ops edit, real notification, permission/configuration/secret change or deployment.

Evidence directory: `/tmp/yuika-cycle34-engineer/`. Next action: QA independently verify exact clean1678519; root records results and integrates only after checking lease/execution ownership. No product edit after freeze unless root stops QA and authorizes a concrete repair.
