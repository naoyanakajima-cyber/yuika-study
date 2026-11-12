# Parent-mode test fixture boundary repair

Engineer: engineer_parent_test_boundary. Baseline PR25 042c55dd04a285277dc3dfa9dd296f161283e809. Candidate df791c07c0071921e22ae667e5230f8fd99ed782 on independent branch codex/parent-test-boundary-20261112, checkout /workspace/yuika-parent-test-fix-20261112. No push/PR update by child.

Changed only tests/parent_mode.py. Fixture storage is now populated on an inert, same-origin route before any application or notification runtime starts. The first app load enters parent-check mode. Added assertions verify absent app globals and pre-existing pending state. Existing calls collection, zero-request assertion, child raw preservation, sandbox answers/reload, cleanup/rollback checks, and normal post-exit mock sending remain. Calls are never cleared or ignored. Request failure diagnostics now include the test phase and requesting document URL; phase is harness state, not a claimed fetch-time active flag.

Independent QA demonstrated a normal startup flush delayed by an actual Web Lock can consume the old fixture after it is seeded, before parent navigation. The new setup removes that preparation window. This does not prove the precise cause of the prior uninstrumented 05:14 failure. Product notification runtime, parent boundary, all app files and user storage contracts are unchanged.

Engineer validation: one focused python tests/parent_mode.py after activation, exit0. All six app entries, isolation/reload/exit/notification guards, inclusive deletion/count/cancel/preservation/stale confirmation, tab close, temporary-mode storage denial and rollback/recovery cases passed. Log: /tmp/engineer-parent-boundary-test.log. git diff --check passed; committed candidate clean. No full-suite run by Engineer; independent QA owns the one candidate full-suite run.

Existing prepared runtime reused manually: ignored .venv directory with bin symlink to /workspace/yuika-pr25-review-20261112/.venv/bin. No dependency/browser installation, setup script, environment settings or permission changes. A top-level symlink was first untracked under the existing directory-only .gitignore rule, so it was replaced by the ignored directory wrapper before candidate commit. This is not automatic setup verification.

Synthetic records and intercepted mock APIs only. No real notifications/private data, merge, publish/deploy, billing, Secrets/access changes, or child delegation.
