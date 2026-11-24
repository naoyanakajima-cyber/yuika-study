# PR10 / PR31 compatibility candidate — engineer evidence

2026-11-24 UTC. Topic checkout `codex/rev-pr31-compat` starts at
`d26d10dea80b93cef7a47dbd814f76e3f69d3934`; merged
`101c64ef9be86cb7c3502d3eeec498f16e93e7fd` with
`git merge --no-commit --no-ff`. Only README had a textual conflict, resolved
by preserving PR10 guidance and adding the notification embedding step.
No main mutation, push, deployment, production settings, or real notifications.

## Scope and generator repair

PR31 report completion/partial-end handling and Edo/focus integration are retained.
PR10 review reasons, actual daily counts, science lever progression, record units/tags,
and history remain. The check_all set is exactly the union: PR10 31, main 27,
candidate 32 suites, including study_reports.

Extended generator preservation retains the original seven generators and adds
Edo, focus, notification and focus-subject embedding in dependency order. It checks
all tracked bytes against the initial snapshot on pass one, then again on pass two;
it never updates the checkout. Initial failure changed Edo, focus and the derived
home progress projection. Diagnosed differences:

- Edo cloned science's new lever-only UI, grading/record fields and selection/runtime.
  It now refreshes build() questions within the existing Edo HTML template, preserving
  its engine and revision archive. Shared notification/history/design/parent embedding
  remains explicit. Future shared engine fixes require explicit Edo review; science
  changes no longer automatically enter Edo. Specifically embed_science targets only
  science, and prototype/embed excludes Edo; Edo science/prototype adapters require
  deliberate manual synchronization, unlike the shared embeddings listed above.
- Focus inherited Kamakura-only recommendation CSS and conditional reason markup.
  The focus generator removes those two inherited fragments; PR10 Kamakura/Onin
  recommendation behavior remains untouched.
- Parent embedding inserted its boundary inside the notification block's comment
  markers. It now inserts before the report begin marker, preserving the full boundary
  before all executable code and making repeated report embedding safe.
- assets/progress.js drift was derived from the unintended Edo science adapter changes;
  preserving Edo prevents that derived drift. No generated HTML beyond the merge
  result was needed to normalize the test.

## Manual preparation and focused verification

No auto-handoff claim. Existing `/workspace/yuika-study/.venv/bin` was manually linked
as ignored `.venv/bin`, then `source scripts/cloud/activate.sh` was run in each Python
shell. `python -m pip check` reported no broken requirements (a nonfatal pip cache
ownership warning); Python resolved to the existing venv, Playwright 1.62.0 and
Chromium 154.0.8037.57. Dedicated setup was not rerun.

All following tests ran on the uncommitted merge working tree while HEAD still
reported d26d10d, not on the eventual candidate commit. Independent QA must run
`bash scripts/check_all.sh` and its UI checks against the fixed candidate SHA.
Engineer did not duplicate the full suite run.

| Command | Observed result |
|---|---|
| `python tests/generator_preservation.py` | Attempt 1 failed first-pass byte equality in the three paths above. After diagnosis and source fixes, attempt 2 passed first and second passes with no tracked-byte changes. |
| `python tests/study_reports.py` | PR10 label/mode adaptation initially passed 16 stubbed reports. Expanded coverage initially failed its four-question fixture because normal Onin includes five candidates; corrected the fixture to the existing kanji filter (four) and required its variant-qualified mode. Expanded attempt 2 passed all seven cases and all 16 reports through Worker validation/stub delivery. |
| `python tests/lever.py` | PASS: 28 calculations/revisions, progression, fallback, challenge gate, tags/units/reports and parent isolation. |
| `python tests/daily_count.py` | PASS: four apps, counts, guards, no additional RNG draws, stale-count confirmation and explicit daily route. |
| `python tests/science_daily_count.py` | PASS: 28 historical selection oracle cases, actual UI counts and normal/parent top route. |
| `python tests/recommended_review.py` | Both Onin/Kamakura compatibility checks passed; actual POST arrivals 0. |
| `python tests/parent_mode.py` | All printed parent-isolation, notification-guard, exit, session-denial and cleanup-recovery checks passed. |
| suite-union and marker inspection | Exact 32-suite union; seven pages each have one notification client after the parent boundary. |
| `git diff --check` | Passed. |

The focused-test shell's final display helper `tail -3 <multiple files>` exited 1
because that shorthand was rejected. This was a log-display error after the five
tests above, not a test failure; `tail -n 3` displayed their success endings. Individual
exit codes for that batch were not captured; independent check_all is the authoritative
per-suite exit-code record. No assertions were removed or weakened.

Expanded study_reports uses fresh 768×1024 contexts and synthetic local settings,
intercepts external traffic, and stubs report delivery. It covers complete/partial
answer counts (including four-question daily), cancelled navigation, unanswered ends,
duplicate result calls/reload, parent queue suppression and unchanged normal storage.
It does not establish real delivery, real user records, Safari/WebKit/iPad behavior,
learning outcomes, or release approval.
