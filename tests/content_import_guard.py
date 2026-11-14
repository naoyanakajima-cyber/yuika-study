"""Synthetic deferred File.text races through real file inputs and editor controls."""
import json
import os
import runpy
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
Handler = runpy.run_path(str(ROOT / 'scripts/cloud/serve.py'))['PreviewHandler']


class Probe(Handler):
    def log_message(self, *args):
        pass


with ThreadingHTTPServer(('127.0.0.1', 0), partial(Probe, directory=str(ROOT))) as server:
    Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
            context = browser.new_context(viewport={'width': 768, 'height': 1024})
            unexpected = []
            def guard(route):
                if route.request.method == 'GET' and route.request.url == base + '/content-review.html':
                    route.continue_()
                else:
                    unexpected.append(route.request.url)
                    route.abort()
            context.route('**/*', guard)
            context.add_init_script("""(()=>{
                window.storageWrites=[];
                for(const name of ['setItem','removeItem','clear']) Storage.prototype[name]=function(){storageWrites.push(name);throw Error('Storage write');};
                window.reads=[];
                File.prototype.text=function(){return new Promise((resolve,reject)=>reads.push({resolve,reject}));};
            })()""")
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            dialog_accept = True
            page.on('dialog', lambda dialog: dialog.accept() if dialog_accept else dialog.dismiss())
            page.goto(base + '/content-review.html')
            def start(name='synthetic.json'):
                index = page.evaluate('reads.length')
                page.locator('#import').set_input_files({'name': name, 'mimeType': 'application/json', 'buffer': b'{}'})
                expect(page.locator('#import-status')).to_contain_text('読み込み中')
                expect(page.locator('#cancel-import')).to_be_visible()
                return index
            def resolve(index, sample=0, invalid=False):
                page.evaluate('([i,s,bad])=>{reads[i].resolve(bad?"{":JSON.stringify(SAMPLES[s]));}', [index,sample,invalid])
            def state():
                return page.evaluate('({proposal,unsaved})')
            def sample():
                page.locator('#sample-text').click()
            def idle():
                expect(page.locator('#import')).to_have_value('')
                expect(page.locator('#cancel-import')).to_be_hidden()
                assert not page.evaluate('pendingImport')
            # Import from empty state, then reject stale results after each real operation.
            a = start(); resolve(a); idle()
            for action in ['edit', 'confirm', 'export', 'sample', 'cancel']:
                sample(); a = start()
                if action == 'edit':
                    page.locator('#q-0-prompt').fill('合成編集を保持してください')
                elif action == 'confirm':
                    page.locator('#confirm-0').click()
                elif action == 'export':
                    with page.expect_download() as download:
                        page.locator('#export-draft').click()
                    assert json.loads(Path(download.value.path()).read_text())['format'] == 'yuika-content-proposal'
                elif action == 'sample':
                    page.locator('#sample-image').click()
                else:
                    page.locator('#cancel').click()
                held = state(); resolve(a); idle()
                assert state() == held, action
                expect(page.locator('#notice')).to_contain_text('案が変わったため再入力')
            # Superseded completion/error cannot clear the newer pending/input/status.
            for failure in [False, True]:
                sample(); a = start('a.json'); b = start('b.json')
                status = page.locator('#import-status').inner_text()
                if failure:
                    page.evaluate('(i)=>{reads[i].reject(Error("synthetic read failure"));}', a)
                else:
                    resolve(a, 1)
                assert page.evaluate('pendingImport')
                assert page.locator('#import-status').inner_text() == status
                assert page.locator('#import').input_value().endswith('b.json')
                assert page.locator('#notice').inner_text() == ''
                resolve(b); idle()
            sample(); a = start(); b = start(); resolve(b,1); idle(); held = state(); resolve(a); assert state() == held
            # A failed newer read never revives the older read.
            for failure in ['invalid', 'reject', 'oversize']:
                sample(); held = state(); a = start()
                if failure == 'oversize':
                    page.locator('#import').set_input_files({'name':'large.json','mimeType':'application/json','buffer':b' '*200001})
                else:
                    b = start()
                    if failure == 'invalid':
                        resolve(b, invalid=True)
                    else:
                        page.evaluate('(i)=>{reads[i].reject(Error("synthetic failure"));}', b)
                idle(); expect(page.locator('#notice')).to_contain_text('読み込みを中止')
                message = page.locator('#notice').inner_text(); resolve(a,1)
                assert state() == held
                assert page.locator('#notice').inner_text() == message
            # Explicit cancellation and empty-files change invalidate pending reads.
            for empty in [False, True]:
                sample(); held = state(); a = start()
                if empty:
                    page.locator('#import').set_input_files([])
                else:
                    page.locator('#cancel-import').click()
                    expect(page.locator('#import')).to_be_focused()
                idle(); resolve(a,1); assert state() == held
                expect(page.locator('#notice')).to_contain_text('読み込みを取り消しました')
            # Refused replacement/cancellation has no authority to mutate the proposal.
            sample(); page.locator('#confirm-0').click(); held = state(); a = start()
            dialog_accept = False
            page.locator('#cancel').click(); assert state() == held
            resolve(a,1); idle(); assert state() == held
            dialog_accept = True
            a = start(); resolve(a); idle()
            assert page.evaluate('proposal.questions.every(q=>q.status==="draft"&&q.confirmedRevision===null)')
            assert page.evaluate('storageWrites') == []
            assert unexpected == [] and errors == [], (unexpected, errors)
            browser.close()
    finally:
        server.shutdown()
print('PASS content import generations: edits/confirm/export/switch/cancel, both read orders, stale failures, failed replacement, discard refusal, memory-only')
