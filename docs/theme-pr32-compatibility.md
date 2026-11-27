# Theme branch and PR32 compatibility

## Scope and parents

This topic merges main `58b6d9e0a8e2761e5c446a11ceafa1afb1e832a5`
into PR12 head `df7af2a205f44e8c76b50e96728685efcc7e57d8`.
The merge had no textual conflicts and required no product-code repairs.
It incorporates PR32's 24-question, five-stage math page and home entry while
preserving the Kamakura-only theme. It adds no theme, PR10 or PR11 feature.

Kamakura HTML, `tests/theme_review.py`, shared Design C assets, the repaired
Edo/focus/parent generators, and `tests/generator_preservation.py` are
byte-identical to the PR12 parent. Math HTML, home HTML, notification embedding,
preview server, design/responsive tests and math tests are byte-identical to
main. The only combined code is the required-suite registration: exact set
equality against both frozen parents confirms 30 unique suites, comprising all
29 PR12 suites plus `tests/math_passage.py` (main has 28).

The existing theme CSS/UI/runtime, state and record behavior, print handling
and diagram contrast fixes are therefore retained. Existing generator fixes
remain in place, including exclusion of Kamakura theme blocks from focus.

## Preliminary checks

The existing cloud environment was manually reused by an ignored `.venv/bin`
link to `/workspace/yuika-study/.venv/bin`, after inspecting the previous
content checkout's same link. Each execution shell sourced
`scripts/cloud/activate.sh`. This is not evidence of automatic environment
setup or saved snapshot application.

- Parent file-byte checks and the exact 30-suite union passed.
- `python tests/generator_preservation.py` exited 0: all 12 generation steps
  preserved every tracked file on the first pass, including the new math HTML;
  the second full pass was unchanged. The isolated test also verified that
  the source checkout was unchanged.
- `python tests/math_passage.py` exited 0: all 24 answers were independently
  recomputed; staged answers, mock reports, early completion and parent
  notification suppression passed.
- A focused math check using the real cloud preview handler and fresh
  Chromium context returned HTTP 200, displayed five stage controls, and
  observed `connect-src 'none'` blocking a synthetic POST. POST arrivals: zero.
- `git diff --cached --check` passed before this note was added; the complete
  staged candidate is checked again before commit.

All answer records and notification configuration used for checks were
synthetic; endpoints and delivery were mocked or blocked.

## Independent acceptance and limits

Independent QA owns `bash scripts/check_all.sh` on the fixed candidate commit,
plus theme-to-math-to-theme navigation in normal and parent modes, checking
theme isolation and preference restoration. Those final-commit results are
pending when this note is committed and will be recorded separately.

Chromium checks do not establish Safari/WebKit or real-iPad compatibility,
personal preference or learning effectiveness. No private records, textbook
photos, real notifications, push, main merge, deployment, Secrets, account
settings or sharing changes were performed by the engineer.
