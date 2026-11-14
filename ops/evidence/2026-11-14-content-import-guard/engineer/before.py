import json,os,runpy
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
root=Path.cwd(); H=runpy.run_path('scripts/cloud/serve.py')['PreviewHandler']
with ThreadingHTTPServer(('127.0.0.1',0),partial(H,directory=str(root))) as s:
 Thread(target=s.serve_forever,daemon=True).start()
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path=os.environ['PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH']);p=b.new_page(viewport={'width':768,'height':1024});p.on('dialog',lambda d:d.accept());p.goto(f'http://127.0.0.1:{s.server_port}/content-review.html');p.locator('#sample-text').click()
  p.evaluate('window.reads=[];File.prototype.text=function(){return new Promise((resolve,reject)=>reads.push({resolve,reject}));};void 0')
  p.locator('#import').set_input_files({'name':'synthetic.json','mimeType':'application/json','buffer':b'{}'})
  p.locator('#q-0-prompt').fill('合成編集を保持してください')
  before=p.evaluate('({proposal,unsaved})');p.evaluate('reads[0].resolve(JSON.stringify(SAMPLES[0]))');p.wait_for_function('document.getElementById("import").value === ""');after=p.evaluate('({proposal,unsaved})')
  assert before['proposal']['questions'][0]['prompt']!=after['proposal']['questions'][0]['prompt']
  Path('/tmp/yuika-content-import-engineer/before.json').write_text(json.dumps({'base':'f1e84a7','reproduced':'deferred File.text completion overwrites actual DOM edit after discard accepted','before':before,'after':after},ensure_ascii=False,indent=2))
  p.screenshot(path='/tmp/yuika-content-import-engineer/before.png');b.close()
 s.shutdown()
print('PASS baseline defect reproduced using deferred synthetic File.text and DOM input')
