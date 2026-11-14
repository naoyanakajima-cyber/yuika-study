"""Verify the cloud preview blocks APIs and cannot serve private workspace files."""
import os
import runpy
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
PreviewHandler = runpy.run_path(str(ROOT / 'scripts/cloud/serve.py'))['PreviewHandler']


class ProbeHandler(PreviewHandler):
    posts = 0

    def log_message(self, *args):
        pass

    def do_POST(self):
        type(self).posts += 1
        self.send_response(204)
        self.end_headers()


with ThreadingHTTPServer(('127.0.0.1', 0), partial(ProbeHandler, directory=str(ROOT))) as server:
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    try:
        for path in ('/.git/config', '/private-data/answers.json', '/requirements-dev.txt',
                     '/assets/', '/assets/unknown.js', '/docs/product/fixtures/synthetic-content.json',
                     '/content-review.html/../README.md', '/%2egit/config', '/'):
            try:
                with urlopen(base + path) as response:
                    assert path == '/' and response.status == 200
                    response.read()
            except HTTPError as error:
                assert path != '/' and error.code == 404
                error.read()
                error.close()
        for name in ('index.html', 'heian-review.html', 'onin-review.html',
                     'kamakura-review.html', 'yuika-review-v2.html', 'mock-focus-review.html',
                     'content-review.html', 'assets/design.css', 'assets/design.js', 'assets/progress.js'):
            with urlopen(f'{base}/{name}') as response:
                assert response.status == 200, name
                assert response.read() == (ROOT / name).read_bytes(), name
                assert response.headers['Cache-Control'] == 'no-store', name
                csp = response.headers['Content-Security-Policy']
                for directive in ("connect-src 'none'", "form-action 'none'", "object-src 'none'"):
                    assert directive in csp, (name, directive)
            try:
                with urlopen(Request(f'{base}/{name}', method='HEAD')):
                    raise AssertionError(f'HEAD unexpectedly allowed: {name}')
            except HTTPError as error:
                assert error.code == 405, name
                error.close()
        with sync_playwright() as pw:
            with pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH')) as browser:
                context = browser.new_context(viewport={'width': 768, 'height': 1024})
                context.route('https://**/*', lambda route: route.abort())
                context.add_init_script(path=str(ROOT / 'tests/seed_random.js'))
                page = context.new_page()
                for name, title in (('onin-review.html', '応仁の乱'), ('kamakura-review.html', '鎌倉幕府の成立'), ('mock-focus-review.html', '模試の弱点対策'), ('content-review.html', '教材の確認室')):
                    response = page.goto(f'{base}/{name}')
                    assert "connect-src 'none'" in response.headers['content-security-policy']
                    expect(page.locator('h1')).to_have_text(title)
                    blocked = page.evaluate('''async () => {
                        window.violations = [];
                        document.addEventListener('securitypolicyviolation', e => violations.push(e.effectiveDirective));
                        try { await fetch('/notification-probe', {method: 'POST', body: 'synthetic'}); return false; }
                        catch { return true; }
                    }''')
                    assert blocked
                    page.wait_for_function("violations.includes('connect-src')")
                assert ProbeHandler.posts == 0, 'API traffic escaped preview CSP'
    finally:
        server.shutdown()
        thread.join()
print('cloud-preview: startup, private path protection, and API blocking passed')
