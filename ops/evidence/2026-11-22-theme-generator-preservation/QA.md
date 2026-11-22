# Cycle192 independent QA — theme branch generator preservation

Reviewer `/root/qa_theme_generator`, independent of implementer `/root/engineer_theme_generator`. Candidate `00c4ccb3b501223366a5f0a736567231ea9b8043`, baseline PR12 `e89aa335936508c6e4984c523ec65da97f510cbd`. Independent detached cloud checkout `/workspace/qa-theme-generator-checkout`. Existing verified `/workspace/yuika-study/.venv/bin` was manually reused through ignored `.venv/bin`; no automatic snapshot handoff success claim. No product/board edits, push, private data, real notifications or deployment.

## Outcome

PASS. Exact candidate full required suite first attempt: 28/28 exit 0, 326 seconds, command exit 0. Start and end checkout status completely clean; HEAD unchanged. Result recorded 2026-11-22T18:18:26.769440+00:00. Each suite and timing: `suite-result.json`; complete output: `check-all-attempt1.log`. Independent static, regeneration and both UI probes also passed on first execution. No blocking findings.

## Source and contract review

- Ten expected paths changed: PR12's own science adapter and prototype source, four non-science HTML allowlist rows, generator regression, lever record regression, check runner and compatibility documentation. No unrelated product changes or weakened assertions/CSP.
- Science HTML is byte-identical to baseline (SHA-256 `54addcfe1f2491adcfb501a2525c476e2ded2d5d5c80062c0c124395cfa866f3`). Its science adapter and prototype block exactly match the new source, including separator handling. PR10's `scienceDailySources` and PR11 CONTENT feature are not imported.
- The four other HTML files each change exactly one science-only allowed-field row: `answerUnit` / `answerTag`. Replacing that single old row produces the complete new file exactly, preserving all other bytes, including Kamakura theme CSS/UI/JS, hierarchy diagram and print rules. The actual predicate is `typeof byId!=='undefined'`; none of the four files declares `byId`. The non-science allowed fields are unchanged.
- Theme specification and existing theme test are byte-identical; all 85 other baseline paths are unchanged. All old 27 suites retain their order, with only the generator regression added (28 total). Evidence: `static-review.py`, `static-result.json`, `static.log`.
- The generator regression checks a disposable tracked-file copy against original bytes on the first pass and again on the second, then confirms the source checkout unchanged. The lever regression uses a real downloaded file and file input. Its reload is before export; import-then-reload is separately covered by the independent science probe. Documentation accurately describes that sequence.

## Independent regeneration and expected negative

`regeneration.py` ran the seven actual generators twice in an archive of the exact candidate. All fourteen commands exited 0 and all tracked bytes matched the original after each pass. Transplanting the identical new regression into a disposable baseline PR12 checkout failed as expected with exit 1: `Generator pass 1 changed tracked files: ['yuika-review-v2.html']`. This is detection of the old defect, not a candidate failure. Original checkout stayed clean. Evidence: `regeneration-result.json`, `regeneration.log`, `old-pr12-generator-negative.log`.

## New bounded synthetic UI probes

`theme-probe.py` ran in two fresh 768×1024 Chromium contexts, normal and parent mode. Five synthetic answers per context covered text input and choice selection, hint, graded and result states. Each standard/Kamakura toggle preserved the same run, question/index/results, learning data/preferences, learning DOM and inputs. Only the normal theme key could change; parent mode preserved all child localStorage bytes. Theme-triggered enqueue/request calls were zero. Selecting Kamakura before reload restored both that theme and the five events.

In normal mode, both themes' screen and print media retained the hierarchy SVG DOM. Both `将軍` and `執権（北条氏）` labels remained 13px white on `#8f4f3c`, measured contrast 6.2657:1. Print hid the theme panel without changing stored preferences. Same-origin science navigation in each mode after standard→Kamakura→standard showed no theme controls/styles and identical measured lever-01/27/28 diagrams, with no horizontal overflow. POST attempts/arrivals and page errors were zero; 16 external font GETs were aborted and separately counted. Evidence: `probe-result.json`, `theme-probe.log`.

`science-probe.py` ran separately in normal and parent mode. An actual UI `lever-16` synthetic answer (`25 cm`) retained unit/tag through reload, actual JSON download, import via file input into empty trial storage, and another reload. A fieldless old record remained acceptable. Invalid unit, invalid tag and unknown field imports were rejected, preserving submitted raw and saved events. Parent child localStorage stayed unchanged. POST attempts/page errors were zero; 11 external font GETs were aborted. Evidence: `science-probe-result.json`, `science-probe.log`.

Four saved images were actually inspected: normal/parent Kamakura input+hint, hierarchy diagram, and non-target lever-28 diagram. Text, primary controls and parent banner were readable in these limited views; no visual blocking issue observed. See `visual-review.json`. These fresh checks are separate from prior cycle evidence and do not assert more contexts or device coverage.

## Limits and next step

Synthetic Chromium validation only. Real iPad/Safari, native zoom, CEO hands-on, learning benefit, theme preference and public deployment remain unverified. Local suite results do not establish external Workers build success. Preserve draft status and let the coordinator verify remote lease, save code/PR/evidence/board, and release the lease. Main is not repaired or authorized for merge by this review.
