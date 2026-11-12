"""Deterministic synthetic scheduling probe; product files are read-only."""
import json,os
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path(os.environ.get('YUIKA_QA_ROOT','/workspace/yuika-design-fix-20261112'))
OUT=Path(os.environ.get('YUIKA_QA_OUT','/tmp/yuika-parent-boundary-qa'));OUT.mkdir(exist_ok=True,parents=True)
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  if self.path=='/qa-seed':
   self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers();self.wfile.write(b'<!doctype html><title>Synthetic storage fixture</title>');return
  super().do_GET()
CONFIG={'enabled':True,'endpoint':'https://synthetic.example.workers.dev','token':'synthetic-token-'+('x'*32),'recipient':'synthetic@example.test'}
JOB={'id':'synthetic-pending','status':'pending','endpoint':CONFIG['endpoint'],'recipient':CONFIG['recipient'],'nextAttempt':0,'report':{'id':'synthetic-pending'}}
SEED='''args=>{localStorage.setItem('yuika-mail-config-v1',JSON.stringify(args[0]));localStorage.setItem('yuika-mail-job-v1:synthetic-pending',JSON.stringify(args[1]));localStorage.setItem('unrelated','synthetic-preserve');}'''
FETCH_SPY='''(()=>{window.__fetchEvidence=[];const fetch0=window.fetch;window.fetch=function(input,init){window.__fetchEvidence.push({url:String(input),active:window.YuikaParent?.active,href:location.href,report:JSON.parse(init?.body||'null')});return fetch0.apply(this,arguments);};})();'''
results=[]
with ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT))) as srv:
 Thread(target=srv.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{srv.server_port}'
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  def fresh():
   c=browser.new_context(viewport={'width':768,'height':1024});c.add_init_script(FETCH_SPY);calls=[]
   def route(r):
    if r.request.url.startswith(base):r.continue_()
    elif r.request.url.startswith(CONFIG['endpoint']):
     calls.append({'url':r.request.url,'body':r.request.post_data_json});r.fulfill(status=200,content_type='application/json',headers={'Access-Control-Allow-Origin':'*'},body='{"accepted":true}')
    else:r.abort()
   c.route('**/*',route);return c,calls
  # A real held Web Lock delays the existing mount flush callback until after
  # the original test's storage seeding, then lets it execute in normal mode.
  c,calls=fresh();holder=c.new_page();holder.goto(base+'/qa-seed')
  holder.evaluate("()=>{navigator.locks.request('yuika-mail-send',async()=>{window.__held=true;await new Promise(r=>window.__release=r)});return true}")
  holder.wait_for_function('window.__held===true');p=c.new_page();p.goto(base+'/onin-review.html')
  p.wait_for_function("async()=>{const q=await navigator.locks.query();return q.pending.some(l=>l.name==='yuika-mail-send')}")
  pending=p.evaluate('async()=>await navigator.locks.query()');assert not p.evaluate('YuikaParent.active')
  p.evaluate(SEED,[CONFIG,JOB]);holder.evaluate('window.__release()')
  p.wait_for_function("()=>JSON.parse(localStorage.getItem('yuika-mail-job-v1:synthetic-pending')).status==='accepted'")
  evidence=p.evaluate('window.__fetchEvidence');assert len(calls)==1 and evidence[0]['active'] is False
  p.goto(base+'/onin-review.html?parent-check=1');expect(p.locator('#parent-check-banner')).to_be_visible()
  assert p.evaluate('YuikaParent.active');assert len(calls)==1
  results.append({'case':'normal_mount_flush_after_fixture_seed','pending_lock_count':len(pending['pending']),'requests':calls,'fetch_evidence':evidence,'parent_requests_after_entry':len(p.evaluate('window.__fetchEvidence')),'old_assert_not_calls_would_fail':bool(calls)})
  c.close()
  # No application or notification script runs while preexisting storage is
  # seeded. Parent is active before the first app instruction.
  c,calls=fresh();p=c.new_page();p.goto(base+'/qa-seed');p.evaluate(SEED,[CONFIG,JOB])
  before=p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')
  p.goto(base+'/onin-review.html?parent-check=1');expect(p.locator('#parent-check-banner')).to_be_visible()
  assert p.evaluate('YuikaParent.active');assert p.evaluate("YuikaParent.storage.getItem('yuika-mail-job-v1:synthetic-pending')") is None
  p.evaluate("window.dispatchEvent(new Event('online'));document.dispatchEvent(new Event('visibilitychange'));YuikaReports.enqueue({id:'synthetic-parent-report'})")
  p.locator('#yuika-mail-form').evaluate("f=>f.dispatchEvent(new Event('submit',{cancelable:true}))")
  p.locator('#yuika-mail-retry').evaluate("e=>e.closest('details').open=true");p.locator('#yuika-mail-retry').click();p.reload();expect(p.locator('#parent-check-banner')).to_be_visible()
  assert not calls;assert p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')==before
  assert p.evaluate('window.__fetchEvidence.length')==0
  results.append({'case':'inert_seed_then_parent_entry_reload_triggers','requests':calls,'child_raw_preserved':True,'parent_active':True})
  c.close();browser.close()
(OUT/'boundary-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2));print('PASS: deterministic normal-mode fixture race; inert seed parent boundary preserved')
