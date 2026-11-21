# Independent QA: PR #25 baseline

Reviewed HEAD: 81002855830dda7d2cac669f8297a0d81756872d; base: 6ec616d5f24f552306219e3177db4f4041f84428. Reviewer: independently spawned qa_design25 (not implementer). All browser data synthetic, fresh Chromium contexts, loopback preview and intercepted/mock network; no real notifications, private data, product edits or push.

## Outcome

Changes requested: new homepage summary accepts malformed record envelopes and invalid saved variants which corresponding unit rejects or defaults. All five units with `{events:[]}` or mismatched datasetVersion set unit blocked=true and disable its daily button, while the adapter returns unavailable=false and normalCount=5. Actual homepage shows zero review/weak counts plus five ordinary questions and 0/30 completed for Onin; clicking reaches disabled daily action and preservation notice. Original raw remains unchanged. Screenshot: corrupt-home.png. Evidence: probe-baseline.json, selection-baseline.json, probe-baseline.log, scripts probe.py and selection.py.

Saved unsupported variants are accepted only by adapter: Heian yomi and mock-focus kanji/yomi; actual unit defaults normal. Eighteen settings/selection cases exercised: fifteen legal configurations agree with actual engine and actual button session length (including count10/15, course, unit, kanji/yomi where supported); three unsupported configurations disagree. Daily-five label remains existing product terminology with explicit actual-count explanatory text, not a newly introduced blocking defect by itself.

Valid future-dated records suppress summary (unavailable=true); read-refusal returns null. All five parent-mode pages use empty isolated summary and leave child storage unchanged. All malformed raw preservation checks pass. Detailed invalid event contracts need repair regression and independent candidate review.

## Tests

Exactly one `bash scripts/check_all.sh`: exit1, 146s, 20 of 21 suites pass. parent_mode.py first Onin case fails line88 `assert not calls` with one intercepted mock `/reports` request. Original test lacked timing/stage information; root cause unproven. Do not report full suite success.

One isolated second parent_mode attempt with instrumentation (no assertion removal): exit0, all six entry pages, reload/exit/notification guards, cleanup/rollback, temporary storage mode pass. All recorded mock requests occur with active=false and report id normal-mock-report after parent exit. This does not establish the cause or dismiss the initial failure. No third attempt without relevant change. Logs: check-all.log, parent-rerun.log; instrumented copy parent_mode_instrumented.py.

## Static review

Existing test assertions changed for UI location/label, preserving storage/isolation/regression coverage. History remaining-count check now checks actual candidates plus current completed display. Parent exit wait adds presence guard only. Google Fonts stylesheet remains aborted in science probe; it is excluded only from unexpected-external collection. No source changes to scripts/practice/adaptive.js, science review projection, scripts/parent/runtime.js or Worker; notification client only replaces recipient text. Preview allowlist adds exactly three shared static assets. New generator extracts existing review projection; validation boundary issue above is new adapter behavior. Test diff saved as test-assert-diff.txt.

No CEO design adoption or production approval inferred. Safari/WebKit and real device usability untested.
