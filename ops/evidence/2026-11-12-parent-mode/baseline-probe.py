import json, os, sys
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(sys.argv[1]).resolve()
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=srv.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{srv.server_port}/';results=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH','/usr/bin/chromium'))
  for mode in ('','?parent-check=1'):
   ctx=browser.new_context(viewport={'width':768,'height':1024});p=ctx.new_page();errors=[];network=[]
   p.on('pageerror',lambda e: errors.append(str(e)))
   p.route('**/*',lambda r:r.continue_() if r.request.url.startswith(base) else (network.append(r.request.url),r.abort())[-1])
   ctx.add_init_script("""const original=Storage.prototype.getItem;Storage.prototype.getItem=function(k){if(this===sessionStorage)throw new DOMException('synthetic session access denied','SecurityError');return original.call(this,k);};""")
   p.goto(base+'mock-focus-review.html'+mode)
   r={'case':'session_access_denied_'+('parent' if mode else 'normal'),'boundary_defined':p.evaluate("typeof YuikaParent!=='undefined'"),'banner_count':p.locator('#parent-check-banner').count(),'pageerrors':errors,'external_requests':network}
   results.append(r);print(json.dumps(r,ensure_ascii=False),flush=True);ctx.close()
  ctx=browser.new_context(timezone_id='UTC');p=ctx.new_page();p.route('**/*',lambda r:r.continue_() if r.request.url.startswith(base) else r.abort());p.goto(base+'mock-focus-review.html?parent-check=1')
  p.evaluate("""()=>{for(const k of ['yuika-social-540-24-v1','yuika-social-540-25-v1'])localStorage.setItem(k,JSON.stringify({schemaVersion:1,events:[{id:'synthetic-delete',at:'2026-11-12T00:00:00Z'}]}));}""")
  before=p.evaluate('Object.fromEntries(Object.entries(localStorage))');p.locator('#parent-check-banner summary').click();p.locator('#parent-since').fill('2026-11-11T00:00');p.locator('#parent-count').click()
  p.evaluate("""()=>{const original=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(this===localStorage&&k==='yuika-social-540-25-v1')throw new DOMException('synthetic second-key failure','QuotaExceededError');return original.call(this,k,v);};}""")
  p.once('dialog',lambda d:d.accept());p.locator('#parent-delete').click();after=p.evaluate('Object.fromEntries(Object.entries(localStorage))')
  r={'case':'second_key_write_failure','changed_keys':[k for k in before if before[k]!=after.get(k)],'first_remaining_events':len(json.loads(after['yuika-social-540-24-v1'])['events']),'second_remaining_events':len(json.loads(after['yuika-social-540-25-v1'])['events']),'status':p.locator('#parent-delete-status').inner_text()};results.append(r);print(json.dumps(r,ensure_ascii=False),flush=True)
  ctx.close();browser.close()
finally:srv.shutdown()
Path('/tmp/yuika-pr24-qa/probe-result.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
