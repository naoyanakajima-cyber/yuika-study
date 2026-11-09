"""Synthetic, keyboard-accessible discovery of recommendations on both unit homes."""
import ast
import importlib.util
import os
from datetime import datetime, timezone
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('preview', ROOT / 'scripts/cloud/serve.py')
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)


class Quiet(preview.PreviewHandler):
    posts = 0

    def log_message(self, *args):
        pass

    def do_POST(self):
        type(self).posts += 1
        self.send_error(405)


# Reuse only the validated synthetic-event builder, without executing its test suite.
seed = next(ast.literal_eval(n.value) for n in ast.parse((ROOT / 'tests/recommended_review.py').read_text()).body
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SEED' for t in n.targets))
server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{server.server_port}/'


def unchanged(page, before):
    assert page.evaluate('localStorage.getItem(KEY)') == before
    assert page.evaluate('run') is None
    assert page.evaluate('screen') == 'home'


def in_view(locator):
    box = locator.bounding_box()
    assert box and 0 <= box['y'] and box['y'] + box['height'] <= 1024, box
    assert 0 <= box['x'] and box['x'] + box['width'] <= 768, box


try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
        for filename in ('onin-review.html', 'kamakura-review.html'):
            context = browser.new_context(viewport={'width': 768, 'height': 1024})
            outgoing = []

            def route_request(route):
                r = route.request
                if r.method == 'GET' and r.url.startswith(base):
                    route.continue_()
                else:
                    outgoing.append((r.method, r.url))
                    route.abort()

            context.route('**/*', route_request)
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.clock.set_fixed_time(datetime(2030, 1, 3, tzinfo=timezone.utc))
            page.goto(base + filename)
            entry = page.locator('#recommendation-entry')
            status = page.locator('#recommendation-entry-status')
            in_view(entry)
            expect(status).to_contain_text('通常練習や未回答の問題も選べます')
            before = page.evaluate('localStorage.getItem(KEY)')
            entry.focus()
            entry.press('Enter')
            expect(page.locator('#course')).to_be_focused()
            in_view(page.locator('#course'))
            unchanged(page, before)

            # Candidate-rich data lets each setting change exercise fresh counts and focus.
            ids = page.evaluate('QUESTIONS.map(q=>q.id)')
            page.evaluate(seed, [{'id': qid} for qid in ids])
            before = page.evaluate('localStorage.getItem(KEY)')
            in_view(entry)
            expect(status).to_contain_text(f'候補 {len(ids)}問')
            for field, value in [('course', 'd2'), ('unit', page.evaluate('UNITS.at(-1)')), ('variant', 'kanji')]:
                page.locator('#' + field).select_option(value)
                expect(page.locator('#' + field)).to_be_focused()
                assert page.evaluate('document.activeElement.matches(":focus-visible")')
                n = page.evaluate('recommendedPlan().length')
                if n:
                    expect(status).to_contain_text(f'候補 {n}問')
                else:
                    expect(status).to_contain_text('今の条件でおすすめする復習はありません')
                unchanged(page, before)
            page.locator('[data-count="10"]').click()
            expect(page.locator('[data-count="10"]')).to_be_focused()
            unchanged(page, before)

            # A single candidate: guidance focuses the destination, but does not start/save.
            page.evaluate("prefs={count:5,course:'all',unit:'all',variant:'normal'}")
            page.evaluate(seed, [{'id': ids[0]}])
            before = page.evaluate('localStorage.getItem(KEY)')
            in_view(entry)
            expect(status).to_contain_text('候補 1問 · 今回は 1問')
            entry.focus()
            entry.press('Enter')
            title = page.locator('#recommended-title')
            expect(title).to_be_focused()
            in_view(title)
            assert title.evaluate("e=>getComputedStyle(e).outlineStyle !== 'none'")
            unchanged(page, before)
            page.keyboard.press('Tab')
            expect(page.locator('#recommended-start')).to_be_focused()
            page.keyboard.press('Enter')
            assert page.evaluate('run.recommended') is True
            assert page.evaluate('localStorage.getItem(KEY)') == before
            q = page.evaluate('run.qs[run.index]')
            if q['type'] == 'text':
                page.locator('#response').fill(q['answer'])
            else:
                page.locator('[data-choice]').filter(has_text=q['answer']).first.click()
            page.locator('#check').click()
            expect(page.locator('#feedback')).to_contain_text('回答を保存しました')
            saved = page.evaluate('localStorage.getItem(KEY)')
            assert page.evaluate('data.events.length') == 2
            page.reload()
            assert page.evaluate('localStorage.getItem(KEY)') == saved
            expect(status).to_contain_text('今の条件でおすすめする復習はありません')
            # Browsers may restore the pre-reload scroll position; inspect the home top explicitly.
            page.evaluate('window.scrollTo(0,0)')
            in_view(entry)

            # Invalid history is not ordinary zero candidates and stays byte-for-byte intact.
            page.evaluate("localStorage.setItem(KEY,'{synthetic-broken')")
            page.reload()
            expect(status).to_contain_text('記録を読み取れないため')
            expect(status).not_to_contain_text('候補 0問')
            before = page.evaluate('localStorage.getItem(KEY)')
            entry.focus()
            entry.press('Enter')
            expect(page.locator('#recommended-title')).to_be_focused()
            expect(page.locator('#recommended-start')).to_be_disabled()
            unchanged(page, before)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            assert not outgoing, outgoing
            assert not errors, errors
            context.close()
        browser.close()
    assert Quiet.posts == 0
    print('Review entry: both units, viewport, keyboard, filters, empty/broken records, persistence and notification blocking passed')
finally:
    server.shutdown()
    server.server_close()
