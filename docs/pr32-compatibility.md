# PR10 / PR32 compatibility candidate — engineer evidence

2026-11-27 UTC. Topic checkout `codex/rev-pr32-cycle309` starts at
`0cd726f558d24999da80c37b1ecdbd2e6090c7bb` and merges main
`58b6d9e0a8e2761e5c446a11ceafa1afb1e832a5` with `--no-commit --no-ff`.
Only index.html had a textual conflict. The resolution preserves PR10's
「今日の復習」labels and adds the math-passage unit in the same location as main.
The main changes to the progress label, preview allowlist, notification embedding,
responsive/design assertions and staged math tests are retained.

## Scope

PR10 recommendation reasons, actual daily counts, existing IDs/keys/history,
parent isolation and notification suppression remain. Math passage's 24 original
questions and five stages are unchanged from main. Its run answers and report
queue are not a new persistent recommended-review data source. No new math
recommendation feature, product adoption, main merge, release or real notification
is included. PR11/12 are untouched.

The check_all suite set is exactly the union: prior PR10 32, current main 28,
candidate 33, adding math_passage while retaining every prior suite. Assertions
and CSP were not weakened. The resolved index diff against prior PR10 contains
only the two main additions (unit entry and its problem-count progress label).

## Manual preparation and focused results

Existing `/workspace/yuika-study/.venv/bin` was manually linked as ignored
`.venv/bin`; each test shell sourced scripts/cloud/activate.sh. Setup and dependency
installation were not repeated. This is not evidence of automatic snapshot handoff.

These checks ran on the uncommitted candidate while HEAD still reported 0cd726f,
not the final candidate SHA. Independent QA must execute the fixed final SHA.

| Check | Result |
| --- | --- |
| python tests/generator_preservation.py | First attempt exit 0. The 12-step real generator chain preserved every tracked file, including the added math HTML, on both passes. No source repair needed. |
| python tests/math_passage.py | First attempt exit 0. All 24 answers independently recomputed; staged operations and mock reports passed. |
| suite-set union | 32 union 28 equals candidate 33. No missing/extra suite. |
| git diff --check | Passed. |

No test failure occurred. The merge conflict was resolved before testing.
The Engineer did not repeat the full check_all run; independent QA owns that run.
The QA handoff includes 768×1024 start/answer/grading/save/reload checks for the
existing review features, the math stage interaction, synthetic mock reports and
parent-mode suppression. Existing check_all suites provide these flows and should
be reviewed for coverage against this exact candidate.

Cloudflare Workers Builds and Safari/WebKit/iPad real-device verification remain
separate limitations. No real records, private教材, mail or remote notification API
were used. No push was performed by the Engineer.
