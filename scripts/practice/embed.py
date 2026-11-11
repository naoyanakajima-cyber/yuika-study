"""Keep the standalone HTML apps self-contained under the preview CSP."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
START = '// ADAPTIVE_START\n'
END = '// ADAPTIVE_END\n'
body = (Path(__file__).with_name('adaptive.js')).read_text()
for name in ('onin-review.html', 'kamakura-review.html', 'heian-review.html', 'mock-focus-review.html'):
    path = ROOT / name
    text = path.read_text()
    if START in text:
        before, rest = text.split(START)
        _, after = rest.split(END)
    else:
        before, after = text.split('load();render();')
        after = 'load();render();' + after
    app_body = body
    if name == 'mock-focus-review.html':
        app_body = body.replace('読みと漢字は別々に数えます。', '')
        app_body = app_body.replace('平安は暗記＝基本、ペア・流れ＝標準、理由＝発展です。', '各問題に登録されたむずかしさで絞り込みます。')
    path.write_text(before + START + app_body + END + after)
