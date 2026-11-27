"""Readable synthetic image: manual reconciliation, trusted source binding and trial."""
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
FIXTURES = ROOT / 'docs/product/fixtures'
TRIANGLE = json.loads((FIXTURES / 'synthetic-triangle-content.json').read_text())
OLD_IMAGE = json.loads((FIXTURES / 'synthetic-image-content.json').read_text())
TEXT = json.loads((FIXTURES / 'synthetic-content.json').read_text())
Handler = runpy.run_path(str(ROOT / 'scripts/cloud/serve.py'))['PreviewHandler']

class Quiet(Handler):
    def log_message(self, *args):
        pass

with ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT))) as server:
    Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/content-review.html'
    try:
        with sync_playwright() as pw:
            with pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH')) as browser:
                ctx = browser.new_context(viewport={'width': 768, 'height': 1024})
                network = []
                ctx.route('**/*', lambda r: r.continue_() if r.request.method == 'GET' and r.request.url == url else (network.append(r.request.url), r.abort()))
                ctx.add_init_script("""(()=>{
                  window.writes=[];
                  for(const n of ['setItem','removeItem','clear'])Storage.prototype[n]=()=>{writes.push(n);throw Error('storage write');};
                  for(const n of ['pushState','replaceState'])history[n]=()=>{writes.push(n);throw Error('history write');};
                  Object.defineProperty(document,'cookie',{get:()=>'',set:()=>{writes.push('cookie');throw Error('cookie write');}});
                  indexedDB.open=()=>{writes.push('indexedDB');throw Error('database open');};
                })()""")
                p = ctx.new_page()
                errors = []
                dialogs = []
                p.on('pageerror', lambda e: errors.append(str(e)))
                dismiss = [False]
                def dialog(d):
                    dialogs.append(d.type)
                    d.dismiss() if dismiss[0] else d.accept()
                p.on('dialog', dialog)
                p.goto(url)
                def state():
                    return p.evaluate('({proposal,unsaved})')
                def source_text():
                    return p.locator('#source-preview').inner_text()
                def upload(value):
                    p.locator('#import').set_input_files({'name': 'synthetic.json', 'mimeType': 'application/json', 'buffer': json.dumps(value, ensure_ascii=False).encode()})
                    expect(p.locator('#import')).to_have_value('')
                def export(selector):
                    with p.expect_download() as dl:
                        p.locator(selector).click()
                    return json.loads(Path(dl.value.path()).read_text())
                # Existing unsaved-discard boundary also applies to the new entry.
                p.locator('#sample-text').click()
                saved = state()
                dismiss[0] = True
                p.locator('#sample-triangle').click()
                assert state() == saved
                dismiss[0] = False
                p.locator('#sample-triangle').focus()
                p.keyboard.press('Enter')
                expect(p.locator('#workflow-title')).to_be_focused()
                assert p.evaluate('proposal') == TRIANGLE
                expect(p.locator('#source-preview svg')).to_have_attribute('viewBox', '0 0 600 320')
                expect(p.locator('#source-preview')).to_contain_text('三角形の辺は3本です。')
                expect(p.locator('#source-preview')).to_contain_text('合成の転記案')
                expect(p.locator('#source-preview')).to_contain_text('OCR結果ではありません')
                assert p.locator('#source-preview path').get_attribute('d') == 'M 300 70 L 180 220 L 420 220 Z'
                box = p.locator('#source-preview svg').bounding_box()
                assert box and box['width'] > 280 and box['x'] >= 0 and box['x'] + box['width'] <= 768
                assert p.evaluate('document.documentElement.scrollWidth <= innerWidth')
                expect(p.locator('#confirm-0')).to_be_disabled()
                expect(p.locator('#trial-start')).to_be_disabled()
                p.locator('#next-step').click()
                expect(p.locator('#resolution-0')).to_be_focused()
                draft = export('#export-draft')
                assert draft == TRIANGLE and draft['schemaVersion'] == 1
                upload(draft)
                assert '三角形の辺は3本です。' in source_text()
                # Deliberately manual steps: no semantic automatic matching is asserted.
                rev = p.evaluate('proposal.revision')
                p.locator('#transcription').fill('三角形の辺は3本です。')
                assert p.evaluate('proposal.revision') > rev
                expect(p.locator('#confirm-0')).to_be_disabled()
                rev = p.evaluate('proposal.revision')
                p.locator('#resolution-0').fill('3')
                assert p.evaluate('proposal.revision') > rev
                expect(p.locator('#confirm-0')).to_be_enabled()
                expect(p.locator('#trial-start')).to_be_disabled()
                assert p.evaluate('proposal.transcription.uncertainties[0]') == {**TRIANGLE['transcription']['uncertainties'][0], 'resolution': '3'}
                p.locator('#confirm-0').focus()
                p.keyboard.press('Enter')
                expect(p.locator('#trial-start')).to_be_enabled()
                confirmed = p.evaluate('proposal')
                for answer, result in [('3', '登録した答えに一致しました'), ('4', '登録した答えとは一致しません')]:
                    saved = state()
                    p.locator('#trial-start').click()
                    expect(p.locator('#trial-title')).to_be_focused()
                    expect(p.locator('#editor')).to_be_hidden()
                    assert p.locator('#editor').evaluate('e=>e.inert')
                    p.evaluate('acceptProposal(SAMPLES[0]);exportProposal(false);changed(()=>proposal.unit.title="forbidden")')
                    assert state() == saved
                    p.locator('#trial-answer').fill(answer)
                    p.locator('#trial-grade').click()
                    expect(p.locator('#trial-result')).to_have_text(result)
                    p.locator('#trial-exit').click()
                    assert p.evaluate('trial') is None and p.locator('#trial-panel').inner_html() == ''
                    assert state() == saved
                    expect(p.locator('#trial-start')).to_be_focused()
                output = export('#export-confirmed')
                assert output == confirmed and set(output) == set(TRIANGLE)
                assert output['questions'][0]['status'] == 'confirmed'
                assert output['questions'][0]['confirmedRevision'] == output['revision']
                assert output['source'] == TRIANGLE['source']
                p.locator('#q-0-hint').fill('線を数えよう。')
                expect(p.locator('#trial-start')).to_be_disabled()
                assert p.evaluate('proposal.questions[0].confirmedRevision') is None
                upload(output)
                expect(p.locator('#trial-start')).to_be_disabled()
                assert p.evaluate('proposal.questions[0].status') == 'draft'
                assert '三角形の辺は3本です。' in source_text()
                # Both sample switches and JSON imports bind to the exact known source.
                for selector, value, marker in [('#sample-image', OLD_IMAGE, '太陽は［判読不明］からのぼります。'), ('#sample-triangle', TRIANGLE, '三角形の辺は3本です。'), ('#sample-text', TEXT, '水を冷やすと氷になります。')]:
                    p.locator(selector).click()
                    assert p.evaluate('proposal') == value
                    assert marker in source_text()
                    upload(value)
                    assert marker in source_text()
                    if value['source']['kind'] == 'text':
                        assert p.locator('#source-preview svg').count() == 0
                    else:
                        expect(p.locator('#confirm-0')).to_be_disabled()
                        expect(p.locator('#trial-start')).to_be_disabled()
                # Each mismatch of the source triple is refused, never loaded as a URL/SVG.
                for key, wrong in [('kind', 'text'), ('sourceId', 'unknown-source'), ('locator', 'synthetic-source.svg'), ('locator', 'https://example.invalid/source.svg')]:
                    bad = copy.deepcopy(output)
                    bad['source'][key] = wrong
                    upload(bad)
                    assert p.locator('#source-preview svg').count() == 0
                    expect(p.locator('#source-preview')).to_contain_text('対応する同梱原本がありません')
                    expect(p.locator('#confirm-0')).to_be_disabled()
                    expect(p.locator('#trial-start')).to_be_disabled()
                assert p.evaluate('writes') == [] and network == [] and errors == []
                assert 'confirm' in dialogs
                ctx.close()
    finally:
        server.shutdown()
print('content-image-trial: manual reconciliation, match/mismatch, memory erasure, JSON roundtrip, exact trusted source binding and negative gates passed')
