import json, os, sys
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path(sys.argv[1]).resolve()
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=srv.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{srv.server_port}/';results=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium')
  for failure,mode in [('read',''),('read','?parent-check=1'),('write','?parent-check=1')]:
   ctx=browser.new_context(viewport={'width':768,'height':1024});p=ctx.new_page();errors=[];network=[]
   p.on('pageerror',lambda e: errors.append(str(e)))
   p.route('**/*',lambda r:r.continue_() if r.request.url.startswith(base) else (network.append(r.request.url),r.abort())[-1])
   method='getItem' if failure=='read' else 'setItem'
   ctx.add_init_script("""localStorage.setItem('qa-child-preserve','synthetic-original');const original=Storage.prototype.METHOD;Storage.prototype.METHOD=function(...args){if(this===sessionStorage)throw new DOMException('synthetic session access denied','SecurityError');return original.apply(this,args);};""".replace('METHOD',method))
   p.goto(base+'mock-focus-review.html'+mode)
   assert p.evaluate("typeof YuikaParent!=='undefined'&&YuikaParent.active&&YuikaParent.suppress()")
   expect(p.locator('#parent-notification-status')).to_contain_text('再読込・移動で失われます')
   assert p.locator('#parent-count').is_disabled()
   p.evaluate("YuikaParent.storage.setItem('qa-child-preserve','synthetic-parent')")
   assert p.evaluate("YuikaParent.storage.getItem('qa-child-preserve')")=='synthetic-parent'
   assert p.evaluate("localStorage.getItem('qa-child-preserve')")=='synthetic-original'
   # Real five-question response flow still works inside temporary storage.
   p.evaluate("start('daily')")
   for _ in range(5):
    p.locator('[data-choice]').first.click();p.locator('#check').click();p.locator('#next').click()
   assert p.evaluate('data.events.length')==5
   assert not errors,errors
   assert not network,network
   r={'case':failure+'_denied_'+('parent' if mode else 'normal'),'result':'pass','answered':5,'child_raw_preserved':True,'pageerrors':0,'external_requests':0}
   results.append(r);print(json.dumps(r),flush=True);ctx.close()
  for failure,mode in [('read',''),('read','?parent-check=1'),('write','?parent-check=1')]:
   ctx=browser.new_context();p=ctx.new_page();p.route('**/*',lambda r:r.continue_() if r.request.url.startswith(base) else r.abort())
   method='getItem' if failure=='read' else 'setItem'
   ctx.add_init_script("""if(!localStorage.getItem('qa-injected-once')){localStorage.setItem('qa-injected-once','1');const original=Storage.prototype.METHOD;Storage.prototype.METHOD=function(...args){if(this===sessionStorage)throw new DOMException('synthetic first-load failure','SecurityError');return original.apply(this,args);};}""".replace('METHOD',method))
   p.goto(base+'mock-focus-review.html'+mode);assert p.evaluate('YuikaParent.active')
   p.evaluate("localStorage.setItem('qa-child-preserve','synthetic-original')")
   p.reload();assert p.evaluate('YuikaParent.active&&YuikaParent.suppress()')
   assert p.locator('#parent-check-banner').count()==1
   p.evaluate("YuikaParent.storage.setItem('qa-child-preserve','synthetic-parent')")
   assert p.evaluate("localStorage.getItem('qa-child-preserve')")=='synthetic-original'
   r={'case':'recovered_reload_'+failure+'_'+('parent' if mode else 'normal'),'result':'pass','parent_retained':True};results.append(r);print(json.dumps(r),flush=True);ctx.close()
  for rollback in ('succeeds','fails','concurrent'):
   ctx=browser.new_context(timezone_id='UTC');p=ctx.new_page();p.route('**/*',lambda r:r.continue_() if r.request.url.startswith(base) else r.abort());p.goto(base+'mock-focus-review.html?parent-check=1')
   p.evaluate("""()=>{for(const k of ['yuika-social-540-24-v1','yuika-social-540-25-v1'])localStorage.setItem(k,JSON.stringify({schemaVersion:1,events:[{id:'synthetic-delete',at:'2026-11-12T00:00:00Z'}]}));}""")
   before=p.evaluate('Object.fromEntries(Object.entries(localStorage))');p.locator('#parent-check-banner summary').click();p.locator('#parent-since').fill('2026-11-11T00:00');p.locator('#parent-count').click()
   p.evaluate("""mode=>{const original=Storage.prototype.setItem;let failed=false;Storage.prototype.setItem=function(k,v){if(this===localStorage){if(k==='yuika-social-540-25-v1'){failed=true;if(mode==='concurrent')original.call(this,'yuika-social-540-24-v1','synthetic concurrent value');throw new DOMException('synthetic second-key failure','QuotaExceededError');}if(failed&&mode==='fails'&&k==='yuika-social-540-24-v1')throw new DOMException('synthetic rollback failure','QuotaExceededError');}return original.call(this,k,v);};}""",rollback)
   p.once('dialog',lambda d:d.accept());p.locator('#parent-delete').click();after=p.evaluate('Object.fromEntries(Object.entries(localStorage))')
   if rollback=='succeeds':
    assert after==before;expect(p.locator('#parent-delete-status')).to_contain_text('元に戻しました')
   else:
    expect(p.locator('#parent-delete-status')).to_contain_text('復元を確認できません')
    if rollback=='concurrent':assert after['yuika-social-540-24-v1']=='synthetic concurrent value'
    p.locator('#parent-count').click();assert p.locator('#parent-delete').is_disabled();expect(p.locator('#parent-delete-status')).to_contain_text('追加の削除をしないでください')
   with p.expect_download() as dl:p.locator('#parent-backup').click()
   saved=json.loads(Path(dl.value.path()).read_text());assert saved['format']=='yuika-parent-cleanup-backup-v1'
   assert {r['key']:r['raw'] for r in saved['records']}==before
   r={'case':'rollback_'+rollback,'result':'pass','backup_original_bytes':True,'false_success':False};results.append(r);print(json.dumps(r),flush=True);ctx.close()
  browser.close()
finally:srv.shutdown()
Path('/tmp/yuika-pr24-qa/candidate/probe-result.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
