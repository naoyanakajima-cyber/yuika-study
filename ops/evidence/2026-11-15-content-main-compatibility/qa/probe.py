from pathlib import Path
import json,os,runpy,subprocess,sys,urllib.request,urllib.error
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright,expect
R=Path('/workspace/yuika-content-main-compat-20261115');O=Path('/tmp/yuika-cycle33-qa');head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert head==sys.argv[1]
Handler=runpy.run_path(str(R/'scripts/cloud/serve.py'))['PreviewHandler']
class Quiet(Handler):
 def log_message(self,*a):pass
writes=[];requests=[];errors=[];routes=[]
INIT='''(()=>{window.qaWrites=[];for(const k of ['setItem','removeItem','clear']){const old=Storage.prototype[k];Storage.prototype[k]=function(...a){qaWrites.push(k);return old.apply(this,a);};}for(const k of ['pushState','replaceState']){const old=history[k];history[k]=function(...a){qaWrites.push(k);return old.apply(this,a);};}for(const [o,k] of [[indexedDB,'open'],[indexedDB,'deleteDatabase'],[caches,'open'],[caches,'delete'],[navigator.serviceWorker,'register']]){if(o&&o[k]){const old=o[k].bind(o);o[k]=function(...a){qaWrites.push(k);return old(...a);};}}})();'''
with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(R))) as srv:
 Thread(target=srv.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{srv.server_port}'
 for path,method,status in [('/content-review.html','GET',200),('/edo-review.html','GET',200),('/unknown.html','GET',404),('/.git/config','GET',404),('/docs/product/fixtures/synthetic-content.json','GET',404),('/api/notify','GET',404),('/api/notify','POST',501),('/content-review.html','HEAD',405),('/edo-review.html','HEAD',405)]:
  req=urllib.request.Request(base+path,method=method)
  try:r=urllib.request.urlopen(req)
  except urllib.error.HTTPError as e:r=e
  assert r.status==status,(path,r.status);assert r.headers['Cache-Control']=='no-store';assert "connect-src 'none'" in r.headers['Content-Security-Policy'];routes.append({'path':path,'method':method,'status':r.status});r.close()
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'));ctx=browser.new_context(viewport={'width':768,'height':1024},accept_downloads=True);ctx.add_init_script(INIT)
  def intercept(r):
   if r.request.url==base+'/content-review.html' and r.request.method=='GET':r.continue_()
   else:requests.append({'method':r.request.method,'url':r.request.url});r.abort()
  ctx.route('**/*',intercept);p=ctx.new_page();p.set_default_timeout(5000);p.on('pageerror',lambda e:errors.append(str(e)));p.on('dialog',lambda d:d.accept());p.goto(base+'/content-review.html')
  assert p.evaluate('localStorage.length===0&&sessionStorage.length===0');p.locator('#sample-text').click();expect(p.locator('#trial-start')).to_be_disabled();p.locator('#confirm-0').click();before=p.evaluate('JSON.stringify({proposal,unsaved})');p.locator('#trial-start').click();expect(p.locator('#editor')).to_be_hidden();expect(p.locator('#trial-title')).to_be_focused();p.locator('#trial-answer').fill('こおり');p.locator('#trial-grade').click();expect(p.locator('#trial-result')).to_contain_text('登録した答えに一致しました');expect(p.locator('#trial-answer')).to_have_value('こおり');p.wait_for_timeout(200);p.screenshot(path=str(O/'trial-graded-768x1024.png'),full_page=True);assert p.evaluate('JSON.stringify({proposal,unsaved})')==before
  p.locator('#trial-exit').click();assert p.evaluate('trial===null');assert p.locator('#trial-panel').inner_text()=='';assert p.evaluate('JSON.stringify({proposal,unsaved})')==before
  with p.expect_download() as dl:p.locator('#export-confirmed').click()
  actual=json.loads(Path(dl.value.path()).read_text());assert actual==json.loads(before)['proposal'];writes=p.evaluate('qaWrites');assert writes==[];assert p.evaluate('localStorage.length===0&&sessionStorage.length===0&&window.name===""');assert requests==[] and errors==[]
  p.locator('#trial-start').click();expect(p.locator('#trial-answer')).to_have_value('');p.locator('#trial-exit').click();ctx.close();browser.close()
 srv.shutdown()
result={'head':head,'routes':routes,'real_ui':'sample→confirm→trial→answer→grade→exit→export→restart-empty','proposal_confirmation_unsaved_unchanged_during_trial':True,'export_json_no_trial_fields':True,'observed_storage_history_idb_cache_sw_writes':writes,'nonallowed_browser_requests':requests,'page_errors':errors,'viewport':[768,1024],'synthetic_only':True};(O/'probe-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result),flush=True)
