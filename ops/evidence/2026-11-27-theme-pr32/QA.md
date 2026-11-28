# PR12 / PR32 independent QA

Reviewer: `qa_theme_pr32`. Fixed candidate: `b4deb0df131b1280ab2cc0647851e1d345d06143`. Result: **PASS**. Independent detached checkout `/workspace/yuika-theme-pr32-qa-cycle311`; implementation remained untouched.

## Exact revision and static review

The candidate retains old PR12 `df7af2a205f44e8c76b50e96728685efcc7e57d8` and main `58b6d9e0a8e2761e5c446a11ceafa1afb1e832a5` as its two parents. The complete Kamakura HTML (CSS/UI/runtime, content, state/storage code and print rules) and theme tests match old PR12 byte for byte. Math HTML matches main byte for byte. Every file changed against one parent matches the opposite parent, except the combined required-suite runner and new compatibility note. No assertion was weakened. Direct diffs and static comparisons are retained alongside this report.

The frozen 29-suite PR12 list and 28-suite main list have an exact 30-suite union. The runner includes that union once each. The added math/home/design/responsive/notification/preview changes are inherited main bytes. Existing focus derivation excludes all Kamakura theme markers. No new theme, PR10/PR11 feature, grading migration or storage key change was added.

## Full required suite

`bash scripts/check_all.sh` ran once, starting 2026-11-27T17:09:47.019027+00:00, completed 2026-11-27T17:16:16.485679+00:00, exit **0**, **30/30 passed**, total **389 seconds**. No failure, retry, skipped suite or harness repair occurred. HEAD and all 100 tracked-file hashes were unchanged; checkout was clean before and after. `check-all.log` retains all stdout/stderr, suite exit codes and timings. `before.json`, `after.json`, `tracked-sha256.json` and `summary.json` retain receipts.

| Suite | Exit | Seconds |
| --- | ---: | ---: |
| `tests/onin_review.py` | 0 | 3 |
| `tests/kamakura_review.py` | 0 | 4 |
| `tests/cloud_preview.py` | 0 | 2 |
| `notifications/test/worker.test.mjs` | 0 | 0 |
| `notifications/test/browser.py` | 0 | 11 |
| `tests/study_reports.py` | 0 | 31 |
| `tests/cloud_bootstrap.py` | 0 | 2 |
| `tests/generator_preservation.py` | 0 | 1 |
| `tests/adaptive_practice.py` | 0 | 3 |
| `tests/adaptive_daily.py` | 0 | 4 |
| `tests/adaptive_quality.py` | 0 | 5 |
| `tests/flash_grading.py` | 0 | 8 |
| `tests/spaced_daily.py` | 0 | 5 |
| `tests/history_compat.py` | 0 | 5 |
| `tests/edo.py` | 0 | 16 |
| `tests/medaka.py` | 0 | 19 |
| `tests/lever.py` | 0 | 4 |
| `tests/math_passage.py` | 0 | 4 |
| `tests/microscope.py` | 0 | 23 |
| `tests/science_adaptive.py` | 0 | 10 |
| `tests/registered_answers.py` | 0 | 3 |
| `tests/history_review_regression.py` | 0 | 3 |
| `tests/state_review_regression.py` | 0 | 4 |
| `tests/prototype_storage.py` | 0 | 7 |
| `tests/focus_data.py` | 0 | 0 |
| `tests/focus_practice.py` | 0 | 14 |
| `tests/parent_mode.py` | 0 | 21 |
| `tests/design_c.py` | 0 | 30 |
| `tests/responsive_subjects.py` | 0 | 134 |
| `tests/theme_review.py` | 0 | 13 |

The generator suite ran the audited twelve-step sequence twice in an isolated tracked-file copy. Its first pass preserved **all committed bytes**, including math; its second pass was unchanged. This is stronger than checking only idempotence. It also verified the source checkout stayed unchanged. Existing generator fixes and exclusions remain byte-identical to old PR12.

The math suite independently recomputed all 24 answers and verified five stages with 8/3/4/5/4 questions, normal completion, early completion, two intercepted mock reports and parent notification suppression. Design/responsive checks preserved the 22-card home, five-stage math navigation and layout checks. The inherited design/responsive success lines still say 20/21 units; both executed assertions explicitly require 22 cards and were inspected. These are results of this fixed-HEAD independent run, not engineer or prior-cycle results.

## Bounded independent interaction and visual evidence

`theme-probe.py` was inspected and adapted from the previous synthetic probe, then executed anew on this candidate. Two fresh 768×1024 contexts covered normal and parent modes. Each ran five Kamakura questions (text and choice), toggling standard/Kamakura during entered input, selected choice, hint, graded answer and result. Run, learning DOM, input values, preferences, records and notice were compared before/after every toggle. Five answer events survived reload and every round trip; theme switches made no notification enqueue call or extra network request.

Each context made standard→math→return, Kamakura→math→return, and standard→math→return comparisons. Math had no theme panel/attribute, no theme-storage writes, unchanged measured body color/background/font/width, and preserved the selected preference. The three-question second stage completed while Kamakura was selected, and returning restored the theme and all five Kamakura events. The parent banner persisted; normal localStorage, including a different synthetic child theme, stayed byte-identical through parent interactions.

Computed diagram label contrast was **6.2657208213:1** for both themes in screen and print media. Diagram DOM stayed identical and print hid theme controls without storage changes. All six screenshots were opened and inspected; the captured theme input/hint, math result, parent banners and diagram labels were readable without overlap. See `visual-inspection.md` and `image-sha256.json`.

The inherited cloud-preview suite does not directly visit math, so a separate bounded `math-csp-probe.py` used the actual PreviewHandler. Math returned HTTP 200 with five stage controls; a synthetic same-origin POST was rejected by CSP, emitted a `connect-src` policy violation and reached the handler **zero** times. No route intercepted this loopback POST. Both the document CSP and the preview header were active; this verifies their combined blocking, not attribution to the preview policy alone. Theme navigation also checked the connection/form blocking headers.

## Limits and handling

All data and browser contexts were synthetic. The math mock report and Worker suites intercepted APIs; independent previews made no real notification. Existing runtime was manually reused through an ignored `.venv/bin` link; this does not prove automatic environment or snapshot handoff. Real iPad/Safari/WebKit, personal preference, learning effectiveness, physical printing and live deployment remain unverified. No product edit, product push, main merge, deployment, real data/notification, account or environment setting change was performed by QA. Passing QA does not authorize production release.
