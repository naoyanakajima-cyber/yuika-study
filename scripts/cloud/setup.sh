#!/usr/bin/env bash
set -Eeuo pipefail
repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$repo_root"
umask 077
stage=invalidate-receipts
trap 'code=$?; trap - ERR; printf "FAIL stage=%s exit=%s time=%s\n" "$stage" "$code" "$(date -u +%FT%TZ)"; exit "$code"' ERR
step() { stage=$1; printf 'STAGE %s time=%s\n' "$stage" "$(date -u +%FT%TZ)"; }
step invalidate-receipts
if [[ -L .venv ]]; then
  echo 'Virtual environment is a symlink; preserved.' >&2
  echo 'FAIL stage=invalidate-receipts exit=1' >&2
  exit 1
fi
rm -f -- .venv/yuika-cloud-install.json .venv/yuika-cloud-setup.json
step log-directory
log_dir=${YUIKA_CLOUD_LOG_DIR:-/workspace/work/yuika-cloud-logs}
mkdir -p "$log_dir"
log_file="$log_dir/setup-$(date -u +%Y%m%dT%H%M%SZ)-$$.log"
exec > >(tee -a "$log_file") 2>&1
step runtime

# The managed image supplies Python, Node.js, and Debian Chromium with its
# system libraries. No production notification credentials are needed.
python --version
node --version
npm --version
chromium_path=${PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH:-/usr/bin/chromium}
if [[ ! -x "$chromium_path" ]]; then
  echo 'Chromium missing. Select a cloud image with Chromium and its system dependencies; see docs/codex-cloud.md.' >&2
  printf 'FAIL stage=runtime exit=1\n' >&2
  exit 1
fi
"$chromium_path" --version
step virtualenv
python -m venv .venv
step dependencies
.venv/bin/python -m pip install --disable-pip-version-check --no-cache-dir -r requirements-dev.txt
step dependency-check
.venv/bin/python -m pip check

# A real launch checks browser compatibility and shared-library availability.
step browser-launch
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
step receipt
.venv/bin/python - "$chromium_path" "$log_file" <<'PY'
import hashlib, importlib.metadata, json, platform, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
root = Path.cwd()
receipt = {
    'schema': 1,
    'completed_at': datetime.now(timezone.utc).isoformat(),
    'checkout': str(root),
    'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'requirements_sha256': hashlib.sha256(Path('requirements-dev.txt').read_bytes()).hexdigest(),
    'python': platform.python_version(),
    'playwright': importlib.metadata.version('playwright'),
    'chromium': subprocess.check_output([sys.argv[1], '--version'], text=True).strip(),
    'setup_log': sys.argv[2],
}
Path('.venv/yuika-cloud-setup.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('RECEIPT .venv/yuika-cloud-setup.json')
PY
echo 'SUCCESS stage=complete'
echo 'Ready. In each new shell: source scripts/cloud/activate.sh'
