# Cycle35 independent QA — theme/current-main compatibility

**Scoped acceptance PASS; product blocking findings 0.** Independent reviewer `/root/qa_theme_compatibility`, separate from Engineer. Fixed HEAD `9fc4bbf3e6c72e09327b6610338f12937fc7aba5` remained clean before/after and at final verification `2026-11-15T11:14:32.198806+00:00`. Parents retain PR12 b416d3c and main60d1a94. New CEO approval read0; this is verification of a draft candidate, not adoption/merge/publication authorization. C8 coordinator PR/ledger persistence remains pending.

## Actually executed mandatory checks

`bash scripts/check_all.sh`, attempt1, **26/26 exit0, 319 seconds**, completed 2026-11-15T11:12:44.784353+00:00. Source scripts/cloud/activate.sh used; matching requirements and existing verified venv were manually reused. This is not automatic snapshot handoff success. Existing23-suite results and Engineer focused results are not counted as this execution.

| Suite | Exit | Seconds |
|---|---:|---:|
| tests/onin_review.py | 0 | 4 |
| tests/kamakura_review.py | 0 | 4 |
| tests/cloud_preview.py | 0 | 1 |
| notifications/test/worker.test.mjs | 0 | 1 |
| notifications/test/browser.py | 0 | 10 |
| tests/cloud_bootstrap.py | 0 | 2 |
| tests/adaptive_practice.py | 0 | 3 |
| tests/adaptive_daily.py | 0 | 4 |
| tests/adaptive_quality.py | 0 | 4 |
| tests/flash_grading.py | 0 | 8 |
| tests/spaced_daily.py | 0 | 5 |
| tests/history_compat.py | 0 | 4 |
| tests/edo.py | 0 | 16 |
| tests/medaka.py | 0 | 17 |
| tests/microscope.py | 0 | 24 |
| tests/science_adaptive.py | 0 | 7 |
| tests/registered_answers.py | 0 | 3 |
| tests/history_review_regression.py | 0 | 3 |
| tests/state_review_regression.py | 0 | 4 |
| tests/prototype_storage.py | 0 | 8 |
| tests/focus_data.py | 0 | 0 |
| tests/focus_practice.py | 0 | 12 |
| tests/parent_mode.py | 0 | 21 |
| tests/design_c.py | 0 | 21 |
| tests/responsive_subjects.py | 0 | 120 |
| tests/theme_review.py | 0 | 13 |

## Independent review and measured boundaries

- C1/C7/static: exactly5 expected files differ from main: README, theme spec, kamakura HTML, mandatory registration, theme test. All other tracked files equal main, including other HTML, shared assets, parent runtime, history archive and CSP-bearing documents. Kamakura script blocks other than the inserted theme IIFE equal main byte-for-byte: problem IDs/answers/validators/keys and new recall retention/prototype lines are retained. Theme patch equals old PR12's patch; theme test equals old PR12 byte-for-byte. Registration is exact main25 plus theme_review. No unmerged PR10/11 difference was imported. `git diff --check` passes. Generator parity was Engineer execution, separately reported; not counted as QA execution.
- C2/C6: six current synthetic images were captured at768x1024 and actually viewed by QA: standard/kamakura home and both diagram screen/print crops. Theme selection and home text are visible, diagram labels legible without clipping in these images. The two permitted C2 exception boxes retain white13px labels and exact figure DOM; current computed background rgb(143,79,60), label contrast **6.265720821251096** in both themes and screen/print (8 measurements). This is current measurement, not prior cycle25 data. Print hides theme UI, uses white body and restores saved choice. Actual keyboard Tab+Space focus is visible, offset3px, contrast **5.509170074497065**. Controls >=44px and gap>=8 passed before partial probe exit. Full theme/responsive suites verify their configured overflow/width assertions.
- C3/C4/C5: supplemental normal and parent five-question runs compare run/data/prefs/main DOM/input/notice/blocked/dirty across standard↔kamakura at input/selection, first hint, grade and result. Normal result enqueue calls0; parent result enqueue calls0 and child's complete localStorage unchanged. Theme write denial leaves learning warning intact; one answer still persists, then theme saving recovers. Session denial uses temporary memory, never child's disk, resets theme on reload. Three previously unreached modes passed in their own first execution, POST attempts0/page errors0 (four pre-existing font GETs blocked).
- Existing theme_review executed independently within mandatory run covers T1–T11 assertions, including its 15-question text/choice sequence, export payload, unknown/get/set storage boundaries/recovery, parent entry/reload/exit, temporary-memory isolation, other-page return, print, reduced-motion and measured colors. Existing main25 suites cover new medaka/edo/recall/history and normal/prototype boundary regressions. Static equality plus suite results are used for these preserved behaviors; no redundant all-question fact audit.

## Failed supplemental harness attempts, retained honestly

1. Full bounded probe attempt1 exited1 at normal result enqueue assertion. The initializing evaluate expression returned an arrow function, which Playwright invoked. Blank page diagnosis with no product loaded measured old initializer1, explicit block0, explicit call1. Preserved original script/log and diagnostic JSON. It reached normal five-question switches but did not reach images/parent/fault/temp.
2. Attempt2 corrected only the harness initialization and moved request observation to a Python list (avoids page-evaluate reentrancy on reload). Normal result spy0, screenshots/diagram/print and control-size assertions passed. It then exited1 because programmatic `.focus()` after mouse clicks was incorrectly treated as keyboard modality. Actual diagnostic measured mouse focus-visible=false/offset0 and real Tab+Space focus-visible=true/offset3/contrast5.509. Product unchanged and threshold not relaxed. No third full-probe run occurred; no “attempt2 all pass” claim.
3. Authorized limited supplemental diagnostic passed once; it serialized diagram numerics not saved before the prior exit. Only previously unexecuted parent/fault/temp modes were then run once and passed. Failure evidence remains alongside successes. No same-cause attempt exceeded2.

## Evidence and limits

Evidence includes scripts, complete logs including both failures, before/after/final JSON, static comparison, diagnostics, six synthetic PNGs and this report. No private answers/photos, baseline checkout or pycache is included. Mandatory tests exercise mocked notifications and may perform existing public asset GETs; their total traffic is not asserted zero. Supplemental routes abort external/POST requests; no actual notifications were sent.

- Chromium CSS viewport 768x1024; no real iPad/Safari/zoom validation
- Visual review of six saved home/diagram images only; no fresh manual visual review of every quiz/feedback/result/parent/records screen
- Scoped two diagram labels, not all diagrams or all contrast combinations
- No real personal answers/materials, preference study, learning-effect measurement or live publication
- Generator parity executed by Engineer; independent QA verifies retained diff/script equality rather than repeating generator execution
- Full mandatory suites include mocked notification services and existing public asset GET behavior; do not describe entire check_all as zero network
- C8 remote PR/ledger persistence and lease release remain coordinator responsibilities

Next: coordinator rechecks lease and remote HEAD, updates existing draft PR12 plus canonical ledger, then releases lease. No new implementation/testing is needed for this frozen candidate on the observed evidence.
