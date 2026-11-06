#!/usr/bin/env bash
# Standalone: paste the rendered version into the saved environment Install field.
# This file must not depend on files in the environment's initial main checkout.
set -Eeuo pipefail
umask 077

revision=${1:?Usage: install.sh FULL_COMMIT [ABSOLUTE_CHECKOUT_DIRECTORY]}
checkout=${2:-/workspace/yuika-study-cloud}
source_repo=${YUIKA_CLOUD_SOURCE_REPO:-https://github.com/naoyanakajima-cyber/yuika-study.git}
log_dir=${YUIKA_CLOUD_LOG_DIR:-/workspace/work/yuika-cloud-logs}
[[ $revision =~ ^[0-9a-f]{40}$ ]] || { echo 'A full lowercase commit SHA is required.' >&2; exit 2; }
[[ $checkout == /* && $checkout != / && ! -L $checkout ]] || { echo 'Use an absolute, non-symlink checkout directory.' >&2; exit 2; }
# A local Git repository is supported for isolated verification, not private files.
[[ $source_repo == https://github.com/naoyanakajima-cyber/yuika-study.git || $source_repo == /* ]] || { echo 'Unexpected source repository.' >&2; exit 2; }
mkdir -p "$log_dir"
log_dir=$(cd -- "$log_dir" && pwd -P)
log_file="$log_dir/install-$(date -u +%Y%m%dT%H%M%SZ)-$$.log"
exec > >(tee -a "$log_file") 2>&1
stage=validate
trap 'code=$?; trap - ERR; printf "FAIL stage=%s exit=%s time=%s\n" "$stage" "$code" "$(date -u +%FT%TZ)"; exit "$code"' ERR
step() { stage=$1; printf 'STAGE %s time=%s\n' "$stage" "$(date -u +%FT%TZ)"; }
fail() { echo "$1" >&2; return 1; }
printf 'INSTALL required_revision=%s log=%s\n' "$revision" "$log_file"

step inspect-checkout
if [[ -e $checkout ]]; then
  [[ -d $checkout ]] || fail 'Existing target is not a directory; preserved.'
  [[ $(git -C "$checkout" rev-parse --show-toplevel) == "$(cd -- "$checkout" && pwd -P)" ]] || fail 'Existing target is not its own checkout; preserved.'
  [[ $(git -C "$checkout" remote get-url origin) == "$source_repo" ]] || fail 'Existing origin differs; preserved.'
  [[ -z $(git -C "$checkout" status --porcelain=v1 --untracked-files=all) ]] || fail 'Existing checkout has changes; preserved. Inspect it before setup.'
  git -C "$checkout" merge-base --is-ancestor "$revision" HEAD || fail 'Existing HEAD does not contain the required revision; preserved. Use a new target directory.'
  printf 'REUSE head=%s branch=%s (no checkout/reset/clean)\n' "$(git -C "$checkout" rev-parse HEAD)" "$(git -C "$checkout" branch --show-current)"
else
  step fetch-pinned-revision
  mkdir -p -- "$(dirname -- "$checkout")"
  staging=$(mktemp -d "$(dirname -- "$checkout")/.yuika-cloud-install.XXXXXX")
  # Keep failed staging directories for diagnosis; never delete existing work.
  printf 'STAGING directory=%s\n' "$staging"
  git init -q "$staging"
  git -C "$staging" remote add origin "$source_repo"
  git -C "$staging" fetch --no-tags origin "$revision"
  [[ $(git -C "$staging" rev-parse 'FETCH_HEAD^{commit}') == "$revision" ]] || fail 'Fetched revision mismatch.'
  step checkout-pinned-revision
  git -C "$staging" checkout --detach "$revision"
  # -T refuses an existing directory; a race must not nest or replace a checkout.
  mv -T --no-clobber -- "$staging" "$checkout"
  [[ ! -e $staging ]] || fail 'Target appeared during installation; both directories preserved.'
fi

step setup
[[ -f $checkout/scripts/cloud/setup.sh && -f $checkout/scripts/cloud/activate.sh && -f $checkout/AGENTS.md ]] || fail 'Required setup files are missing.'
[[ ! -L $checkout/.venv ]] || fail 'The virtual environment is a symlink; preserved.'
# A failed retry must not retain a previous successful installation receipt.
rm -f -- "$checkout/.venv/yuika-cloud-install.json"
bash "$checkout/scripts/cloud/setup.sh"
step record-success
python - "$checkout" "$revision" "$log_file" <<'PY'
import hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
root, revision, log = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
receipt = {
    'schema': 1,
    'completed_at': datetime.now(timezone.utc).isoformat(),
    'required_revision': revision,
    'head': subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip(),
    'checkout': str(root.resolve()),
    'requirements_sha256': hashlib.sha256((root / 'requirements-dev.txt').read_bytes()).hexdigest(),
    'install_log': log,
    'provenance': 'installer invocation; correlate with platform startup logs to establish automatic execution',
}
path = root / '.venv/yuika-cloud-install.json'
path.write_text(json.dumps(receipt, indent=2) + '\n')
print(f'RECEIPT {path}')
PY
printf 'SUCCESS stage=complete time=%s checkout=%s\n' "$(date -u +%FT%TZ)" "$checkout"
