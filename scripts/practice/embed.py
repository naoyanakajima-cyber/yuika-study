"""Keep the standalone HTML apps self-contained under the preview CSP."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
START = '// ADAPTIVE_START\n'
END = '// ADAPTIVE_END\n'
body = (Path(__file__).with_name('adaptive.js')).read_text()
for name in ('onin-review.html', 'kamakura-review.html'):
    path = ROOT / name
    text = path.read_text()
    if START in text:
        before, rest = text.split(START)
        _, after = rest.split(END)
    else:
        before, after = text.split('load();render();')
        after = 'load();render();' + after
    path.write_text(before + START + body + END + after)
