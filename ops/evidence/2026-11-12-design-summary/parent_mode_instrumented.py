"""Parent sandbox and destructive-cleanup UI: synthetic data, intercepted network."""
import json, os, sys, subprocess
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright, expect
ROOT=Path('/workspace/yuika-pr25-review-20261112')
# Every standalone entry must carry exactly the reviewed boundary before app code.
for entry in ROOT.glob('*.html'):
 text=entry.read_text();body=text.split('<!-- YUIKA_PARENT_BEGIN -->')[1].split('<!-- YUIKA_PARENT_END -->')[0]
 assert (ROOT/'scripts/parent/runtime.js').read_text() in body
 assert text.lower().index('<meta charset')<1024
 assert text.index('<!-- YUIKA_PARENT_BEGIN -->')<text.index('<script')
 rest=text.replace(body,'')
 assert 'localStorage.' not in rest,entry.name

class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=srv.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{srv.server_port}/'
CONFIG={'enabled':True,'endpoint':'https://test-notify.example.workers.dev','token':'synthetic-key-123456789012345678901234','recipient':'parent@example.test'}
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  assets={}
  for path in ['react@18/umd/react.production.min.js','react-dom@18/umd/react-dom.production.min.js','@babel/standalone@7/babel.min.js']:
   u='https://unpkg.com/'+path;assets[u]=subprocess.check_output(['curl','--fail','--silent','--show-error','--location','--max-time','30',u])
  for app in ('onin-review.html','kamakura-review.html','heian-review.html','yuika-review-v2.html','mock-focus-review.html','index.html'):
   ctx=browser.new_context(timezone_id="UTC");ctx.add_init_script(path=str(ROOT / "tests/seed_random.js"));p=ctx.new_page();calls=[];errors=[];logs=[]
   p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:logs.append(m.text))
   def route(r):
    if r.request.url.startswith(BASE):r.continue_()
    elif r.request.url in assets:r.fulfill(body=assets[r.request.url],content_type='application/javascript')
    elif '.workers.dev/' in r.request.url:
     print('MOCK_REQUEST',app,'URL',p.url,'ACTIVE',p.evaluate('window.YuikaParent?.active'),'BODY',r.request.post_data,flush=True);calls.append(r.request.url);r.fulfill(content_type='application/json',headers={'Access-Control-Allow-Origin':'*'},body='{"accepted":true,"ready":true,"recipient":"parent@example.test"}')
    else:r.abort()
   p.route('**/*',route)
   p.goto(BASE+app)
   p.evaluate('(c)=>{localStorage.setItem("yuika-mail-config-v1",JSON.stringify(c));localStorage.setItem("unrelated","preserve");}',CONFIG)
   # Store pending work before entry: it must not be read or flushed in mode.
   p.evaluate('''c=>localStorage.setItem('yuika-mail-job-v1:synthetic',JSON.stringify({id:'synthetic',status:'pending',endpoint:c.endpoint,recipient:c.recipient,nextAttempt:0,report:{id:'synthetic'}}))''',CONFIG)
   before=p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')
   if app=='index.html':
    ctx.add_init_script("window.__opened=[];window.open=(u)=>{window.__opened.push(u);return null;};if(location.search.includes('parent-check=1')||sessionStorage.getItem('yuika-parent-check-v1')==='1')sessionStorage.setItem('yuika-parent-check-v1:yuika_parent-email','synthetic@example.test');")
   print('ENTER_PARENT',app,flush=True);p.goto(BASE+app+'?parent-check=1');print('ENTERED_PARENT',app,flush=True)
   expect(p.locator('#parent-check-banner')).to_contain_text('保護者確認モード（記録・通知なし）')
   assert 'parent-check' not in p.url
   assert p.evaluate('YuikaParent.active')
   assert p.evaluate('YuikaParent.storage.getItem("unrelated")') is None
   if app not in ('index.html',):
    # Actual daily-five answering flow; persistence and analysis use the sandbox.
    p.evaluate("prototypeScience?start('daily'):start('daily')")
    for i in range(5):
     q=p.evaluate('prototypeScience?session.questions[session.index]:run.qs[run.index]')
     if app=='yuika-review-v2.html':
      if q['type']=='number':p.locator('#numeric').fill(str(q['answer']))
      else:p.locator('[data-choice]').first.click()
     elif q['type']=='choice':p.locator('[data-choice]').first.click()
     elif q['type']=='structure':
      for j in range(len(q['items'])):p.locator(f'[data-step="{j}"]').click()
      for j,b in enumerate(q['blanks']):p.locator('[data-fill]').nth(j).select_option(label=b['answer'])
     else:p.locator('#response').fill(q['answer'])
     p.locator('#check').click();p.locator('#next').click()
    assert p.evaluate('(prototypeScience?state:data).events.length')==5
    key=p.evaluate('KEY');p.reload()
    assert p.evaluate('(prototypeScience?state:data).events.length')==5
    assert p.evaluate('(k)=>localStorage.getItem(k)',key) is None
   else:
    p.get_by_role('button',name='環境問題・公害',exact=False).click(timeout=60000)
    p.get_by_role('button',name='復習クイズ',exact=False).click()
    for _ in range(10):
     p.get_by_role('button',name='わからない（正解を見る）',exact=False).click()
     p.get_by_role('button',name='次の問題へ',exact=False).or_(p.get_by_role('button',name='結果を見る',exact=False)).click()
    p.get_by_role('button',name='結果を保護者に送る',exact=False).click()
    assert p.evaluate('window.__opened.length')==0
    p.wait_for_function("()=>JSON.parse(YuikaParent.storage.getItem('yuika_sessions')||'[]').length===1")
    p.reload();assert p.evaluate("JSON.parse(YuikaParent.storage.getItem('yuika_sessions')).length")==1
   if app!='mock-focus-review.html':
    p.evaluate('''c=>{YuikaParent.storage.setItem('yuika-mail-config-v1',JSON.stringify(c));YuikaParent.storage.setItem('yuika-mail-job-v1:sandbox-pending',JSON.stringify({id:'sandbox-pending',status:'pending',endpoint:c.endpoint,recipient:c.recipient,nextAttempt:0,report:{id:'sandbox-pending'}}));}''',CONFIG)
    queue_before=p.evaluate("YuikaParent.storage.getItem('yuika-mail-job-v1:sandbox-pending')")
    p.evaluate("YuikaReports.enqueue({id:'sandbox-report'})")
    p.evaluate("window.dispatchEvent(new Event('online'));document.dispatchEvent(new Event('visibilitychange'))")
    p.locator('#yuika-mail-form').evaluate("f=>f.dispatchEvent(new Event('submit',{cancelable:true}))")
    assert p.evaluate("YuikaParent.storage.getItem('yuika-mail-job-v1:sandbox-pending')")==queue_before
    assert p.evaluate("YuikaParent.storage.getItem('yuika-mail-job-v1:sandbox-report')") is None
   assert not calls,calls
   assert any('通知を送信しません' in m for m in logs)
   assert p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')==before
   # A fresh tab gets neither mode nor its records.
   fresh=ctx.new_page();fresh.route('**/*',lambda r:r.continue_() if r.request.url.startswith(BASE) else r.abort())
   fresh.goto(BASE+'mock-focus-review.html');assert not fresh.evaluate('YuikaParent.active');fresh.close()
   # Remove pending synthetic work before leaving so that normal retry is separate.
   p.evaluate("localStorage.removeItem('yuika-mail-job-v1:synthetic')")
   p.locator('#parent-exit').click();p.wait_for_function('()=>window.YuikaParent&&!YuikaParent.active')
   assert p.evaluate("Object.keys(sessionStorage).filter(k=>k.startsWith('yuika-parent-check-v1')).length")==0
   assert p.locator('#parent-check-banner').count()==0
   if app not in ('index.html','mock-focus-review.html'):
    p.evaluate("YuikaReports.enqueue({id:'normal-mock-report'})")
    p.wait_for_function("()=>JSON.parse(localStorage.getItem('yuika-mail-job-v1:normal-mock-report')||'null')?.status==='accepted'")
    assert calls
   assert not errors,errors
   ctx.close();print('PASS parent isolation/reload/exit/notification guards:',app,flush=True)
  # Delete inclusive boundary across current + old records; cancel and stale plan.
  ctx=browser.new_context(timezone_id="UTC");p=ctx.new_page();p.route('https://**/*',lambda r:r.abort());p.goto(BASE+'onin-review.html?parent-check=1')
  p.evaluate('''()=>{
   const old={id:'old',at:'2026-11-10T00:00:00Z'},cut={id:'cut',at:'2026-11-11T00:00:00Z'},newer={id:'new',answeredAt:'2026-11-12T00:00:00Z'};
   for(const k of ['yuika-social-540-27-v1','yuika-prototype-v1:yuika-social-540-27-v1'])localStorage.setItem(k,JSON.stringify({schemaVersion:1,datasetVersion:'synthetic',events:[old,cut,newer]}));
   localStorage.setItem('yuika_sessions',JSON.stringify([{ts:cut.at},{ts:old.at}]));
   localStorage.setItem('yuika_cleared',JSON.stringify({a:{ts:cut.at},b:{ts:old.at}}));
   localStorage.setItem('yuika-science-review-v2',JSON.stringify({events:[],legacy:[{capturedAt:cut.at,raw:'synthetic'}]}));
   localStorage.setItem('yuika-science-v1','{"attempts":10}');
  }''')
  p.locator('#parent-check-banner summary').click();p.locator('#parent-since').fill('2026-11-11T00:00')
  p.locator('#parent-count').click();expect(p.locator('#parent-delete-status')).to_have_text('削除対象：7件')
  snapshot=p.evaluate('JSON.stringify(localStorage)')
  p.once('dialog',lambda d:d.dismiss());p.locator('#parent-delete').click();assert p.evaluate('JSON.stringify(localStorage)')==snapshot
  p.once('dialog',lambda d:d.accept());p.locator('#parent-delete').click();expect(p.locator('#parent-delete-status')).to_contain_text('7件を削除しました')
  assert p.evaluate("JSON.parse(localStorage.getItem('yuika-social-540-27-v1')).events.map(e=>e.id)")==['old']
  assert p.evaluate("localStorage.getItem('yuika-science-v1')")=='{"attempts":10}'
  p.locator('#parent-count').click();expect(p.locator('#parent-delete-status')).to_have_text('削除対象：0件')
  assert p.locator('#parent-delete').is_disabled()
  p.locator('#parent-since').fill('2026-11-01T00:00');p.locator('#parent-count').click()
  p.evaluate("localStorage.setItem('yuika_sessions','[]')")
  p.once('dialog',lambda d:d.accept());p.locator('#parent-delete').click();expect(p.locator('#parent-delete-status')).to_contain_text('記録が更新されました')
  print('PASS inclusive deletion, count, cancel, preserve older/undated, stale confirmation',flush=True)
  p.goto(BASE+'mock-focus-review.html?parent-check=1');p.evaluate("YuikaParent.storage.setItem('close-test','sandbox')");p.close()
  p=ctx.new_page();p.route('https://**/*',lambda r:r.abort());p.goto(BASE+'mock-focus-review.html')
  assert not p.evaluate('YuikaParent.active')
  assert p.evaluate("sessionStorage.getItem('yuika-parent-check-v1:close-test')") is None
  print('PASS tab close clears mode and sandbox for subsequent tab',flush=True)
  ctx.close()
  # Denied initial session reads/writes must remain usable and fail closed.
  for method,entry in [('getItem',''),('getItem','?parent-check=1'),('setItem','?parent-check=1')]:
   ctx=browser.new_context();p=ctx.new_page();errors=[]
   p.on('pageerror',lambda e:errors.append(str(e)))
   p.route('https://**/*',lambda r:r.abort())
   ctx.add_init_script("""(()=>{localStorage.setItem('unrelated','preserve');const method=%s,original=Storage.prototype[method],first=sessionStorage.getItem('__synthetic_once')===null;sessionStorage.setItem('__synthetic_once','seen');if(first)Storage.prototype[method]=function(...args){if(this===sessionStorage)throw new DOMException('synthetic session denial','SecurityError');return original.apply(this,args);};})();""" % json.dumps(method))
   p.goto(BASE+'mock-focus-review.html'+entry)
   expect(p.locator('#parent-notification-status')).to_contain_text('再読込・移動で失われます')
   assert p.evaluate('YuikaParent.active && YuikaParent.suppress()')
   before=p.evaluate('JSON.stringify(localStorage)')
   p.locator('#daily-five').click()
   p.evaluate("YuikaParent.storage.setItem('synthetic-memory','retained')")
   assert p.evaluate("YuikaParent.storage.getItem('synthetic-memory')")=='retained'
   assert p.evaluate('JSON.stringify(localStorage)')==before
   assert p.locator('#parent-count').is_disabled()
   assert not errors,errors
   assert 'parent-check=1' in p.url
   p.reload()
   assert p.evaluate('YuikaParent.active')
   assert p.evaluate('JSON.stringify(localStorage)')==before
   expect(p.locator('#parent-check-banner')).to_be_visible()
   ctx.close()
  print('PASS initial session read/write denial uses isolated temporary mode',flush=True)
  # A second write failure restores earlier raw values; a failed rollback keeps
  # an exportable original and blocks further deletion rather than claiming success.
  for rollback_fails in (False,True):
   ctx=browser.new_context(timezone_id='UTC');p=ctx.new_page();p.route('https://**/*',lambda r:r.abort())
   p.goto(BASE+'mock-focus-review.html?parent-check=1')
   p.evaluate("""()=>{for(const k of ['yuika-social-540-24-v1','yuika-social-540-25-v1'])localStorage.setItem(k,JSON.stringify({events:[{id:'synthetic',at:'2026-11-12T00:00:00Z'}]}));}""")
   before=p.evaluate('Object.fromEntries(Object.entries(localStorage))')
   p.locator('#parent-check-banner summary').click();p.locator('#parent-since').fill('2026-11-11T00:00');p.locator('#parent-count').click()
   p.evaluate("""failRollback=>{const original=Storage.prototype.setItem;let writes=0;Storage.prototype.setItem=function(k,v){if(this===localStorage){writes++;if(writes===2||(failRollback&&writes>2))throw new DOMException('synthetic write failure','QuotaExceededError');}return original.call(this,k,v);};}""",rollback_fails)
   p.once('dialog',lambda d:d.accept());p.locator('#parent-delete').click()
   expect(p.locator('#parent-backup')).to_be_visible()
   if rollback_fails:
    expect(p.locator('#parent-delete-status')).to_contain_text('復元を確認できません')
    p.locator('#parent-count').click();expect(p.locator('#parent-delete-status')).to_contain_text('追加の削除をしない')
   else:
    expect(p.locator('#parent-delete-status')).to_contain_text('元に戻しました')
    assert p.evaluate('Object.fromEntries(Object.entries(localStorage))')==before
   with p.expect_download() as download:p.locator('#parent-backup').click()
   packet=json.loads(Path(download.value.path()).read_text())
   assert packet['format']=='yuika-parent-cleanup-backup-v1'
   assert {c['key']:c['raw'] for c in packet['records']}==before
   assert p.locator('#parent-delete').is_disabled()
   ctx.close()
  print('PASS cleanup rollback and incomplete-recovery original export',flush=True)
  browser.close()

finally:srv.shutdown()
