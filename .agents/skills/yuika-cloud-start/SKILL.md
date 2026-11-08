---
name: yuika-cloud-start
description: Start work in the saved yuika-study Codex Cloud environment and verify installation evidence without overwriting existing branches.
---

# Start yuika-study in Codex Cloud

1. Before running setup manually, inspect the current environment's supported
   status and install logs. Record the runtime environment ID, source configuration
   ID/version, timestamps, initial checkout/HEAD, and whether this is a new task
   or a resumed runtime. Do not dump environment variables or credentials.
2. The saved Install script prepares `/workspace/yuika-study-cloud` independently
   of the platform's initial checkout. Read its `AGENTS.md` and
   `docs/codex-cloud.md`. Confirm `git status --short --branch`, HEAD, and
   `.venv/yuika-cloud-install.json` plus `.venv/yuika-cloud-setup.json` before
   changing anything. Receipts alone do not prove automatic execution: correlate
   them with the platform's Install run and saved configuration version. An empty
   skill list or revision number alone does not establish non-application.
3. Preserve any existing topic branch and uncommitted changes. Never reset,
   clean, force-checkout, or force-pull a branch. For a new task on the installer's
   detached HEAD, create a unique `codex/<task>` branch. If resuming an existing
   topic branch, keep it. Use a separate checkout for independent concurrent tasks.
4. In every shell that runs Python, first run
   `cd /workspace/yuika-study-cloud` and `source scripts/cloud/activate.sh` in
   that same shell. Installed packages persist; shell exports do not.
5. If setup evidence or dependencies are missing, report that automatic preparation
   is unverified. You may run `bash scripts/cloud/setup.sh` in the verified checkout
   as manual recovery; identify it as manual. If the dedicated checkout is absent,
   use the saved, commit-pinned Install script. Do not assume setup files exist on
   main, substitute a moving branch, or overwrite the initial checkout.
6. Run these six commands after activation in the same shell and record each
   exit code:

   ```bash
   python tests/onin_review.py
   python tests/kamakura_review.py
   python tests/cloud_preview.py
   node --test notifications/test/worker.test.mjs
   python notifications/test/browser.py
   python tests/cloud_bootstrap.py
   ```

7. For a requested development preview, after activation run
   `python scripts/cloud/serve.py --port 8000` and use the cloud browser at
   `http://127.0.0.1:8000/`. Choose a different port for concurrent previews.
   Do not start a production service. The preview blocks notification APIs by CSP.
8. Use synthetic browser records and mock notification APIs only. Do not send
   email/Chat, deploy, publish the app, merge production changes, change Secrets
   or billing, or import personal answers, photos, or browser profiles. Keep
   `.venv` and logs out of commits. Report current results and limitations.
