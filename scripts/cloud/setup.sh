#!/usr/bin/env bash
set -euo pipefail
repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$repo_root"

# The managed image supplies Python, Node.js, and Debian Chromium with its
# system libraries. No production notification credentials are needed.
python --version
node --version
npm --version
chromium_path=${PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH:-/usr/bin/chromium}
if [[ ! -x "$chromium_path" ]]; then
  echo 'Chromium missing. Select a cloud image with Chromium and its system dependencies; see docs/codex-cloud.md.' >&2
  exit 1
fi
"$chromium_path" --version
python -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check --no-cache-dir -r requirements-dev.txt
.venv/bin/python -m pip check

# A real launch checks browser compatibility and shared-library availability.
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH="$chromium_path" .venv/bin/python - <<'PY'
import os
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    with pw.chromium.launch(executable_path=os.environ['PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH']) as browser:
        page = browser.new_page(viewport={'width': 768, 'height': 1024})
        page.set_content('<title>cloud-ready</title>')
        assert page.title() == 'cloud-ready'
        print(f'Chromium launch OK: {browser.version}, viewport 768x1024')
PY
echo 'Ready. In each new shell: source scripts/cloud/activate.sh'
