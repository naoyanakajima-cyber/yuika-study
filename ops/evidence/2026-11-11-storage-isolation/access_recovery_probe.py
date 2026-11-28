"""Observe pre-existing science read-access recovery; do not modify product."""
import json,os,subprocess,sys
from pathlib import Path
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path('/workspace/yuika-review-storage-isolation-20261111');OUT=Path('/workspace/work/isolation-qa-20261111');sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
class Handler(PreviewHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
rows=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  for sha in ['c5c6c15c4968ee3d04f8a43f273f12bbb3b9b81e',subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()]:
   body=subprocess.check_output(['git','show',sha+':yuika-review-v2.html'],cwd=ROOT)
   ctx=browser.new_context(viewport={'width':768,'height':1024})
   def route(r):
    if r.request.method=='POST' or not r.request.url.startswith(base):r.abort()
    elif r.request.url.endswith('/yuika-review-v2.html'):r.fulfill(status=200,headers={'Content-Type':'text/html','Content-Security-Policy':"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:"},body=body)
    else:r.continue_()
   ctx.route('**/*',route)
   ctx.add_init_script("window.originalGet=Storage.prototype.getItem;Storage.prototype.getItem=function(k){if(k.includes('yuika-science-review-v2'))throw Error('synthetic temporary read refusal');return originalGet.call(this,k);};")
   page=ctx.new_page();page.goto(base+'/yuika-review-v2.html')
   initial=page.evaluate('({blocked,rawBroken,events:state.events.length})')
   page.evaluate('()=>{Storage.prototype.getItem=originalGet;}')
   after=page.evaluate('(()=>{const saved=persist();return {saved,blocked,rawBroken,dirty,stored:localStorage.getItem(KEY)};})()')
   rows.append({'head':sha,'initial':initial,'after_access_restored':after});ctx.close()
  browser.close()
 (OUT/'access-recovery-result.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
finally:server.shutdown()
