# Theme branch and PR31 compatibility

## Scope and candidate parents

This topic merges observed main `101c64ef9be86cb7c3502d3eeec498f16e93e7fd` into PR12 head `00c4ccb3b501223366a5f0a736567231ea9b8043`. The merge had no textual conflicts. It preserves Kamakura appearance switching, in-progress input and hints, grading, history, reload, parent isolation, and diagram contrast while incorporating PR31 study-report lifecycle behavior and Edo/focus notification integration. No PR10 recommendation/count feature or PR11 content-review feature is included.

The required suite union is 29: all 28 original PR12 suites plus main's added `tests/study_reports.py` (main has 27). Set equality was checked against both frozen parent scripts. The complete final-commit `bash scripts/check_all.sh` is assigned to independent QA; the results below are preliminary checks of the uncommitted candidate, not a claim that final-commit QA has passed.

## Generator diagnosis and repair

The original seven-step preservation test omitted Edo, focus and notification generation. Expanding it to the real 12-step sequence initially exited 1 on its first generation: `assets/progress.js`, `edo-review.html`, and `mock-focus-review.html` changed. This was an observed regression, not an expected test success.

Inspection of the isolated generated copy found three causes:

- Edo cloned current science HTML, importing science-only lever code and changing its derived progress projection.
- Parent embedding placed the storage boundary inside the notification markers, allowing subsequent notification embedding to remove it.
- On this theme branch, focus generation also cloned Kamakura-only theme CSS, controls and runtime, including an unintended focus theme preference key. This difference did not occur on the content branch and required its own repair.

Edo now refreshes questions from `scripts/edo/questions.py` in its existing standalone engine. Future science/prototype adapter changes need explicit Edo synchronization; shared notification/history/design/parent generators still update their blocks. Parent embedding inserts before the entire reports block. Focus generation removes exactly one of each of the three Kamakura theme blocks before deriving its shared quiz engine; count assertions fail if that source structure changes. It does not strip unrelated recommendation features.

After diagnosis and these repairs, the next preservation run exited 0: the first complete generation preserved every tracked file byte, and a second complete generation was unchanged. A final timed run after README clarification also passed (exit 0, 0.972 seconds). Checks run in isolated tracked-file copies and assert the source checkout is unchanged; no assertions were weakened.

Original PR12 `scripts/practice/science.js`, `scripts/practice/embed_science.py`, `scripts/prototype/runtime.js`, `scripts/prototype/embed.py`, `tests/lever.py`, `tests/theme_review.py`, and shared design assets remain byte-identical to the original topic head. The merged HTML incorporates only PR31 behavior; the generators reproduce it exactly.

## Preliminary verification

Every shell sourced `scripts/cloud/activate.sh`. The existing cloud dependency environment was manually reused via an ignored `.venv/bin` symlink; this does not establish automatic environment handoff. Browser contexts and answer/configuration data are synthetic, notification endpoints and Worker delivery are mocked.

| Focused suite | Exit | Seconds |
| --- | ---: | ---: |
| `tests/theme_review.py` | 0 | 12.581 |
| `tests/study_reports.py` | 0 | 26.171 |
| `tests/lever.py` | 0 | 4.201 |
| `tests/prototype_storage.py` | 0 | 7.031 |
| `tests/focus_data.py` | 0 | 0.046 |
| `tests/generator_preservation.py` (final timed run) | 0 | 0.972 |

Theme tests covered input/state preservation, reload, stored preference errors, parent isolation, keyboard controls and diagrams in both themes on screen and print. The two hierarchy label contrast ratios were 6.266 in all four theme/media combinations; unexpected external requests and POST arrivals were zero (15 existing font GETs blocked).

Study reports exercised seven app/unit cases with daily planned count, early completion, cancelled navigation, unanswered completion, duplicate completion and parent isolation. Sixteen captured synthetic reports passed the Worker contract and mail stub checks. Cancellation leaves storage and queue unchanged; unanswered completion creates no job; parent checks leave normal localStorage byte-identical. The browser suite fetches existing public React/Babel CDN assets, so it is not completely offline.

Lever tests passed 28 calculations/revisions, daily/recheck behavior, staged quiz and fallback, challenge gating, unit/error tags, reports and parent isolation. Prototype tests passed existing-record preservation, import/export and corrupt/quota behavior. Focus data passed all 46 original questions and privacy guards. `git diff --check` exited 0.

## Limits

Independent final-commit full-suite and manual operation verification are still pending at the time this document is committed. Chromium at iPad-equivalent size is not Safari/WebKit or real-iPad validation. No real records, textbook photos, delivery, personal trial, production publication or learning effectiveness were tested. No push, main merge, deployment, real notification, secret, account setting or sharing change was performed by the engineer.
