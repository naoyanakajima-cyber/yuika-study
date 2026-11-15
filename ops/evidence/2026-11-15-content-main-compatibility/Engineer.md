# Cycle33 Engineer handoff — CONTENT-MVP current-main compatibility

- Frozen candidate: `d75a5469fbf1e8c5011a6307308546e5ec669ceb`.
- Checkout: `/workspace/yuika-content-main-compat-20261115`, branch `codex/content-main-compat-20261115`.
- Merge parents: existing PR11 `ee51e68d7e1eeb21bd0e959ec58166a869947d0a`, current main `60d1a946cc02ed8acea54c0d7af7d6451fcc30ec`.
- Commit timestamp 2026-11-15T09:08:53Z, clean freeze verified around 09:09Z. No product edits after freeze.
- Sole merge conflict was preview allowlist; resolved to preserve both Edo learning entry and content review entry. No main branch change, no push.

## Implementation and accepted scope

1. Topic merge retains both parents and all preceding PR11 history. All 84 main-tracked files outside the seven explicit shared integration paths exactly match main; this includes seven learning HTML pages, assets, practice/history, notification code and runtimes.
2. Existing PR11 content HTML, three product specs, four synthetic fixture files and four content-specific suites (12 files total) exactly match old PR11 HEAD. No new feature or PR10/12 dependency introduced.
3. Preview retains loopback, narrow explicit entries, CSP/API blocking, no-store and HEAD405; Edo and content entry coexist. Cloud-preview regression now checks Edo HTTP200, exact body, CSP, no-store and HEAD405 as well as existing content entry. Documentation allowlist includes Edo.
4. check_all keeps exact union of the existing 26 PR11 and 25 main suites: 29 unique run lines, no duplicates or dropped assertions.
5. Parent-mode required entries now explicitly include Edo as well as content. Main recall operation and every non-content HTML protection remain. Content SHA exception and generator preflight remain byte-identical to old PR11. Unknown HTML requires protection; generator may embed protection into unknown HTML, matching existing behavior.
6. Independent QA owns exact fixed-HEAD all29 suite run and fresh 768px content trial manual flow. Engineer does not claim those results.
7. Main-relative diff comprises old PR11 content additions plus the seven shared integration paths only; no unrelated main rollback.

## Engineer verification performed

- `source scripts/cloud/activate.sh; python tests/cloud_preview.py`: exit0. `/tmp/yuika-cycle33-engineer/cloud-preview.log`.
- `source scripts/cloud/activate.sh; python tests/parent_mode.py`: exit0. Six original apps exercise isolation/reload/exit/mock-notification guards, deletion/rollback/session-denial behavior; static preflight also includes Edo. This does not claim interactive Edo parent flow coverage. `/tmp/yuika-cycle33-engineer/parent-mode.log`.
- `source scripts/cloud/activate.sh; python /tmp/yuika-cycle33-engineer/static-check.py`: exit0. `/tmp/yuika-cycle33-engineer/static-check.json`.
- Static verifier compared current working tree bytes against both exact parent commits; all main84/content12 matches and run-line union29 passed.
- In a temporary copy only: parent generator replay preserved all8 HTML bytes; unprotected synthetic unknown HTML was rejected by parent preflight, embedded with generator, then passed; altered synthetic content HTML caused parent generator rejection before any HTML writes and preflight rejected it. Temporary copy removed automatically.
- `git diff --check --cached` and final `git diff --check HEAD^ HEAD`: exit0.
- Final HEAD/parents/time saved in `frozen-head.txt`; `frozen-status.txt` empty.

## Preparation and limitations

Read AGENTS.md, README.md and docs/codex-cloud.md; used cloud checkout only. requirements-dev.txt exactly matched the previously verified `/workspace/yuika-pr26-fix-20261112` checkout; manually reused its venv through an ignored `.venv/bin` link. `python -m pip check` succeeded and runtime import succeeded. This is manual reuse, not proof of snapshot auto-handoff success. Initial directory-level venv symlink appeared untracked because `.gitignore` matches `.venv/`; it was replaced with ignored directory plus bin link before clean freeze, with no product/config changes.

No dedicated content suites repeated by Engineer because their bytes were untouched; independent QA will run them in the required all29. No long suite started by Engineer. No tests failed and no blind retries. Synthetic data only. No deployment, real notifications, settings, secrets or permissions changes. Browser validation is Chromium only, not Safari/WebKit/real iPad. Independent acceptance and any CEO decision remain for root/QA and the canonical board.
