# PR26 follow-up engineering evidence

- Independent checkout: `/workspace/yuika-pr26-fix-20261112`
- Local branch: `codex/pr26-followup-20261112`
- Original PR26 HEAD: `326d5fd76756963819fcdc0a7463ef867aeed331`
- Integrated prior verified test-only commit `df791c07c0071921e22ae667e5230f8fd99ed782` as `5b772250401d9057152d698f07e78456968bbf85` (parent-mode fixture seeded before application startup).
- Frozen candidate: `acd169882b626ef255ba68cd73c995024c30e515`, working tree clean.

## Reproduced issue and repair

Independent QA reproduced unsupported URL subjects `constructor`, `toString`, and `__proto__` being mistaken for configured subjects, showing native-function/object titles and zero questions. Missing, empty, and ordinary unknown subjects already fell back to the mixed 46-question entry. No code-execution or data-leak finding is claimed.

The narrow repair accepts only own properties of the four-subject mapping in `scripts/focus/subjects.js` and the generated-summary template `scripts/design/build_summary.py`. Regenerated `mock-focus-review.html` and `assets/progress.js` contain those guards. The new regression in `tests/responsive_subjects.py` checks empty/plain-unknown/inherited names, fallback to all 46 selectable questions, unchanged mixed preferences, matching home summaries, and unchanged stored answer history. Existing valid-subject and history tests remain intact.

## Engineer verification

- `source scripts/cloud/activate.sh && python tests/responsive_subjects.py`: PASS, exit 0, first attempt. All 17 pages across 390/768/1024/1280 widths in normal and parent modes, subject boundaries, mixed-history preservation, and added invalid-subject cases passed.
- Focused test output: `/tmp/engineer-pr26-responsive.log`.
- `node --check assets/progress.js`: PASS.
- `git diff --check`: PASS.
- Re-running `scripts/design/embed.py`, `scripts/parent/embed.py`, and `scripts/design/build_summary.py` produced identical hashes for generated outputs: idempotency PASS.
- Existing prepared Python/runtime reused through an ignored `.venv/bin` symlink to `/workspace/yuika-pr25-review-20261112/.venv/bin`; no dependency installation or setup execution. This is manual runtime reuse, not evidence of automatic setup inheritance.

## Handoff

Independent reviewer `/root/qa_pr26_review` received the exact frozen candidate for separate subject/preferences probes and one full 22-suite. Engineering has not self-approved that full-suite result. No push, PR mutation, production action, real notification, or private inputs were used. Parent coordinator owns lease recheck, integration/push, PR update, and ledger persistence.
