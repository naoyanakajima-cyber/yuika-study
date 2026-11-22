# Harness notes

Initial static clean assertion failed because the manually reused `.venv` was a symlink and `.gitignore` only ignores `.venv/` directories. No tracked/product file was modified. The runtime-only link was replaced with an ignored `.venv` directory containing a `bin` symlink to `/workspace/yuika-study/.venv/bin`. Static review then passed on its second execution. The check-all first log honestly retains `?? .venv` in its start header; final tracked and untracked status is checked separately. This is manual reuse, not successful automated environment restoration.

The independent UI probe passed on its first execution. No product assertion was weakened, no probe failure was retried, and no all-suite rerun was performed.
