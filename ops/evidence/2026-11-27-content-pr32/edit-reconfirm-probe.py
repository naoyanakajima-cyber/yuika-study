"""Independent focused edit/reconfirm/trial probe after confirmed content change."""
import json,os,subprocess,sys,time,runpy
from pathlib import Path
from datetime import datetime,timezone
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path(sys.argv[1]).resolve();OUT=Path(__file__).resolve().parent
Handler=runpy.run_path(str(ROOT/'scripts/cloud/serve.py'))['PreviewHandler']
class Quiet(Handler):
 def log_message(self,*args):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=srv.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{srv.server_port}/'
started=time.monotonic();result={'candidate':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'started_at':datetime.now(timezone.utc).isoformat(),'contexts':[],'requests_blocked':[],'page_errors':[],'content_parent_runtime':False,'parent_scope':'Actual study-page banner entry/exit; content is memory-only and preserves the existing parent session. A query parameter alone is not parent verification.'}
def storage(p):return p.evaluate('({local:Object.fromEntries(Object.entries(localStorage)),session:Object.fromEntries(Object.entries(sessionStorage))})')
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH','/usr/bin/chromium'))
  for parent in (False,True):
   ctx=browser.new_context(viewport={'width':768,'height':1024},is_mobile=True,has_touch=True,timezone_id='Asia/Tokyo')
   ctx.add_init_script(path=ROOT/'tests/seed_random.js')
   def route(r):
    if r.request.url==base+'__fixture__':r.fulfill(body='<!doctype html><title>synthetic fixture</title>',content_type='text/html')
    elif r.request.url.startswith(base) and r.request.method=='GET':r.continue_()
    else:result['requests_blocked'].append({'method':r.request.method,'url':r.request.url});r.abort()
   ctx.route('**/*',route);p=ctx.new_page();p.set_default_timeout(10000)
   p.on('pageerror',lambda e:result['page_errors'].append(str(e)));p.on('dialog',lambda d:d.accept())
   p.goto(base+'__fixture__');p.evaluate("localStorage.setItem('independent-child-sentinel','synthetic-byte-preserve');localStorage.setItem('yuika-science-v2','synthetic-history-preserve')")
   child=p.evaluate('Object.fromEntries(Object.entries(localStorage))')
   if parent:
    p.goto(base+'onin-review.html?parent-check=1');expect(p.locator('#parent-check-banner')).to_be_visible()
    assert p.evaluate('YuikaParent.suppress()') is True
   p.goto(base+'content-review.html');baseline=storage(p)
   assert p.locator('#parent-check-banner').count()==0
   # Observe persistence calls only after actual parent boundary establishment.
   p.evaluate("""()=>{window.qaWrites=[];for(const n of ['setItem','removeItem','clear']){const f=Storage.prototype[n];Storage.prototype[n]=function(...a){qaWrites.push(n);return f.apply(this,a)}}}""")
   for kind,selector,correct,wrong in [('text','#sample-text','こおり','水'),('image','#sample-triangle','3','4')]:
    p.locator(selector).click();expect(p.locator('#trial-start')).to_be_disabled()
    if kind=='image':
     expect(p.locator('#confirm-0')).to_be_disabled();expect(p.locator('#source-preview svg')).to_be_visible()
     p.locator('#transcription').fill('三角形の辺は3本です。');p.locator('#resolution-0').fill('3')
    p.locator('#confirm-0').click();expect(p.locator('#trial-start')).to_be_enabled()
    p.locator('#q-0-hint').fill('合成の確認済み編集を点検');expect(p.locator('#trial-start')).to_be_disabled()
    assert p.evaluate('proposal.questions.every(q=>q.status==="draft"&&q.confirmedRevision===null)')
    p.locator('#confirm-0').click();expect(p.locator('#trial-start')).to_be_enabled()
    saved=p.evaluate('proposal');assert saved['questions'][0]['hint']=='合成の確認済み編集を点検'
    p.locator('#trial-start').click();p.locator('#trial-answer').fill(correct);p.locator('#trial-grade').click()
    expect(p.locator('#trial-result')).to_have_text('登録した答えに一致しました')
    assert p.evaluate('proposal')==saved and storage(p)==baseline and p.evaluate('qaWrites')==[]
    p.locator('#trial-exit').click();assert p.evaluate('trial') is None
    result['contexts'].append({'parent_study_session':parent,'source':kind,'confirmed_edit_invalidates':True,'edited_content_reconfirmed':True,'trial_after_reconfirmation':True,'storage_unchanged':True,'storage_write_calls':0})
   p.reload();expect(p.locator('#work')).to_be_hidden();assert p.evaluate('proposal') is None and storage(p)==baseline
   if parent:
    p.goto(base+'onin-review.html');expect(p.locator('#parent-check-banner')).to_be_visible();p.locator('#parent-exit').click()
    assert p.evaluate('Object.fromEntries(Object.entries(localStorage))')==child
   ctx.close();print('PASS content text/image with '+('actual parent study session preserved' if parent else 'normal context'),flush=True)
  browser.close()
 assert not result['page_errors'] and not [r for r in result['requests_blocked'] if r['method']!='GET']
 result['result']='passed'
finally:
 result.update(finished_at=datetime.now(timezone.utc).isoformat(),seconds=round(time.monotonic()-started,3))
 (OUT/'edit-reconfirm-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');srv.shutdown();srv.server_close()
