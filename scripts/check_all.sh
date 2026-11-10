#!/usr/bin/env bash
set -uo pipefail
repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root" || exit 1
source scripts/cloud/activate.sh || exit 1
export PYTHONHASHSEED=0
printf 'HEAD: %s\n' "$(git rev-parse HEAD)"
printf 'Working tree (empty = clean):\n'
git status --short
printf 'Browser RNG seed: 20261110\n'
names=()
codes=()
times=()
failed=0
all_started=$SECONDS
run() {
  local name=$1 started=$SECONDS code
  shift
  printf '\nRUN %s\n' "$name"
  "$@"
  code=$?
  names+=("$name"); codes+=("$code"); times+=("$((SECONDS-started))")
  if (( code != 0 )); then failed=1; fi
}
run tests/onin_review.py python tests/onin_review.py
run tests/kamakura_review.py python tests/kamakura_review.py
run tests/cloud_preview.py python tests/cloud_preview.py
run notifications/test/worker.test.mjs node --test notifications/test/worker.test.mjs
run notifications/test/browser.py python notifications/test/browser.py
run tests/cloud_bootstrap.py python tests/cloud_bootstrap.py
run tests/adaptive_practice.py python tests/adaptive_practice.py
run tests/adaptive_daily.py python tests/adaptive_daily.py
run tests/adaptive_quality.py python tests/adaptive_quality.py
run tests/flash_grading.py python tests/flash_grading.py
printf '\n%-40s %6s %8s\n' 'Suite' 'Exit' 'Seconds'
for i in "${!names[@]}"; do
  printf '%-40s %6s %8s\n' "${names[$i]}" "${codes[$i]}" "${times[$i]}"
done
printf 'Total: %ss; result=%s\n' "$((SECONDS-all_started))" "$failed"
exit "$failed"
