#!/usr/bin/env bash
# Source this file in every shell; setup-script exports do not persist to tasks.
cloud_repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
if [[ ! -f "$cloud_repo_root/.venv/bin/activate" ]]; then
  echo 'Run bash scripts/cloud/setup.sh first.' >&2
  return 1
fi
source "$cloud_repo_root/.venv/bin/activate"
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=${PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH:-/usr/bin/chromium}
export PLAYWRIGHT_BROWSERS_PATH=${PLAYWRIGHT_BROWSERS_PATH:-$cloud_repo_root/.cache/ms-playwright}
unset cloud_repo_root
