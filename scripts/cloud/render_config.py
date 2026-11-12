"""Render a standalone, commit-pinned Install script and saved Start skill."""
import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--revision', required=True, help='Full reviewed commit SHA')
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
if not re.fullmatch('[0-9a-f]{40}', args.revision):
    parser.error('--revision must be a full lowercase commit SHA')


def committed(path):
    return subprocess.check_output(
        ['git', 'show', f'{args.revision}:{path}'], cwd=ROOT, text=True)


# Validate required files in the pinned revision, never use unstaged local copies.
for path in ('scripts/cloud/setup.sh', 'scripts/cloud/activate.sh', 'AGENTS.md',
             'requirements-dev.txt', 'notifications/test/browser.py'):
    committed(path)
install = committed('scripts/cloud/install.sh')
start = committed('.agents/skills/yuika-cloud-start/SKILL.md')
start = start.replace(
    '# Start yuika-study in Codex Cloud\n',
    '# Start yuika-study in Codex Cloud\n\n'
    f'This saved version requires commit `{args.revision}`. Before manual setup, '
    'confirm the install receipt has that exact `required_revision` and run '
    f'`git merge-base --is-ancestor {args.revision} HEAD` in the dedicated checkout. '
    'A newer topic branch containing this commit is valid; never reset it.\n',
    1,
)
rendered = (
    '# yuika-study saved environment Install script; no initial checkout dependency.\n'
    f'# Reviewed revision: {args.revision}\n'
    f"bash -s -- '{args.revision}' /workspace/yuika-study-cloud <<'YUIKA_CLOUD_INSTALL'\n"
    + install + 'YUIKA_CLOUD_INSTALL\n'
)
args.output.mkdir(parents=True, exist_ok=True)
(args.output / 'install.sh').write_text(rendered)
(args.output / 'start-skill.md').write_text(start)
print(f'Rendered revision {args.revision}: {args.output}')
