"""Synthetic guidance: next action, explicit confirmation, focus and no side effects."""
import copy
import json
import os
import runpy
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
TEXT = json.loads((ROOT / 'docs/product/fixtures/synthetic-content.json').read_text())
IMAGE = json.loads((ROOT / 'docs/product/fixtures/synthetic-image-content.json').read_text())
Handler = runpy.run_path(str(ROOT / 'scripts/cloud/serve.py'))['PreviewHandler']


class Quiet(Handler):
    posts = 0
    def log_message(self, *args):
        pass
    def do_POST(self):
        type(self).posts += 1
        self.send_error(405)


with ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT))) as server:
    Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}/content-review.html'
    try:
        with sync_playwright() as pw:
            with pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH')) as browser:
                context = browser.new_context(viewport={'width': 768, 'height': 1024})
                requests, errors, downloads = [], [], []
                def guard(route):
                    if route.request.method == 'GET' and route.request.url == base:
                        route.continue_()
                    else:
                        requests.append(route.request.url)
                        route.abort()
                context.route('**/*', guard)
                context.add_init_script("""(() => {
                    localStorage.setItem('synthetic-history', 'preserve');
                    window.storageWrites=[];
                    for (const k of ['setItem','removeItem','clear']) {
                        const old=Storage.prototype[k];
                        Storage.prototype[k]=function(...a){storageWrites.push(k);return old.apply(this,a)};
                    }
                })()""")
                p = context.new_page()
                p.on('pageerror', lambda e: errors.append(str(e)))
                p.on('download', lambda d: downloads.append(d))
                p.on('dialog', lambda d: d.accept())
                p.goto(base)
                def navigate(target):
                    before = p.evaluate('({proposal,unsaved})')
                    count = len(downloads)
                    p.locator('#next-step').focus()
                    p.locator('#next-step').press('Enter')
                    expect(p.locator('#'+target)).to_be_focused()
                    box = p.locator('#'+target).bounding_box()
                    assert box and 0 <= box['y'] < 1024, box
                    assert p.locator('#'+target).evaluate("e=>getComputedStyle(e).outlineStyle!=='none'")
                    assert p.evaluate('({proposal,unsaved})') == before
                    assert len(downloads) == count
                def upload(value):
                    p.locator('#import').set_input_files({'name':'synthetic.json','mimeType':'application/json','buffer':json.dumps(value).encode()})
                    expect(p.locator('#import')).to_have_value('')

                p.locator('#sample-text').click()
                expect(p.locator('#workflow-title')).to_be_focused()
                expect(p.locator('#workflow-count')).to_have_text('確認済み 0 / 1問')
                for selector in ['#workflow-count','#workflow-next','#next-step']:
                    box=p.locator(selector).bounding_box()
                    assert box and 0<=box['y'] and box['y']+box['height']<=1024, box
                navigate('question-title-0')
                p.locator('#confirm-0').click()
                expect(p.locator('#workflow-count')).to_have_text('確認済み 1 / 1問')
                navigate('export-title')
                with p.expect_download() as download:
                    p.locator('#export-confirmed').click()
                saved=json.loads(Path(download.value.path()).read_text())
                upload(saved)
                expect(p.locator('#workflow-count')).to_have_text('確認済み 0 / 1問')
                navigate('question-title-0')

                multiple=copy.deepcopy(TEXT)
                multiple['questions'].append({**copy.deepcopy(TEXT['questions'][0]),'id':'draft-synthetic-second'})
                upload(multiple)
                p.locator('#confirm-0').click()
                expect(p.locator('#workflow-count')).to_have_text('確認済み 1 / 2問')
                navigate('question-title-1')
                p.locator('#confirm-1').click()
                expect(p.locator('#workflow-count')).to_have_text('確認済み 2 / 2問')
                p.locator('#q-1-hint').fill('合成の編集')
                expect(p.locator('#workflow-count')).to_have_text('確認済み 0 / 2問')
                navigate('question-title-0')
                p.locator('#q-1-answer').fill('')
                expect(p.locator('#workflow-next')).to_contain_text('問題案 2 に修正が必要')
                navigate('issues-1')

                image=copy.deepcopy(IMAGE)
                image['transcription']['uncertainties'].append({**copy.deepcopy(image['transcription']['uncertainties'][0]),'id':'synthetic-uncertainty-002'})
                upload(image)
                expect(p.locator('#workflow-next')).to_contain_text('不明箇所が 2件')
                navigate('resolution-0')
                p.locator('#resolution-0').fill('東')
                expect(p.locator('#workflow-next')).to_contain_text('不明箇所が 1件')
                navigate('resolution-1')
                p.locator('#resolution-1').fill('東')
                expect(p.locator('#workflow-next')).to_contain_text('正答を入力')
                navigate('issues-0')
                p.locator('#q-0-answer').fill('東')
                p.locator('#q-0-explanation').fill('合成の説明')
                p.locator('#q-0-hint').fill('合成のヒント')
                navigate('question-title-0')
                p.locator('#confirm-0').click()
                navigate('export-title')
                p.locator('#resolution-0').fill('')
                expect(p.locator('#workflow-count')).to_have_text('確認済み 0 / 1問')
                navigate('resolution-0')
                p.locator('#cancel').click()
                expect(p.locator('#work')).to_be_hidden()
                p.locator('#sample-text').click()
                expect(p.locator('#workflow-count')).to_have_text('確認済み 0 / 1問')
                assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
                assert p.evaluate('storageWrites')==[]
                assert p.evaluate('localStorage.getItem("synthetic-history")')=='preserve'
                assert not requests and not errors and Quiet.posts==0, (requests,errors,Quiet.posts)
                print('content-guidance: progress, repair/review/export navigation, keyboard, invalidation and no external/storage side effects passed')
    finally:
        server.shutdown()
