# Independent QA plan — PR10 / PR32 compatibility

Reviewer: qa_rev_pr32. Author: engineer_rev_pr32. PrM: root/coordinator.

Wait for the fixed candidate commit, then create a separate detached checkout. Manually reuse the existing cloud venv; do not claim automatic snapshot handoff. Run check_all once on clean fixed HEAD, capture complete log, per-suite results, timings and before/after HEAD/status. Require the exact union of old PR10's 32 suites and main's 28 suites (33 unique suites).

Directly compare old PR10/main/candidate, retain old question definitions and shared runtime behavior, inspect parent/notification boundary and new math content. Require generator_preservation to include every tracked file including the new math page. Confirm synthetic 768x1024 review answer/grade/save/reload and math stages/mock reports/parent suppression through required suites and a focused independent probe where coverage is missing.

No private data, real notifications, deployment, push, product edits, new algorithms or authority expansion. Same-cause retry maximum two, only after diagnosis. Old QA and engineer preliminary checks do not establish candidate success.
