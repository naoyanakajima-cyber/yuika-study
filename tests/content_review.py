"""Synthetic proposal review workflow; no real input, notification or storage writes."""
import copy
import json
import os
import runpy
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'docs/product/fixtures'
Handler = runpy.run_path(str(ROOT / 'scripts/cloud/serve.py'))['PreviewHandler']


class Probe(Handler):
    posts = 0

    def log_message(self, *args):
        pass

    def do_POST(self):
        type(self).posts += 1
        self.send_error(405)


TEXT = json.loads((FIXTURES / 'synthetic-content.json').read_text())
IMAGE = json.loads((FIXTURES / 'synthetic-image-content.json').read_text())
with ThreadingHTTPServer(('127.0.0.1', 0), partial(Probe, directory=str(ROOT))) as server:
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as pw:
            with pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH')) as browser:
                context = browser.new_context(viewport={'width': 768, 'height': 1024})
                requests = []
                def guard(route):
                    req = route.request
                    if req.method == 'GET' and req.url == base + '/content-review.html':
                        route.continue_()
                    else:
                        requests.append((req.method, req.url))
                        route.abort()
                context.route('**/*', guard)
                context.add_init_script("""(()=>{
                    const set=Storage.prototype.setItem;
                    set.call(localStorage,'yuika-social-540-27-v1','synthetic-history-preserve');
                    set.call(localStorage,'yuika-science-v2','synthetic-science-preserve');
                    window.storageWrites=[];
                    for(const method of ['setItem','removeItem','clear']){
                        const original=Storage.prototype[method];
                        Storage.prototype[method]=function(...args){storageWrites.push(method);return original.apply(this,args);};
                    }
                })()""")
                p = context.new_page()
                errors = []
                dialogs = []
                p.on('pageerror', lambda error: errors.append(str(error)))
                p.on('dialog', lambda dialog: (dialogs.append(dialog.type), dialog.accept()))
                response = p.goto(base + '/content-review.html')
                assert "connect-src 'none'" in response.headers['content-security-policy']
                expect(p.locator('h1')).to_have_text('教材の確認室')
                assert p.evaluate('SAMPLES') == [TEXT, IMAGE]
                assert p.evaluate('ASSETS.text') == (FIXTURES / 'synthetic-source.txt').read_text()
                assert p.evaluate('ASSETS.image') == (FIXTURES / 'synthetic-source.svg').read_text()
                expect(p.locator('#work')).to_be_hidden()
                p.locator('#sample-text').click()
                expect(p.locator('#source-preview')).to_contain_text('水を冷やすと氷になります')
                expect(p.locator('#export-confirmed')).to_be_disabled()
                assert p.evaluate('proposal.questions[0].status') == 'draft'
                p.locator('#confirm-0').click()
                expect(p.locator('#export-confirmed')).to_be_enabled()
                with p.expect_download() as download:
                    p.locator('#export-confirmed').click()
                confirmed = json.loads(Path(download.value.path()).read_text())
                assert download.value.suggested_filename.startswith('confirmed-')
                assert confirmed['questions'][0]['confirmedRevision'] == confirmed['revision']
                assert confirmed['questions'][0]['status'] == 'confirmed'

                def upload(value):
                    p.locator('#import').set_input_files({'name': 'synthetic.json', 'mimeType': 'application/json', 'buffer': json.dumps(value, ensure_ascii=False).encode()})
                    expect(p.locator('#import')).to_have_value('')

                # Re-imported confirmation has no authority; content remains intact.
                upload(confirmed)
                expect(p.locator('#status-0')).to_have_text('未確認')
                assert p.evaluate('proposal.questions[0].answer') == confirmed['questions'][0]['answer']
                assert p.evaluate('proposal.questions[0].confirmedRevision') is None
                p.locator('#confirm-0').click()
                revision = p.evaluate('proposal.revision')
                p.locator('#q-0-answer').fill('こおり')
                assert p.evaluate('proposal.revision') > revision
                expect(p.locator('#status-0')).to_have_text('未確認')
                expect(p.locator('#export-confirmed')).to_be_disabled()
                with p.expect_download() as download:
                    p.locator('#export-draft').click()
                draft = json.loads(Path(download.value.path()).read_text())
                assert download.value.suggested_filename.startswith('draft-')
                assert draft['questions'][0]['status'] == 'draft' and draft['questions'][0]['confirmedRevision'] is None

                # Structure failures preserve the current proposal, not a partially parsed value.
                baseline = p.evaluate('proposal')
                for invalid in [{'schemaVersion': 1, 'events': []}, {**TEXT, 'extra': True}, {**TEXT, 'questions': [{**TEXT['questions'][0], 'type': 'unknown'}]}, {**TEXT, 'unit': None}]:
                    upload(invalid)
                    expect(p.locator('#notice')).to_contain_text('読み込みを中止')
                    assert p.evaluate('proposal') == baseline

                valid_choice = copy.deepcopy(TEXT)
                valid_choice['questions'][0].update(type='choice', options=['氷', '水'], readings=[])
                upload(valid_choice)
                expect(p.locator('#confirm-0')).to_be_enabled()
                p.locator('#confirm-0').click()
                expect(p.locator('#export-confirmed')).to_be_enabled()

                # Content problems remain editable drafts but cannot be confirmed.
                cases = []
                duplicate = copy.deepcopy(TEXT)
                duplicate['questions'].append(copy.deepcopy(duplicate['questions'][0]))
                cases.append(duplicate)
                for patch in [{'answer': None}, {'id': '54027-01'}, {'sourceRefs': [{'sourceId': 'unknown', 'locator': 'lines:1'}]}, {'type': 'choice', 'options': ['氷', '氷'], 'readings': []}, {'type': 'choice', 'options': ['水', '湯'], 'readings': []}]:
                    value = copy.deepcopy(TEXT)
                    value['questions'][0].update(patch)
                    cases.append(value)
                for value in cases:
                    upload(value)
                    expect(p.locator('#notice')).to_contain_text('読み込みました')
                    expect(p.locator('#confirm-0')).to_be_disabled()
                    expect(p.locator('#export-confirmed')).to_be_disabled()

                # Every accepted draft remains repairable in the page, even empty references.
                repair = copy.deepcopy(TEXT)
                repair['packageId'] = 'bad'
                repair['source']['kind'] = 'image'
                repair['questions'][0]['sourceRefs'] = []
                repair['questions'][0]['generatedFields'].append('unknown')
                upload(repair)
                p.locator('#metadata summary').click()
                p.locator('#package-id').fill('draft-repaired-synthetic')
                p.locator('#source-kind').select_option('text')
                p.locator('#questions summary').click()
                p.locator('#q-0-add-ref').click()
                p.locator('#q-0-ref-0-locator').fill('lines:1-1')
                p.locator('#q-0-apply-generated').click()
                expect(p.locator('#confirm-0')).to_be_enabled()
                p.locator('#confirm-0').click()
                p.locator('#q-0-generated-prompt').uncheck()
                expect(p.locator('#status-0')).to_have_text('未確認')
                expect(p.locator('#export-confirmed')).to_be_disabled()

                # Editing any category invalidates all confirmation, including a second question.
                multiple = copy.deepcopy(TEXT)
                multiple['questions'].append({**copy.deepcopy(TEXT['questions'][0]), 'id': 'draft-synthetic-water-002'})
                upload(multiple)
                for selector in ['#q-0-prompt', '#unit-title', '#source-label', '#transcription', '#q-0-ref-0-locator']:
                    p.locator('#confirm-0').click()
                    p.locator('#confirm-1').click()
                    expect(p.locator('#export-confirmed')).to_be_enabled()
                    old = p.evaluate('proposal.revision')
                    field = p.locator(selector)
                    # Expand containing details if needed.
                    field.evaluate("el=>{for(let n=el.parentElement;n;n=n.parentElement)if(n.tagName==='DETAILS')n.open=true}")
                    field.fill(field.input_value() + ' 合成')
                    assert p.evaluate('proposal.revision') > old
                    assert p.evaluate('proposal.questions.every(q=>q.status==="draft"&&q.confirmedRevision===null)')
                    expect(p.locator('#export-confirmed')).to_be_disabled()

                # Unknown source and markup are text only, never navigation or HTML execution.
                injection = copy.deepcopy(TEXT)
                injection['questions'][0]['prompt'] = '<img src="https://example.invalid/image" onerror="window.injected=true">'
                injection['source']['locator'] = 'https://example.invalid/' + 'x' * 170
                injection['questions'][0]['generatedFields'].append('x' * 300)
                upload(injection)
                assert p.locator('#q-0-prompt').input_value() == injection['questions'][0]['prompt']
                expect(p.locator('#source-meta')).to_contain_text(injection['source']['locator'])
                assert p.evaluate('document.documentElement.scrollWidth <= innerWidth')
                assert not p.evaluate('Boolean(window.injected)')
                assert p.locator('#questions img').count() == 0

                # Image fixture is hand-authored; missing answer and unresolved text block all.
                p.locator('#sample-image').click()
                expect(p.locator('#source-preview svg')).to_be_visible()
                expect(p.locator('#source-preview')).to_contain_text('OCRは実行していません')
                expect(p.locator('#confirm-0')).to_be_disabled()
                p.locator('#q-0-answer').fill('東')
                p.locator('#q-0-explanation').fill('太陽は東からのぼるという合成の説明です。')
                p.locator('#q-0-hint').fill('朝の方角を確認しよう。')
                expect(p.locator('#confirm-0')).to_be_disabled()
                p.locator('#resolution-0').fill('東')
                expect(p.locator('#confirm-0')).to_be_enabled()
                p.locator('#confirm-0').click()
                expect(p.locator('#export-confirmed')).to_be_enabled()
                p.locator('#resolution-0').fill('')
                expect(p.locator('#confirm-0')).to_be_disabled()
                assert p.evaluate('proposal.transcription.uncertainties[0].quote') == '［判読不明］'
                assert p.evaluate('document.documentElement.scrollWidth <= innerWidth')
                p.locator('#cancel').click()
                expect(p.locator('#work')).to_be_hidden()
                assert 'confirm' in dialogs
                p.locator('#sample-text').click()
                p.locator('#q-0-hint').fill('未保存の合成編集')
                assert p.evaluate('storageWrites') == []
                assert p.evaluate('localStorage.getItem("yuika-social-540-27-v1")') == 'synthetic-history-preserve'
                assert p.evaluate('localStorage.getItem("yuika-science-v2")') == 'synthetic-science-preserve'
                p.reload()
                assert 'beforeunload' in dialogs
                expect(p.locator('#work')).to_be_hidden()
                assert p.evaluate('localStorage.getItem("yuika-social-540-27-v1")') == 'synthetic-history-preserve'
                assert p.evaluate('localStorage.getItem("yuika-science-v2")') == 'synthetic-science-preserve'
                assert p.evaluate('storageWrites') == []
                assert not requests, requests
                assert Probe.posts == 0
                assert not errors, errors
                print('content-review: C1-C11 synthetic workflow passed; external requests 0; POST arrivals 0; storage writes 0')
    finally:
        server.shutdown()
        thread.join()
