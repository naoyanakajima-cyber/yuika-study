"""Real regeneration must preserve committed app behavior and be repeatable.

Run in a temporary tracked-file copy: this suite must not rewrite the checkout.
Comparing the first pass matters: idempotence alone permits a stable regression.
"""
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
GENERATORS = (
    'scripts/practice/embed.py',
    'scripts/practice/embed_science.py',
    'scripts/history/embed.py',
    'scripts/prototype/embed.py',
    'scripts/design/build_summary.py',
    'scripts/design/embed.py',
    'scripts/parent/embed.py',
)


def snapshot(root, names):
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in names}


def main():
    names = subprocess.check_output(
        ['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')[:-1]
    expected = snapshot(ROOT, names)
    with TemporaryDirectory(prefix='yuika-generator-regression-') as directory:
        isolated = Path(directory)
        for name in names:
            target = isolated / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        previous = expected
        for attempt in (1, 2):
            for generator in GENERATORS:
                subprocess.run([sys.executable, generator], cwd=isolated,
                               check=True, capture_output=True, text=True)
            actual = snapshot(isolated, names)
            changed = [name for name in names if actual[name] != previous[name]]
            assert not changed, f'Generator pass {attempt} changed tracked files: {changed}'
            previous = actual
    assert snapshot(ROOT, names) == expected, 'Test modified its source checkout'
    print('generator_preservation: seven generators preserve all tracked files; second pass unchanged PASS')


if __name__ == '__main__':
    main()
